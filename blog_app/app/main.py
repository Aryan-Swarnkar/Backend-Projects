from fastapi import FastAPI
from app.routers.users import router
from app.routers.posts import post_router

app = FastAPI()

app.include_router(router)
app.include_router(post_router)

@app.get("/")
def index():
    return {
        "message": "This is working for real."
    }
