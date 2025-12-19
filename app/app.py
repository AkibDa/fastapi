from fastapi import FastAPI, File, UploadFile, Depends, Form
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile
from app.users import current_active_user, fastapi_users, auth_backend
from app.schemas import UserRead, UserCreate, UserUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(
  fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
  fastapi_users.get_register_router(UserRead,UserCreate), prefix="/auth", tags=["auth"]
)
app.include_router(
  fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"]
)
app.include_router(
  fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
  fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"]
)

@app.post("/upload")
async def upload(file: UploadFile = File(...), caption: str = Form(""), session: AsyncSession = Depends(get_async_session)):
  temp_file_path = None

  try:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
      shutil.copyfileobj(file.file, temp_file)
      temp_file_path = temp_file.name
      upload_result = imagekit.files.upload(
          file=open(temp_file_path, "rb"),
          file_name=file.filename,
          use_unique_file_name=True,
          tags=["backend-upload"]
      )
    # The SDK usually returns a successful object or raises an error
    if not upload_result or not upload_result.url:
      raise Exception("Image upload failed: No URL returned")

    post = Post(
        caption=caption,
        image_url=upload_result.url,
        file_type="video" if file.content_type.startswith("video/") else "image",
        file_name=upload_result.name,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
  except Exception as e:
    raise e
  finally:
    if temp_file_path and os.path.exists(temp_file_path):
      os.unlink(temp_file_path)
    file.file.close()

@app.get("/feed")
async def feed(session: AsyncSession = Depends(get_async_session) ):
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
          {
              "id": str(post.id),
              "caption": post.caption,
              "image_url": post.image_url,
              "file_type": post.file_type,
              "file_name": post.file_name,
              "created_at": post.created_at.isoformat(),
          }
        )
    return {"posts": posts_data}

@app.delete("/post/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
      post_uuid = uuid.UUID(post_id)

      result = await session.execute(select(Post).where(Post.id == post_uuid))
      post = result.scalars().first()

      if not post:
          return {"error": "Post not found"}

      await session.delete(post)
      await session.commit()

      return {"message": "Post deleted successfully"}

    except ValueError:
      return {"error": "Invalid post ID format"}

    except Exception as e:
      return {"error": str(e)}