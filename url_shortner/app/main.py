from fastapi import FastAPI

app = FastAPI(title="ShortLink API")


@app.get("/health")
async def health_check():
    return {"status": "ok"}