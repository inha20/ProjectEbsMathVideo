"""
ProjectEbsMathVideo - FastAPI Backend
AI-powered math video recommendation system with YouTube and EBS integration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from database import init_db
from chat_engine import chat_engine
from youtube_service import youtube_service
from ebs_service import ebs_service

# ──────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────
app = FastAPI(
    title="ProjectEbsMathVideo API",
    description="수학 영상 추천 시스템 - YouTube & EBS",
    version="1.0.0",
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


# ──────────────────────────────────────────────
# Pydantic models
# ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class SearchRequest(BaseModel):
    query: str
    max_results: int = 6


class EBSRecommendRequest(BaseModel):
    level: Optional[str] = None
    topics: Optional[list[str]] = None
    difficulty: Optional[str] = None
    limit: int = 6


class PlaylistAddRequest(BaseModel):
    session_id: str
    video_id: str
    title: str
    channel: str
    thumbnail: str
    source: str  # youtube / ebs
    url: str


# ──────────────────────────────────────────────
# In-memory playlist storage (simple approach)
# ──────────────────────────────────────────────
playlists: dict[str, list[dict]] = {}


# ──────────────────────────────────────────────
# Chat endpoints
# ──────────────────────────────────────────────
@app.post("/api/chat/start")
def chat_start():
    """Start a new chat session and get greeting message."""
    session_id = chat_engine.create_session()
    result = chat_engine.get_greeting(session_id)
    return result


@app.post("/api/chat/message")
def chat_message(req: ChatRequest):
    """Send a message in an existing chat session."""
    if not req.session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    result = chat_engine.chat(req.session_id, req.message)

    # If recommendations are generated, also fetch videos and EBS courses
    if result.get("recommendations"):
        rec = result["recommendations"]
        result["ebs_courses"] = ebs_service.recommend(
            level=rec.get("level"),
            topics=rec.get("topics"),
            difficulty=rec.get("difficulty"),
        )

    return result


# ──────────────────────────────────────────────
# YouTube endpoints
# ──────────────────────────────────────────────
@app.post("/api/youtube/search")
async def youtube_search(req: SearchRequest):
    """Search YouTube for math videos."""
    results = await youtube_service.search(req.query, req.max_results)
    return {
        "query": req.query,
        "results": results,
        "search_url": youtube_service.get_youtube_search_url(req.query),
    }


# ──────────────────────────────────────────────
# EBS endpoints
# ──────────────────────────────────────────────
@app.post("/api/ebs/recommend")
def ebs_recommend(req: EBSRecommendRequest):
    """Get EBS course recommendations."""
    courses = ebs_service.recommend(
        level=req.level,
        topics=req.topics,
        difficulty=req.difficulty,
        limit=req.limit,
    )
    return {"courses": courses}


@app.get("/api/ebs/courses")
def ebs_all_courses(level: Optional[str] = None):
    """Get all EBS courses, optionally filtered by level."""
    return {"courses": ebs_service.get_all(level)}


@app.get("/api/ebs/search")
def ebs_search(q: str):
    """Search EBS courses by keyword."""
    return {"courses": ebs_service.search(q)}


# ──────────────────────────────────────────────
# Playlist endpoints
# ──────────────────────────────────────────────
@app.post("/api/playlist/add")
def playlist_add(req: PlaylistAddRequest):
    """Add a video to the session playlist."""
    if req.session_id not in playlists:
        playlists[req.session_id] = []

    # Check if already exists
    for item in playlists[req.session_id]:
        if item["video_id"] == req.video_id:
            return {"message": "이미 재생목록에 있습니다.", "playlist": playlists[req.session_id]}

    playlists[req.session_id].append({
        "video_id": req.video_id,
        "title": req.title,
        "channel": req.channel,
        "thumbnail": req.thumbnail,
        "source": req.source,
        "url": req.url,
    })

    return {"message": "추가되었습니다!", "playlist": playlists[req.session_id]}


@app.get("/api/playlist/{session_id}")
def playlist_get(session_id: str):
    """Get current playlist for a session."""
    return {"playlist": playlists.get(session_id, [])}


@app.delete("/api/playlist/{session_id}/{video_id}")
def playlist_remove(session_id: str, video_id: str):
    """Remove a video from the playlist."""
    if session_id in playlists:
        playlists[session_id] = [
            v for v in playlists[session_id] if v["video_id"] != video_id
        ]
    return {"message": "삭제되었습니다.", "playlist": playlists.get(session_id, [])}


@app.delete("/api/playlist/{session_id}")
def playlist_clear(session_id: str):
    """Clear the entire playlist."""
    playlists[session_id] = []
    return {"message": "재생목록을 비웠습니다.", "playlist": []}


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
