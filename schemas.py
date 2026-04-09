"""
schemas.py - Pydantic 스키마 (API 요청/응답 직렬화)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ──────────────────────────────────────
# User
# ──────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, examples=["student01"])
    password: str = Field(..., min_length=4, max_length=100)
    grade: str = Field(default="중1", examples=["중1", "중2", "고1"])


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    grade: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ──────────────────────────────────────
# Video
# ──────────────────────────────────────

class VideoBase(BaseModel):
    title: str
    url: str
    source: str = "ebs"
    topic: str
    subtopic: str = ""
    grade: str = "중1"
    difficulty: str = "medium"
    description: str = ""


class VideoCreate(VideoBase):
    thumbnail_url: str = ""
    channel_name: str = ""
    duration_seconds: int = 0


class VideoResponse(VideoBase):
    id: int
    thumbnail_url: str = ""
    channel_name: str = ""
    duration_seconds: int = 0
    view_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class VideoSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, examples=["중2 일차함수"])
    grade: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    source: Optional[str] = None  # youtube / ebs / all
    max_results: int = Field(default=10, ge=1, le=50)


# ──────────────────────────────────────
# Progress
# ──────────────────────────────────────

class ProgressCreate(BaseModel):
    video_id: int
    watched_seconds: int = 0
    watch_percentage: float = 0.0
    completed: bool = False
    quiz_score: Optional[float] = None
    last_position: int = 0


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    video_id: int
    watched_seconds: int
    watch_percentage: float
    completed: bool
    quiz_score: Optional[float]
    last_position: int
    watch_count: int
    video: Optional[VideoResponse] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────
# Playlist
# ──────────────────────────────────────

class PlaylistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["중2 함수 정복"])
    description: str = ""


class PlaylistAddVideo(BaseModel):
    video_id: int
    position: Optional[int] = None


class PlaylistResponse(BaseModel):
    id: int
    name: str
    description: str
    is_public: bool
    video_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistDetailResponse(PlaylistResponse):
    videos: List[VideoResponse] = []


# ──────────────────────────────────────
# Chat
# ──────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., examples=["user"])
    content: str = Field(..., examples=["중학교 2학년인데 함수가 너무 어려워요"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[ChatMessage] = []


class RecommendedVideo(BaseModel):
    title: str
    url: str
    source: str
    topic: str
    difficulty: str
    reason: str = ""  # 추천 사유


class ChatResponse(BaseModel):
    reply: str
    recommended_videos: List[RecommendedVideo] = []
    extracted_info: dict = {}  # 추출된 학년/단원/난이도


# ──────────────────────────────────────
# Recommendation
# ──────────────────────────────────────

class RecommendationRequest(BaseModel):
    user_id: Optional[int] = None
    grade: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)


class WeakTopicResponse(BaseModel):
    topic: str
    subtopic: str
    avg_score: float
    watch_count: int
    recommendation: str


# ──────────────────────────────────────
# Dashboard
# ──────────────────────────────────────

class DashboardResponse(BaseModel):
    total_watched: int
    total_completed: int
    avg_quiz_score: float
    total_watch_time_minutes: float
    weak_topics: List[WeakTopicResponse] = []
    recent_videos: List[ProgressResponse] = []
