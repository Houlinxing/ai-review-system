from pydantic import BaseModel, Field
from datetime import datetime


# -------------------------
# YouTube 单视频抓取请求
# -------------------------
class YouTubeImportRequest(BaseModel):
    video_id: str
    topic:    str


# -------------------------
# YouTube 关键词搜索请求
# -------------------------
class YouTubeKeywordRequest(BaseModel):
    keyword:               str
    max_videos:            int = Field(default=3,  ge=1, le=10)
    max_results_per_video: int = Field(default=20, ge=1, le=100)


# -------------------------
# B站 单视频抓取请求
# -------------------------
class BilibiliImportRequest(BaseModel):
    bvid:  str   # BV号，例如 BV1xx411c7mD
    topic: str


# -------------------------
# B站 关键词搜索请求
# -------------------------
class BilibiliKeywordRequest(BaseModel):
    keyword:               str
    max_videos:            int = Field(default=3,  ge=1, le=10)
    max_results_per_video: int = Field(default=20, ge=1, le=100)


# -------------------------
# 手动创建评论
# -------------------------
class CommentCreate(BaseModel):
    platform: str
    region:   str | None = None
    content:  str
    topic:    str


# -------------------------
# 评论返回（查询用）
# -------------------------
class CommentResponse(BaseModel):
    id:              int
    platform:        str
    video_id:        str      | None = None
    comment_id:      str      | None = None
    topic:           str
    content:         str
    region:          str      | None = None
    language:        str      | None = None
    like_count:      int             = 0
    reply_count:     int             = 0
    sentiment:       float    | None = None
    sentiment_label: str      | None = None
    published_at:    datetime | None = None
    created_at:      datetime | None = None

    class Config:
        from_attributes = True