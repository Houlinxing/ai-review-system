from sqlalchemy import (
    Column, Integer, String, Text, Float,
    DateTime, Index
)
from sqlalchemy.sql import func
from .database import Base

from datetime import datetime, timezone

class Comment(Base):
    __tablename__ = "comments"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 来源信息
    platform   = Column(String(50),  nullable=False)
    video_id   = Column(String(100), nullable=False)
    comment_id = Column(String(150), nullable=False, unique=True)  # 去重关键字段

    # 评论内容
    topic    = Column(String(200), nullable=False)
    content  = Column(Text,        nullable=False)
    language = Column(String(20),  nullable=True)

    # 地区（YouTube暂时为空，大众点评/Reddit等平台接入后填充）
    region = Column(String(100), nullable=True)

    # 互动数据
    like_count  = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)

    # 情感分析
    sentiment       = Column(Float,      nullable=True)
    sentiment_label = Column(String(20), nullable=True)  # "positive"/"negative"/"neutral"

    # 时间字段
    published_at = Column(DateTime(timezone=True), nullable=True)   # 平台原始发布时间
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc)) # 入库时间

    # 索引
    __table_args__ = (
        Index("ix_comments_topic",     "topic"),
        Index("ix_comments_video_id",  "video_id"),
        Index("ix_comments_platform",  "platform"),
        Index("ix_comments_published", "published_at"),
    )

    def __repr__(self):
        return f"<Comment id={self.id} platform={self.platform} sentiment={self.sentiment}>"