from app.crawlers.bilibili_crawler import (
    get_bilibili_comments,
    search_bilibili_videos
)
from app.utils.text_cleaner import clean_text
from app.core.logger import setup_logger

logger = setup_logger(__name__)


def get_clean_bilibili_comments(
    bvid: str,
    max_results: int = 20
) -> list[dict]:
    """
    抓取单个B站视频的评论并清洗
    """
    raw_comments = get_bilibili_comments(
        bvid,
        max_results=max_results
    )

    clean_comments = []
    skipped = 0

    for comment in raw_comments:
        cleaned_content = clean_text(comment["content"])

        if len(cleaned_content.strip()) < 5:
            skipped += 1
            continue

        clean_comments.append({
            "comment_id":   comment["comment_id"],
            "content":      cleaned_content,
            "like_count":   comment["like_count"],
            "reply_count":  comment["reply_count"],
            "published_at": comment["published_at"],
        })

    logger.info(f"bvid={bvid} raw={len(raw_comments)} clean={len(clean_comments)} skipped={skipped}")
    return clean_comments


def get_bilibili_comments_by_keyword(
    keyword: str,
    max_videos: int = 3,
    max_results_per_video: int = 20
) -> dict:
    """
    关键词搜索B站视频 → 聚合多个视频的评论
    """
    # 第一步：搜索相关视频
    videos = search_bilibili_videos(keyword, max_videos=max_videos)

    if not videos:
        logger.warning(f"B站搜索无结果: keyword={keyword}")
        return {"comments": [], "videos": []}

    all_comments = []
    successful_videos = []

    # 第二步：逐个视频抓取评论
    for video in videos:
        bvid = video["video_id"]
        try:
            comments = get_clean_bilibili_comments(
                bvid,
                max_results=max_results_per_video
            )

            for comment in comments:
                comment["video_id"] = bvid

            all_comments.extend(comments)
            successful_videos.append(video)

            logger.info(f"B站视频 {bvid} 抓取 {len(comments)} 条评论")

        except Exception as e:
            logger.warning(f"B站视频 {bvid} 抓取失败: {e}")
            continue

    logger.info(f"B站关键词抓取完成: keyword={keyword} 视频={len(successful_videos)} 评论={len(all_comments)}")

    return {
        "comments": all_comments,
        "videos":   successful_videos,
    }