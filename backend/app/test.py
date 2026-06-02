from dotenv import load_dotenv
from googleapiclient.discovery import build
import os

load_dotenv()

youtube = build(
    "youtube",
    "v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)

request = youtube.videos().list(
    part="snippet",
    id="dQw4w9WgXcQ"
)

response = request.execute()

print(response)