"""
routers/videos.py - 영상 API 라우터
영상 검색, 조회, 추천, 학습 진도 관리
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from schemas import (
    VideoResponse, VideoSearchRequest, ProgressCreate, ProgressResponse,
    RecommendationRequest, DashboardResponse, WeakTopicResponse,
)
from services.ebs_service import ebs_service
from services.youtube_service import youtube_service
from services.recommendation_service import recommendation_service
from models import Video, Progress, User
from database import get_db

router = APIRouter(prefix="/api/videos", tags=["영상"])


@router.post("/search")
async def search_videos(request: VideoSearchRequest, db: Session = Depends(get_db)):
    """
    통합 영상 검색 (EBS + YouTube)
    """
    all_results = []

    source = request.source or "all"

    # EBS 검색
    if source in ("all", "ebs"):
        ebs_results = await ebs_service.search_videos(
            query=request.query,
            grade=request.grade,
            topic=request.topic,
            difficulty=request.difficulty,
            max_results=request.max_results,
        )
        all_results.extend(ebs_results)

    # YouTube 검색
    if source in ("all", "youtube"):
        yt_results = await youtube_service.search_videos(
            query=request.query,
            grade=request.grade,
            topic=request.topic,
            max_results=request.max_results,
        )
        all_results.extend(yt_results)

    return {
        "total": len(all_results),
        "results": all_results[:request.max_results],
    }


@router.get("/topics")
async def get_topics(grade: Optional[str] = Query(None, examples=["중2"])):
    """학년별 단원 목록 조회"""
    topics = await ebs_service.get_all_topics(grade=grade)
    return {"topics": topics}


@router.post("/recommendations")
async def get_recommendations(
    request: RecommendationRequest, db: Session = Depends(get_db)
):
    """
    맞춤 추천 결과 반환 (이어보기 + 취약단원 + 규칙기반)
    """
    result = await recommendation_service.get_recommendations(
        db=db,
        user_id=request.user_id,
        grade=request.grade,
        topic=request.topic,
        difficulty=request.difficulty,
        limit=request.limit,
    )
    return result


@router.post("/progress")
async def save_progress(progress_data: ProgressCreate, db: Session = Depends(get_db)):
    """
    학습 진도 저장 (시청 기록, 퀴즈 점수)
    """
    # 기존 진도 확인
    existing = (
        db.query(Progress)
        .filter(Progress.user_id == 1, Progress.video_id == progress_data.video_id)  # TODO: 인증 연동
        .first()
    )

    if existing:
        # 업데이트
        existing.watched_seconds = max(existing.watched_seconds, progress_data.watched_seconds)
        existing.watch_percentage = max(existing.watch_percentage, progress_data.watch_percentage)
        existing.completed = existing.completed or progress_data.completed
        existing.last_position = progress_data.last_position
        existing.watch_count += 1
        if progress_data.quiz_score is not None:
            existing.quiz_score = progress_data.quiz_score
        db.commit()
        db.refresh(existing)
        return {"message": "진도 업데이트 완료", "progress_id": existing.id}
    else:
        # 신규 생성
        new_progress = Progress(
            user_id=1,  # TODO: 인증 연동
            video_id=progress_data.video_id,
            watched_seconds=progress_data.watched_seconds,
            watch_percentage=progress_data.watch_percentage,
            completed=progress_data.completed,
            quiz_score=progress_data.quiz_score,
            last_position=progress_data.last_position,
        )
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return {"message": "진도 저장 완료", "progress_id": new_progress.id}


@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 학습 대시보드 (통계 + 취약단원 + 최근 시청)
    """
    from sqlalchemy import func

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    # 기본 통계
    stats = (
        db.query(
            func.count(Progress.id).label("total"),
            func.sum(Progress.watched_seconds).label("total_seconds"),
            func.avg(Progress.quiz_score).label("avg_score"),
        )
        .filter(Progress.user_id == user_id)
        .first()
    )

    completed_count = (
        db.query(func.count(Progress.id))
        .filter(Progress.user_id == user_id, Progress.completed == True)
        .scalar()
    )

    # 취약 단원 분석
    weak_topics = await recommendation_service.analyze_weak_topics(db, user_id)

    # 최근 시청
    recent = (
        db.query(Progress)
        .filter(Progress.user_id == user_id)
        .order_by(Progress.updated_at.desc())
        .limit(5)
        .all()
    )

    return DashboardResponse(
        total_watched=stats.total or 0,
        total_completed=completed_count or 0,
        avg_quiz_score=round(stats.avg_score or 0, 1),
        total_watch_time_minutes=round((stats.total_seconds or 0) / 60, 1),
        weak_topics=[
            WeakTopicResponse(
                topic=wt["topic"],
                subtopic=wt["subtopic"],
                avg_score=wt["avg_score"],
                watch_count=wt["watch_count"],
                recommendation=wt["recommendation"],
            )
            for wt in weak_topics
        ],
        recent_videos=[],
    )
