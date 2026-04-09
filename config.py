"""
config.py - 애플리케이션 설정 관리
환경 변수 기반 설정 (pydantic-settings)
"""

import os
import secrets
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """전역 설정 클래스"""

    # === API Keys ===
    OPENAI_API_KEY: str = ""
    YOUTUBE_API_KEY: str = ""

    # === JWT 인증 ===
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24시간

    # === Database ===
    DATABASE_URL: str = "sqlite:///./ebs_math.db"

    # === Server ===
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # === AI Chat ===
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    MAX_CHAT_HISTORY: int = 20

    # === YouTube ===
    YOUTUBE_MAX_RESULTS: int = 10

    # === EBS ===
    EBS_DATA_PATH: str = os.path.join(
        os.path.dirname(__file__), "data", "ebs_math_videos.json"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """싱글턴 설정 인스턴스 반환"""
    return Settings()
