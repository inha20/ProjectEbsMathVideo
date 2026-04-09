"""
database.py - SQLAlchemy 데이터베이스 설정
세션 관리, 엔진 생성, 의존성 주입
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 전용
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI 의존성 주입용 DB 세션 제너레이터"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """테이블 생성 (앱 시작 시 호출)"""
    from models import User, Video, Progress, Playlist, PlaylistVideo  # noqa: F401
    Base.metadata.create_all(bind=engine)
