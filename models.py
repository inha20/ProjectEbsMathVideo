"""
models.py - SQLAlchemy ORM 모델
User, Video, Progress, Playlist, PlaylistVideo
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database import Base
import enum


# ──────────────────────────────────────
# Enums
# ──────────────────────────────────────

class VideoSource(str, enum.Enum):
    YOUTUBE = "youtube"
    EBS = "ebs"


class Difficulty(str, enum.Enum):
    EASY = "easy"         # 기초
    MEDIUM = "medium"     # 보통
    HARD = "hard"         # 심화


class GradeLevel(str, enum.Enum):
    MIDDLE_1 = "중1"
    MIDDLE_2 = "중2"
    MIDDLE_3 = "중3"
    HIGH_1 = "고1"
    HIGH_2 = "고2"
    HIGH_3 = "고3"


# ──────────────────────────────────────
# User 모델
# ──────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    grade = Column(String(10), default="중1")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress_records = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    playlists = relationship("Playlist", back_populates="user", cascade="all, delete-orphan")


# ──────────────────────────────────────
# Video 모델
# ──────────────────────────────────────

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), default="")
    source = Column(String(20), default=VideoSource.EBS.value)  # youtube / ebs
    topic = Column(String(100), nullable=False)          # 대단원 (예: 함수)
    subtopic = Column(String(100), default="")           # 소단원 (예: 일차함수)
    grade = Column(String(10), default="중1")             # 학년
    difficulty = Column(String(20), default=Difficulty.MEDIUM.value)
    duration_seconds = Column(Integer, default=0)
    description = Column(Text, default="")
    channel_name = Column(String(100), default="")
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    progress_records = relationship("Progress", back_populates="video", cascade="all, delete-orphan")
    playlist_items = relationship("PlaylistVideo", back_populates="video", cascade="all, delete-orphan")


# ──────────────────────────────────────
# Progress (학습 이력) 모델
# ──────────────────────────────────────

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)
    watched_seconds = Column(Integer, default=0)        # 시청 시간(초)
    watch_percentage = Column(Float, default=0.0)       # 시청률 (0~100)
    completed = Column(Boolean, default=False)           # 완료 여부
    quiz_score = Column(Float, nullable=True)            # 퀴즈 점수 (0~100)
    last_position = Column(Integer, default=0)           # 이어보기 위치(초)
    watch_count = Column(Integer, default=1)             # 시청 횟수
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress_records")
    video = relationship("Video", back_populates="progress_records")


# ──────────────────────────────────────
# Playlist 모델
# ──────────────────────────────────────

class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="playlists")
    playlist_videos = relationship("PlaylistVideo", back_populates="playlist",
                                   cascade="all, delete-orphan", order_by="PlaylistVideo.position")


# ──────────────────────────────────────
# PlaylistVideo (다대다 중간 테이블)
# ──────────────────────────────────────

class PlaylistVideo(Base):
    __tablename__ = "playlist_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)
    position = Column(Integer, default=0)  # 재생 순서
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    playlist = relationship("Playlist", back_populates="playlist_videos")
    video = relationship("Video", back_populates="playlist_items")
