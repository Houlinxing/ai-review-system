from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.database import SessionLocal
from app.models import Comment,Summary
from app.schemas import (
    CommentCreate,
    CommentResponse,
    YouTubeImportRequest,
    YouTubeKeywordRequest,
    BilibiliImportRequest,      
    BilibiliKeywordRequest   
)
from app.services.comment_service import (
    create_comment as create_comment_service,
    bulk_create_comments,
    get_comments_by_topic,
    get_topic_stats,
)
from app.services.youtube_service import (
    get_clean_youtube_comments,
    get_comments_by_keyword
)
from app.services.bilibili_service import (        
    get_clean_bilibili_comments,
    get_bilibili_comments_by_keyword
)
from app.services.sentiment_service import analyze_sentiment, analyze_sentiments_batch
from app.services.ai_service import generate_summary, _empty_summary
from app.core.response import success, error
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sentiment_label(score: float) -> str:
    if score >= 0.3:
        return "positive"
    elif score <= -0.3:
        return "negative"
    else:
        return "neutral"


# -------------------------
# create comment（手动新增）
# -------------------------
@router.post("/comments")
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    sentiment_score = analyze_sentiment(comment.content)
    db_comment = create_comment_service(
        db=db,
        platform=comment.platform,
        region=comment.region,
        content=comment.content,
        topic=comment.topic,
        sentiment=sentiment_score
    )
    return success(db_comment)


# -------------------------
# 趋势接口
# -------------------------
@router.get("/trend/{topic}")
def get_trend(topic: str, db: Session = Depends(get_db)):
    from sqlalchemy import func, cast, Date

    rows = (
        db.query(
            cast(Comment.published_at, Date).label("date"),
            func.avg(Comment.sentiment).label("avg_sentiment"),
            func.count(Comment.id).label("count")
        )
        .filter(
            Comment.topic == topic,
            Comment.published_at.isnot(None)
        )
        .group_by(cast(Comment.published_at, Date))
        .order_by(cast(Comment.published_at, Date))
        .all()
    )

    return success([
        {
            "date": str(row.date),
            "avg_sentiment": round(float(row.avg_sentiment), 3),
            "count": row.count
        }
        for row in rows
    ])


