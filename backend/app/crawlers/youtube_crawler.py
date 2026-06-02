from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

youtube = build(
    "youtube",
    "v3",
    developerKey=os.getenv(
        "YOUTUBE_API_KEY"
    )
)


def get_youtube_comments(
    video_id: str,
    max_results: int = 20
):

    comments = []

    request = (
        youtube.commentThreads()
        .list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results
        )
    )

    response = request.execute()

    for item in response["items"]:

        text = (
            item["snippet"]
            ["topLevelComment"]
            ["snippet"]
            ["textDisplay"]
        )

        comments.append(text)

    return comments