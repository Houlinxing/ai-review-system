from pydantic import BaseModel

class CommentCreate(BaseModel):
    platform: str
    region: str
    content: str