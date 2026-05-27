from sqlalchemy import Column, Integer, String, Text
from .database import Base
from sqlalchemy import Float, DateTime
from datetime import datetime



class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String)
    region = Column(String)
    content = Column(Text)
    sentiment = Column(Float, default=0)
    topic = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)