# -------------------------
# get comments
# -------------------------
@router.get("/comments", response_model=list[CommentResponse])
def get_comments(
    topic: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return get_comments_by_topic(db, topic)


# -------------------------
# stats
# -------------------------
@router.get("/stats/{topic}")
def get_stats(topic: str, db: Session = Depends(get_db)):
    return success(get_topic_stats(db, topic))


# -------------------------
# summary
# -------------------------
@router.get("/summary/{topic}")
def summary(topic: str, db: Session = Depends(get_db)):
    # 先查有没有缓存的总结
    cached = db.query(Summary).filter(Summary.topic == topic).first()
    if cached:
        logger.info(f"summary cache hit: topic={topic}")
        return success({
            "topic": topic,
            "summary": {
                "verdict": cached.verdict,
                "verdict_reason": cached.verdict_reason,
                "pros": cached.pros,
                "cons": cached.cons,
                "tips": cached.tips,
                "summary": cached.summary_text,
            }
        })
    comments = (
        db.query(Comment)
        .filter(Comment.topic == topic)
        .order_by(Comment.like_count.desc())
        .limit(50)
        .all()
    )

    if not comments:
        return success({"topic": topic, "summary": _empty_summary()})

    comment_texts = [c.content for c in comments]

    try:
        summary_data = generate_summary(comment_texts, topic=topic)

         # 生成后写入缓存
        db_summary = Summary(
            topic=topic,
            verdict=summary_data["verdict"],
            verdict_reason=summary_data["verdict_reason"],
            pros=summary_data["pros"],
            cons=summary_data["cons"],
            tips=summary_data["tips"],
            summary_text=summary_data["summary"],
        )
        db.add(db_summary)
        db.commit()
        logger.info(f"summary generated and cached: topic={topic}")

    except Exception as e:
        logger.error(f"summary generation error: {e}", exc_info=True)
        summary_data = {
            "verdict":        "中立",
            "verdict_reason": "",
            "pros":           [],
            "cons":           [],
            "tips":           [],
            "summary":        "Summary generation failed",
        }

    return success({"topic": topic, "summary": summary_data})


# -------------------------
# youtube 单视频抓取
# -------------------------
@router.post("/crawl/youtube")
def crawl_youtube(
    request: YouTubeImportRequest,
    db: Session = Depends(get_db)
):
    try:
        existing_count = (
            db.query(Comment)
            .filter(Comment.video_id == request.video_id)
            .count()
        )

        if existing_count >= 10:
            logger.info(f"cache hit: video_id={request.video_id} count={existing_count}")
            return success({
                "topic":      request.topic,
                "fetched":    0,
                "imported":   0,
                "skipped":    existing_count,
                "from_cache": True
            })

        comments = get_clean_youtube_comments(
            request.video_id,
            max_results=20
        )
        if not comments:
            return error("No valid comments found")

        texts      = [c["content"] for c in comments]
        sentiments = analyze_sentiments_batch(texts)

        db_objects = [
            Comment(
                platform="youtube",
                video_id=request.video_id,
                comment_id=comment["comment_id"],
                topic=request.topic,
                content=comment["content"],
                like_count=comment["like_count"],
                reply_count=comment["reply_count"],
                published_at=comment["published_at"],
                sentiment=score,
                sentiment_label=sentiment_label(score),
                region=None,
                language=None,
            )
            for comment, score in zip(comments, sentiments)
        ]

        imported = _upsert_comments(db, db_objects)
        logger.info(f"youtube crawl done: topic={request.topic} fetched={len(db_objects)} imported={imported}")

        return success({
            "topic":      request.topic,
            "fetched":    len(db_objects),
            "imported":   imported,
            "skipped":    len(db_objects) - imported,
            "from_cache": False
        })

    except Exception as e:
        logger.error(f"crawl error: {e}", exc_info=True)
        return error(str(e))


# -------------------------
# youtube 关键词搜索抓取
# -------------------------
@router.post("/crawl/youtube/keyword")
def crawl_youtube_by_keyword(
    request: YouTubeKeywordRequest,
    db: Session = Depends(get_db)
):
    try:
        existing_count = (
            db.query(Comment)
            .filter(Comment.topic == request.keyword)
            .count()
        )

        if existing_count >= 10:
            logger.info(f"cache hit: keyword={request.keyword} count={existing_count}")
            return success({
                "keyword":    request.keyword,
                "fetched":    0,
                "imported":   0,
                "skipped":    existing_count,
                "from_cache": True
            })

        result = get_comments_by_keyword(
            keyword=request.keyword,
            max_videos=request.max_videos,
            max_results_per_video=request.max_results_per_video
        )

        comments = result["comments"]
        videos   = result["videos"]

        if not comments:
            return error("No valid comments found")

        texts      = [c["content"] for c in comments]
        sentiments = analyze_sentiments_batch(texts)

        db_objects = [
            Comment(
                platform="youtube",
                video_id=comment["video_id"],
                comment_id=comment["comment_id"],
                topic=request.keyword,
                content=comment["content"],
                like_count=comment["like_count"],
                reply_count=comment["reply_count"],
                published_at=comment["published_at"],
                sentiment=score,
                sentiment_label=sentiment_label(score),
                region=None,
                language=None,
            )
            for comment, score in zip(comments, sentiments)
        ]

        imported = _upsert_comments(db, db_objects)
        logger.info(f"keyword crawl done: keyword={request.keyword} fetched={len(db_objects)} imported={imported}")

        return success({
            "keyword":    request.keyword,
            "videos":     videos,
            "fetched":    len(db_objects),
            "imported":   imported,
            "skipped":    len(db_objects) - imported,
            "from_cache": False
        })

    except Exception as e:
        logger.error(f"keyword crawl error: {e}", exc_info=True)
        return error(str(e))


# -------------------------
# B站 单视频抓取
# -------------------------
@router.post("/crawl/bilibili")
def crawl_bilibili(
    request: BilibiliImportRequest,
    db: Session = Depends(get_db)
):
    try:
        existing_count = (
            db.query(Comment)
            .filter(Comment.video_id == request.bvid)
            .count()
        )

        if existing_count >= 10:
            logger.info(f"cache hit: bvid={request.bvid} count={existing_count}")
            return success({
                "topic":      request.topic,
                "fetched":    0,
                "imported":   0,
                "skipped":    existing_count,
                "from_cache": True
            })

        comments = get_clean_bilibili_comments(
            request.bvid,
            max_results=20
        )
        if not comments:
            return error("No valid comments found")

        texts      = [c["content"] for c in comments]
        sentiments = analyze_sentiments_batch(texts)

        db_objects = [
            Comment(
                platform="bilibili",
                video_id=request.bvid,
                comment_id=comment["comment_id"],
                topic=request.topic,
                content=comment["content"],
                like_count=comment["like_count"],
                reply_count=comment["reply_count"],
                published_at=comment["published_at"],
                sentiment=score,
                sentiment_label=sentiment_label(score),
                region=None,
                language=None,
            )
            for comment, score in zip(comments, sentiments)
        ]

        imported = _upsert_comments(db, db_objects)
        logger.info(f"bilibili crawl done: topic={request.topic} fetched={len(db_objects)} imported={imported}")

        return success({
            "topic":      request.topic,
            "fetched":    len(db_objects),
            "imported":   imported,
            "skipped":    len(db_objects) - imported,
            "from_cache": False
        })

    except Exception as e:
        logger.error(f"bilibili crawl error: {e}", exc_info=True)
        return error(str(e))


# -------------------------
# B站 关键词搜索抓取
# -------------------------
@router.post("/crawl/bilibili/keyword")
def crawl_bilibili_by_keyword(
    request: BilibiliKeywordRequest,
    db: Session = Depends(get_db)
):
    try:
        existing_count = (
            db.query(Comment)
            .filter(Comment.topic == request.keyword)
            .filter(Comment.platform == "bilibili")
            .count()
        )

        if existing_count >= 10:
            logger.info(f"cache hit: keyword={request.keyword} count={existing_count}")
            return success({
                "keyword":    request.keyword,
                "fetched":    0,
                "imported":   0,
                "skipped":    existing_count,
                "from_cache": True
            })

        result = get_bilibili_comments_by_keyword(
            keyword=request.keyword,
            max_videos=request.max_videos,
            max_results_per_video=request.max_results_per_video
        )

        comments = result["comments"]
        videos   = result["videos"]

        if not comments:
            return error("No valid comments found")

        texts      = [c["content"] for c in comments]
        sentiments = analyze_sentiments_batch(texts)

        db_objects = [
            Comment(
                platform="bilibili",
                video_id=comment["video_id"],
                comment_id=comment["comment_id"],
                topic=request.keyword,
                content=comment["content"],
                like_count=comment["like_count"],
                reply_count=comment["reply_count"],
                published_at=comment["published_at"],
                sentiment=score,
                sentiment_label=sentiment_label(score),
                region=None,
                language=None,
            )
            for comment, score in zip(comments, sentiments)
        ]

        imported = _upsert_comments(db, db_objects)
        logger.info(f"bilibili keyword crawl done: keyword={request.keyword} fetched={len(db_objects)} imported={imported}")

        return success({
            "keyword":    request.keyword,
            "videos":     videos,
            "fetched":    len(db_objects),
            "imported":   imported,
            "skipped":    len(db_objects) - imported,
            "from_cache": False
        })

    except Exception as e:
        logger.error(f"bilibili keyword crawl error: {e}", exc_info=True)
        return error(str(e))


# -------------------------
# 去重写入（共用）
# -------------------------
def _upsert_comments(db: Session, db_objects: list[Comment]) -> int:
    if not db_objects:
        return 0

    rows = [{
        c.name: getattr(obj, c.name)
        for c in Comment.__table__.columns if c.name != "id"
    } for obj in db_objects]

    stmt = (insert(Comment).values(rows).on_conflict_do_nothing(
        index_elements=["comment_id"]))

    result = db.execute(stmt)
    db.commit()
    return result.rowcount

@router.get("/topics")
def get_topics(db: Session = Depends(get_db)):
    from sqlalchemy import func

    rows = (
        db.query(
            Comment.topic,
            func.count(Comment.id).label("comment_count"),
            func.max(Comment.created_at).label("last_searched_at"),
            func.array_agg(func.distinct(Comment.platform)).label("platforms")
        )
        .group_by(Comment.topic)
        .order_by(func.max(Comment.created_at).desc())
        .all()
    )

    return success([
        {
            "topic": row.topic,
            "comment_count": row.comment_count,
            "last_searched_at": row.last_searched_at.isoformat() if row.last_searched_at else None,
            "platforms": row.platforms
        }
        for row in rows
    ])

@router.delete("/topics/{topic}")
def delete_topic(topic: str, db: Session = Depends(get_db)):
    try:
        deleted_comments = (
            db.query(Comment)
            .filter(Comment.topic == topic)
            .delete()
        )

        deleted_summary = (
            db.query(Summary)
            .filter(Summary.topic == topic)
            .delete()
        )

        db.commit()

        logger.info(f"topic deleted: topic={topic} comments={deleted_comments} summary={deleted_summary}")

        return success({
            "topic": topic,
            "deleted_comments": deleted_comments,
            "deleted_summary": deleted_summary
        })

    except Exception as e:
        db.rollback()
        logger.error(f"delete topic error: {e}", exc_info=True)
        return error(str(e))

@router.delete("/topics")
def delete_all_topics(db: Session = Depends(get_db)):
    try:
        deleted_comments = db.query(Comment).delete()
        deleted_summary = db.query(Summary).delete()
        db.commit()

        logger.info(f"all topics deleted: comments={deleted_comments} summary={deleted_summary}")

        return success({
            "deleted_comments": deleted_comments,
            "deleted_summary": deleted_summary
        })

    except Exception as e:
        db.rollback()
        logger.error(f"delete all topics error: {e}", exc_info=True)
        return error(str(e))

def _upsert_comments(db: Session, db_objects: list[Comment]) -> int:
    if not db_objects:
        return 0

    rows = [
        {c.name: getattr(obj, c.name)
         for c in Comment.__table__.columns
         if c.name not in ("id", "created_at")}   # ← 排除created_at，让数据库server_default自动填充
        for obj in db_objects
    ]

    stmt = (
        insert(Comment)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["comment_id"])
    )

    result = db.execute(stmt)
    db.commit()
    return result.rowcount