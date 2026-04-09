"""
main.py - FastAPI 애플리케이션 진입점
EBS 수학 영상 학습 추천 시스템
"""

import os
import sys
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from core.exceptions import BaseBusinessException

from config import get_settings
from database import init_db, SessionLocal
from models import User, Video
from services.ebs_service import ebs_service

# ──────────────────────────────────────
# 로깅 설정
# ──────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("EbsMathVideo")

settings = get_settings()


# ──────────────────────────────────────
# 앱 시작/종료 이벤트
# ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 DB 초기화 & 시드 데이터 투입"""
    logger.info("🚀 EBS 수학 영상 학습 시스템을 시작합니다...")

    # DB 테이블 생성
    init_db()
    logger.info("✅ 데이터베이스 초기화 완료")

    # 시드 데이터: 기본 사용자 생성
    db = SessionLocal()
    try:
        if not db.query(User).first():
            import bcrypt
            hashed = bcrypt.hashpw("1234".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            demo_user = User(
                username="demo_student",
                password_hash=hashed,
                grade="중2",
            )
            db.add(demo_user)
            db.commit()
            logger.info("✅ 데모 사용자 생성: demo_student / 1234")

        # EBS 영상 데이터를 DB에도 시드
        if db.query(Video).count() == 0:
            ebs_videos = await ebs_service.search_videos(max_results=999)
            for v in ebs_videos[:100]:  # 상위 100개만 DB에 저장
                video = Video(
                    title=v["title"],
                    url=v["url"],
                    source=v["source"],
                    topic=v["topic"],
                    subtopic=v.get("subtopic", ""),
                    grade=v["grade"],
                    difficulty=v["difficulty"],
                    duration_seconds=v.get("duration_seconds", 0),
                    description=v.get("description", ""),
                    channel_name=v.get("channel_name", "EBSi"),
                )
                db.add(video)
            db.commit()
            logger.info(f"✅ EBS 영상 시드 데이터 투입 완료 (100개)")
    finally:
        db.close()

    yield

    logger.info("👋 서버가 종료됩니다.")


# ──────────────────────────────────────
# FastAPI 앱 생성
# ──────────────────────────────────────
app = FastAPI(
    title="EBS 수학 영상 학습 추천 시스템",
    description=(
        "학생과 AI의 대화를 통해 학생에게 필요한 유튜브 영상 링크와 "
        "EBS 영상 링크를 불러오는 프로그램입니다. "
        "유튜브 재생목록 만들기와 EBS 강좌 추천 기능을 제공합니다."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BaseBusinessException)
async def business_exception_handler(request: Request, exc: BaseBusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

# 정적 파일 & 템플릿
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# ──────────────────────────────────────
# 라우터 등록
# ──────────────────────────────────────
from routers import chat, videos, playlists, users

app.include_router(chat.router)
app.include_router(videos.router)
app.include_router(playlists.router)
app.include_router(users.router)


# ──────────────────────────────────────
# 메인 페이지
# ──────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """메인 페이지 렌더링"""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "ok", "service": "EBS Math Video Recommendation System"}


# ──────────────────────────────────────
# 실행
# ──────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
