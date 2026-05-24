from fastapi import FastAPI

from .database import engine, Base
from .routes import router

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)

@app.get("/")
def root():
    return {"message": "AI Review System Running"}