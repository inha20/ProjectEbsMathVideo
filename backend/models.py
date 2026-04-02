"""SQLAlchemy models for chat history, playlists, and user profiles."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime, timezone
from database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True)
    student_level = Column(String(32), default="unknown")  # middle / high / suneung
    topics = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True)
    role = Column(String(16))  # user / assistant
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True)
    name = Column(String(256), default="내 재생목록")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PlaylistItem(Base):
    __tablename__ = "playlist_items"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, index=True)
    video_id = Column(String(32))
    title = Column(String(512))
    channel = Column(String(256))
    thumbnail = Column(String(512))
    source = Column(String(16))  # youtube / ebs
    url = Column(String(512))
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
