from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Comment
from app.schemas import (
    CommentCreate,
    CommentResponse,
    YouTubeImportRequest
)

from app.services.sentiment_service import (
    analyze_sentiment,
    analyze_sentiments_batch
)

from app.services.youtube_service import (
    get_clean_youtube_comments
)

from app.services.ai_service import generate_summary
from app.core.response import success, error

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# create comment
# -------------------------
@router.post("/comments")
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):

    sentiment = analyze_sentiment(comment.content)

    db_comment = Comment(
        platform=comment.platform,
        region=comment.region,
        content=comment.content,
        topic=comment.topic,
        sentiment=sentiment
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return success(db_comment)


# -------------------------
# get comments
# -------------------------
@router.get("/comments", response_model=list[CommentResponse])
def get_comments(topic: str | None = Query(default=None), db: Session = Depends(get_db)):

    query = db.query(Comment)

    if topic:
        query = query.filter(Comment.topic == topic)

    return query.all()


# -------------------------
# stats
# -------------------------
@router.get("/stats/{topic}")
def get_stats(topic: str, db: Session = Depends(get_db)):

    total = db.query(Comment).filter(Comment.topic == topic).count()

    avg = db.query(func.avg(Comment.sentiment)).filter(
        Comment.topic == topic
    ).scalar()

    return success({
        "topic": topic,
        "total_comments": total,
        "average_sentiment": float(avg or 0)
    })


# -------------------------
# summary
# -------------------------
@router.get("/summary/{topic}")
def summary(topic: str, db: Session = Depends(get_db)):

    comments = db.query(Comment).filter(Comment.topic == topic).all()

    if not comments:
        return success({
            "topic": topic,
            "summary": "No comments found"
        })

    summary_text = generate_summary([c.content for c in comments])

    return success({
        "topic": topic,
        "summary": summary_text
    })


# -------------------------
# youtube crawler
# -------------------------
@router.post("/crawl/youtube")
def crawl_youtube(request: YouTubeImportRequest, db: Session = Depends(get_db)):

    try:
        comments = get_clean_youtube_comments(
            request.video_id,
            max_results=20
        )

        if not comments:
            return error("No valid comments found")

        sentiments = analyze_sentiments_batch(
            comments
        )

        # 存清洗后的评论
        db_objects = [
            Comment(
                platform="youtube",
                region="unknown",
                content=text,
                topic=request.topic,
                sentiment=sentiment
            )
            for text, sentiment in zip(
                comments,
                sentiments
            )
            ]

        db.bulk_save_objects(db_objects)
        db.commit()

        return success({
            "topic": request.topic,
            "imported": len(db_objects)
        })

    except Exception as e:
        print("crawl error:", e)
        return error(str(e))