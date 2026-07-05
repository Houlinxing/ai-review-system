from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Comment


def create_comment(
    db: Session,
    platform: str,
    region: str,
    content: str,
    topic: str,
    sentiment: float
):

    comment = Comment(
        platform=platform,
        region=region,
        content=content,
        topic=topic,
        sentiment=sentiment
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def bulk_create_comments(
    db: Session,
    comments: list[Comment]
):

    db.bulk_save_objects(comments)
    db.commit()

    return len(comments)


def get_comments_by_topic(
    db: Session,
    topic: str | None = None
):

    query = db.query(Comment)

    if topic:
        query = query.filter(
            Comment.topic == topic
        )

    return query.all()


def get_topic_stats(
    db: Session,
    topic: str
):

    total_comments = (
        db.query(Comment)
        .filter(Comment.topic == topic)
        .count()
    )

    average_sentiment = (
        db.query(
            func.avg(Comment.sentiment)
        )
        .filter(Comment.topic == topic)
        .scalar()
    )

    return {
        "topic": topic,
        "total_comments": total_comments,
        "average_sentiment": (
            average_sentiment or 0
        )
    }


def get_comments_for_summary(
    db: Session,
    topic: str
):

    return (
        db.query(Comment)
        .filter(Comment.topic == topic)
        .all()
    )