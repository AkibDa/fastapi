from fastapi import FastAPI, HTTPException

app = FastAPI()

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
def get_post_by_id(post_id: int):
  if post_id not in text_posts:
    raise HTTPException(status_code=404, detail="Post not found")

  return text_posts.get(post_id)

