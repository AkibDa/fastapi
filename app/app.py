from fastapi import FastAPI, HTTPException
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

text_posts = {
    1: {"title": "Post 1", "content": "This is the content of post 1."},
    2: {"title": "Post 2", "content": "This is the content of post 2."},
    3: {"title": "Post 3", "content": "This is the content of post 3."},
    4: {"title": "Post 4", "content": "This is the content of post 4."},
    5: {"title": "Post 5", "content": "This is the content of post 5."},
    6: {"title": "Post 6", "content": "This is the content of post 6."},
    7: {"title": "Post 7", "content": "This is the content of post 7."},
    8: {"title": "Post 8", "content": "This is the content of post 8."},
    9: {"title": "Post 9", "content": "This is the content of post 9."},
    10: {"title": "Post 10", "content": "This is the content of post 10."},
}

@app.get("/posts")
def get_post(limit: int = None):
  if limit is not None and 1 > limit > len(text_posts):
    raise HTTPException(status_code=400, detail="Invalid limit value")
  if limit:
    return dict(list(text_posts.items())[:limit])
  return text_posts

@app.get("/posts/{post_id}")
def get_post_by_id(post_id: int) -> PostResponse:
  if post_id not in text_posts:
    raise HTTPException(status_code=404, detail="Post not found")

  return text_posts.get(post_id)

@app.post("/posts")
def create_post(post: PostCreate) -> PostResponse:
  title = post.title
  content = post.content
  post_id = max(text_posts.keys()) + 1

  text_posts[post_id] = {"title": title, "content": content}
  return text_posts[post_id]
