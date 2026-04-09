"""
routers/playlists.py - 재생목록 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import PlaylistCreate, PlaylistAddVideo, PlaylistResponse, PlaylistDetailResponse, VideoResponse
from services.playlist_service import playlist_service
from database import get_db

router = APIRouter(prefix="/api/playlists", tags=["재생목록"])


@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    data: PlaylistCreate, db: Session = Depends(get_db)
):
    """새 재생목록 생성"""
    playlist = playlist_service.create_playlist(
        db, user_id=1, name=data.name, description=data.description  # TODO: 인증 연동
    )
    video_count = playlist_service.get_playlist_video_count(db, playlist.id)
    return PlaylistResponse(
        id=playlist.id,
        name=playlist.name,
        description=playlist.description,
        is_public=playlist.is_public,
        video_count=video_count,
        created_at=playlist.created_at,
    )


@router.get("/", response_model=List[PlaylistResponse])
async def get_playlists(db: Session = Depends(get_db)):
    """내 재생목록 전체 조회"""
    playlists = playlist_service.get_user_playlists(db, user_id=1)
    result = []
    for p in playlists:
        video_count = playlist_service.get_playlist_video_count(db, p.id)
        result.append(PlaylistResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            is_public=p.is_public,
            video_count=video_count,
            created_at=p.created_at,
        ))
    return result


@router.get("/{playlist_id}")
async def get_playlist_detail(playlist_id: int, db: Session = Depends(get_db)):
    """재생목록 상세 조회 (영상 목록 포함)"""
    playlist = playlist_service.get_playlist_detail(db, playlist_id, user_id=1)
    if not playlist:
        raise HTTPException(status_code=404, detail="재생목록을 찾을 수 없습니다")

    videos = []
    for pv in playlist.playlist_videos:
        v = pv.video
        if v:
            videos.append({
                "id": v.id,
                "title": v.title,
                "url": v.url,
                "source": v.source,
                "topic": v.topic,
                "subtopic": v.subtopic,
                "grade": v.grade,
                "difficulty": v.difficulty,
                "duration_seconds": v.duration_seconds,
                "position": pv.position,
            })

    return {
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "videos": videos,
    }


@router.post("/{playlist_id}/videos")
async def add_video_to_playlist(
    playlist_id: int, data: PlaylistAddVideo, db: Session = Depends(get_db)
):
    """재생목록에 영상 추가"""
    pv = playlist_service.add_video_to_playlist(
        db, playlist_id, data.video_id, data.position
    )
    return {"message": "영상이 추가되었습니다", "position": pv.position}


@router.delete("/{playlist_id}/videos/{video_id}")
async def remove_video_from_playlist(
    playlist_id: int, video_id: int, db: Session = Depends(get_db)
):
    """재생목록에서 영상 제거"""
    success = playlist_service.remove_video_from_playlist(db, playlist_id, video_id)
    if not success:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    return {"message": "영상이 제거되었습니다"}


@router.delete("/{playlist_id}")
async def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    """재생목록 삭제"""
    success = playlist_service.delete_playlist(db, playlist_id, user_id=1)
    if not success:
        raise HTTPException(status_code=404, detail="재생목록을 찾을 수 없습니다")
    return {"message": "재생목록이 삭제되었습니다"}
