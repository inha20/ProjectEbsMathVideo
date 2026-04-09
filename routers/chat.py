"""
routers/chat.py - 채팅 API 라우터
학생-AI 대화 엔드포인트
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import ChatRequest, ChatResponse, RecommendedVideo
from services.chat_service import chat_service
from services.recommendation_service import recommendation_service
from database import get_db

router = APIRouter(prefix="/api/chat", tags=["채팅"])


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    """
    학생 메시지를 받아 AI가 응답하고,
    파악된 학습 정보를 바탕으로 영상을 추천한다.
    """
    # 대화 이력 변환
    history = [{"role": m.role, "content": m.content} for m in request.history]

    # AI 챗봇 응답 생성
    reply, extracted_info = await chat_service.chat(request.message, history)

    # 추출된 정보로 영상 추천
    recommended = []
    if extracted_info.get("topic") or extracted_info.get("grade"):
        videos = await recommendation_service.recommend_by_rules(
            grade=extracted_info.get("grade"),
            topic=extracted_info.get("topic"),
            difficulty=extracted_info.get("difficulty"),
            limit=5,
        )
        recommended = [
            RecommendedVideo(
                title=v["title"],
                url=v["url"],
                source=v.get("source", "ebs"),
                topic=v.get("topic", ""),
                difficulty=v.get("difficulty", "medium"),
                reason=v.get("reason", ""),
            )
            for v in videos
        ]

    return ChatResponse(
        reply=reply,
        recommended_videos=recommended,
        extracted_info=extracted_info,
    )
