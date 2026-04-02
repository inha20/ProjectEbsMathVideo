from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.schemas.playlist import PlaylistAddRequest, PlaylistResponse
from app.repositories.playlist_repository import PlaylistRepository
from app.services.playlist_service import PlaylistService

router = APIRouter(prefix="/api/playlist", tags=["playlist"])

def get_playlist_service(db: Session = Depends(get_db)) -> PlaylistService:
    repo = PlaylistRepository(db)
    return PlaylistService(repo)

@router.post("/add", response_model=PlaylistResponse)
def add_playlist(req: PlaylistAddRequest, service: PlaylistService = Depends(get_playlist_service)):
    return service.add_to_playlist(req.session_id, req.model_dump())

@router.get("/{session_id}", response_model=PlaylistResponse)
def get_playlist(session_id: str, service: PlaylistService = Depends(get_playlist_service)):
    return {"message": "success", "playlist": service.get_playlist(session_id)}

@router.delete("/{session_id}/{video_id}", response_model=PlaylistResponse)
def remove_playlist_item(session_id: str, video_id: str, service: PlaylistService = Depends(get_playlist_service)):
    return service.remove_from_playlist(session_id, video_id)

@router.delete("/{session_id}", response_model=PlaylistResponse)
def clear_playlist(session_id: str, service: PlaylistService = Depends(get_playlist_service)):
    return service.clear_playlist(session_id)
