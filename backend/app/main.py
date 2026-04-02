from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.config import settings

# Router imports
from app.routers import chat, youtube, ebs, playlist

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="수학 영상 추천 시스템 - YouTube & EBS (Refactored)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# Include routers
app.include_router(chat.router)
app.include_router(youtube.router)
app.include_router(ebs.router)
app.include_router(playlist.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "version": settings.VERSION}
