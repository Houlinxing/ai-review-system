from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    platform = Column(String)
    region = Column(String)

    content = Column(Text)