from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

youtube = build(
    "youtube",
    "v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)


def search_youtube_videos(
    keyword: str,
    max_videos: int = 3
) -> list[dict]:
    """
    关键词搜索视频，返回 video_id 列表
    """
    request = youtube.search().list(
        part="snippet",
        q=keyword,
        type="video",                    # 只搜视频，排除频道/播放列表
        maxResults=max_videos,
        relevanceLanguage="zh-Hans",     # 优先返回中文相关视频
        order="relevance"                # 按相关度排序
    )

    response = request.execute()

    videos = []
    for item in response.get("items", []):
        videos.append({
            "video_id": item["id"]["videoId"],
            "title":    item["snippet"]["title"],
            "channel":  item["snippet"]["channelTitle"],
        })

    return videos


def get_youtube_comments(
    video_id: str,
    max_results: int = 20
) -> list[dict]:

    comments = []

    request = (
        youtube.commentThreads()
        .list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            order="relevance"  # 按相关度排序，热门评论优先
        )
    )

    response = request.execute()

    for item in response["items"]:
        snippet = item["snippet"]["topLevelComment"]["snippet"]

        # 解析 published_at
        raw_time = snippet.get("publishedAt")
        published_at = (
            datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            if raw_time else None
        )

        comments.append({
            "comment_id":  item["snippet"]["topLevelComment"]["id"],  # 评论唯一ID
            "content":     snippet.get("textDisplay", ""),
            "like_count":  snippet.get("likeCount", 0),
            "reply_count": item["snippet"].get("totalReplyCount", 0),
            "published_at": published_at,
        })

    return comments