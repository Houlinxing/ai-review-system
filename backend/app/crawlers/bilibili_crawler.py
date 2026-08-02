import requests
from datetime import datetime, timezone
from app.core.logger import setup_logger
import hashlib
from urllib.parse import urlencode
from functools import lru_cache
import time

logger = setup_logger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Origin": "https://www.bilibili.com",
}

# WBI签名用的固定混淆表（B站公开算法，不涉及账号）
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]

_wbi_cache = {"keys": None, "expire": 0}

def get_mixin_key(orig: str) -> str:
    return ''.join([orig[i] for i in MIXIN_KEY_ENC_TAB])[:32]


def get_wbi_keys() -> tuple[str, str]:
    if _wbi_cache["keys"] and time.time() < _wbi_cache["expire"]:
        return _wbi_cache["keys"]

    resp = requests.get(
        "https://api.bilibili.com/x/web-interface/nav",
        headers=HEADERS,
        timeout=10
    )
    data = resp.json()
    img_url = data["data"]["wbi_img"]["img_url"]
    sub_url = data["data"]["wbi_img"]["sub_url"]

    img_key = img_url.rsplit('/', 1)[-1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[-1].split('.')[0]

    _wbi_cache["keys"] = (img_key, sub_key)
    _wbi_cache["expire"] = time.time() + 3600  # 缓存1小时

    return _wbi_cache["keys"]


def enc_wbi(params: dict) -> dict:
    """给参数加上WBI签名"""
    img_key, sub_key = get_wbi_keys()
    mixin_key = get_mixin_key(img_key + sub_key)

    params = dict(params)
    params['wts'] = int(time.time())
    params = dict(sorted(params.items()))  # 按key排序

    query = urlencode(params)
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = w_rid

    return params

def bvid_to_aid(bvid: str) -> int | None:
    """
    BV号 → AV号（评论接口需要AV号）
    """
    try:
        url = "https://api.bilibili.com/x/web-interface/view"
        resp = requests.get(url, params={"bvid": bvid}, headers=HEADERS, timeout=10)
        data = resp.json()

        if data.get("code") != 0:
            logger.warning(f"bvid转换失败: bvid={bvid} code={data.get('code')} msg={data.get('message')}")
            return None

        aid = data["data"]["aid"]
        logger.info(f"bvid转换成功: {bvid} → av{aid}")
        return aid

    except Exception as e:
        logger.error(f"bvid转换异常: {e}", exc_info=True)
        return None


def get_bilibili_comments(
    bvid: str,
    max_results: int = 20
) -> list[dict]:
    """
    抓取B站视频评论
    输入：BV号
    输出：评论列表（和 youtube_crawler 保持相同的字段结构）
    """
    # 第一步：BV号转AV号
    aid = bvid_to_aid(bvid)
    if not aid:
        return []

    comments = []
    page = 1
    page_size = min(max_results, 20)  # B站单页最多20条

    while len(comments) < max_results:
        try:
            url = "https://api.bilibili.com/x/v2/reply/main"
            params = {
                "type": 1,
                "oid":  aid,
                "mode": 3,        # 按热度排序
                "ps":   page_size,
                "pn":   page,
            }

            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            data = resp.json()

            if data.get("code") != 0:
                logger.warning(f"评论接口异常: oid={aid} code={data.get('code')}")
                break

            replies = data.get("data", {}).get("replies", [])
            if not replies:
                logger.info(f"没有更多评论: oid={aid} page={page}")
                break

            for item in replies:
                try:
                    # 时间戳转 datetime
                    ctime = item.get("ctime", 0)
                    published_at = datetime.fromtimestamp(ctime, tz=timezone.utc) if ctime else None

                    comments.append({
                        "comment_id":  f"bili_{item['rpid']}",  # 加前缀避免和YouTube ID冲突
                        "content":     item["content"]["message"],
                        "like_count":  item.get("like", 0),
                        "reply_count": item.get("rcount", 0),
                        "published_at": published_at,
                    })

                except Exception as e:
                    logger.warning(f"单条评论解析失败: {e}")
                    continue

            logger.info(f"B站评论抓取: bvid={bvid} page={page} 本页={len(replies)} 累计={len(comments)}")

            # 判断是否还有下一页
            cursor = data.get("data", {}).get("cursor", {})
            if cursor.get("is_end"):
                break

            page += 1

        except Exception as e:
            logger.error(f"B站评论请求异常: oid={aid} page={page} {e}", exc_info=True)
            break

    return comments[:max_results]


def search_bilibili_videos(keyword: str, max_videos: int = 3) -> list[dict]:
    try:
        raw_params = {
            "search_type": "video",
            "keyword":     keyword,
            "order":       "scores",
            "ps":          max_videos,
            "pn":          1,
        }

        # 加WBI签名
        signed_params = enc_wbi(raw_params)

        url = "https://api.bilibili.com/x/web-interface/wbi/search/type"  # 注意路径加了 /wbi/
        resp = requests.get(url, params=signed_params, headers=HEADERS, timeout=10)

        if resp.status_code != 200:
            logger.warning(f"B站搜索HTTP异常: status={resp.status_code}")
            return []

        try:
            data = resp.json()
        except ValueError:
            logger.warning(f"B站搜索返回非JSON: text={resp.text[:200]}")
            return []

        if data.get("code") != 0:
            logger.warning(f"B站搜索失败: code={data.get('code')} msg={data.get('message')}")
            return []

        results = data.get("data", {}).get("result", [])
        videos = [
            {
                "video_id": item["bvid"],
                "title": item.get("title", "").replace('<em class="keyword">', "").replace("</em>", ""),
                "channel": item.get("author", ""),
            }
            for item in results[:max_videos] if item.get("bvid")
        ]

        logger.info(f"B站搜索: keyword={keyword} 找到{len(videos)}个视频")
        return videos

    except Exception as e:
        logger.error(f"B站搜索异常: {e}", exc_info=True)
        return []