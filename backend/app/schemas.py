from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel
from pydantic import BaseModel


class YouTubeImportRequest(
    BaseModel
):
    video_id: str
    topic: str

class CommentCreate(BaseModel):
    platform: str
    region: str | None = None
    content: str
    topic: str

class CommentResponse(BaseModel):
    id: int
    platform: str
    region: str | None = None
    topic: str
    content: str
    sentiment: float
    created_at: datetime

    class Config:
        from_attributes = True