from app.crawlers.youtube_crawler import (
    get_youtube_comments,
    search_youtube_videos
)
from app.utils.text_cleaner import clean_text

from app.core.logger import setup_logger
logger = setup_logger(__name__)


def get_clean_youtube_comments(
    video_id: str,
    max_results: int = 20
) -> list[dict]:
    raw_comments = get_youtube_comments(
        video_id,
        max_results=max_results
    )

    clean_comments = []
    skipped = 0  # ← 记录过滤数量

    for comment in raw_comments:
        cleaned_content = clean_text(comment["content"])

        if len(cleaned_content.strip()) < 5:
            skipped += 1  # ← 计数
            continue

        clean_comments.append({
            "comment_id":   comment["comment_id"],
            "content":      cleaned_content,
            "like_count":   comment["like_count"],
            "reply_count":  comment["reply_count"],
            "published_at": comment["published_at"],
        })

    # ← 加这一行
    logger.info(f"video={video_id} raw={len(raw_comments)} clean={len(clean_comments)} skipped={skipped}")

    return clean_comments

def get_comments_by_keyword(
    keyword: str,
    max_videos: int = 3,
    max_results_per_video: int = 20
) -> dict:
    """
    关键词搜索视频 → 聚合多个视频的评论
    返回评论列表 + 视频来源信息
    """
    # 第一步：搜索相关视频
    videos = search_youtube_videos(keyword, max_videos=max_videos)

    if not videos:
        return {"comments": [], "videos": []}

    all_comments = []
    successful_videos = []

    # 第二步：逐个视频抓取评论
    for video in videos:
        video_id = video["video_id"]
        try:
            comments = get_clean_youtube_comments(
                video_id,
                max_results=max_results_per_video
            )

            # 每条评论带上来源 video_id，方便溯源
            for comment in comments:
                comment["video_id"] = video_id

            all_comments.extend(comments)
            successful_videos.append(video)

            logger.info(f"视频 {video_id} 抓取 {len(comments)} 条评论")

        except Exception as e:
            # 单个视频失败不影响其他视频
            logger.warning(f"视频 {video_id} 抓取失败: {e}")
            continue

    return {
        "comments": all_comments,
        "videos":   successful_videos,   # 成功抓取的视频列表，返回给前端展示
    }