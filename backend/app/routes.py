from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Comment
from .schemas import CommentCreate

from app.database import SessionLocal
from app.schemas import CommentCreate, CommentResponse

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

    db_comment = Comment(
        platform=comment.platform,
        region=comment.region,
        content=comment.content,
        topic=comment.topic
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return db_comment

# 获取评论
@router.get("/comments")
def get_comments(db: Session = Depends(get_db)):
    return db.query(Comment).all()