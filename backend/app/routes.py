from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Comment
from .schemas import CommentCreate
from fastapi import Query
from app.schemas import CommentResponse
from app.ai import analyze_sentiment
from sqlalchemy import func

router = APIRouter()

# 获取数据库连接
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建评论
@router.post("/comments")
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    sentiment_score = analyze_sentiment(comment.content)

    db_comment = Comment(
        platform=comment.platform,
        region=comment.region,
        content=comment.content,
        topic=comment.topic,
        sentiment=sentiment_score
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return db_comment

# 获取评论
@router.get("/comments", response_model=list[CommentResponse])
def get_comments(
    topic: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Comment)
    if topic:
        query = query.filter(Comment.topic == topic)

    return query.all()

@router.get("/stats/{topic}")
def get_topic_stats(topic: str, db: Session = Depends(get_db)):

    total_comments = (
        db.query(Comment)
        .filter(Comment.topic == topic)
        .count()
    )

    average_sentiment = (
        db.query(func.avg(Comment.sentiment))
        .filter(Comment.topic == topic)
        .scalar()
    )
    
    if average_sentiment is None:
        average_sentiment = 0

    return {
        "topic": topic,
        "total_comments": total_comments,
        "average_sentiment": average_sentiment
    }