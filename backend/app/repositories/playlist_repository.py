from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.domain import Playlist, PlaylistItem

class PlaylistRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_playlist(self, session_id: str) -> Playlist:
        playlist = self.db.query(Playlist).filter(Playlist.session_id == session_id).first()
        if not playlist:
            playlist = Playlist(session_id=session_id)
            self.db.add(playlist)
            self.db.commit()
            self.db.refresh(playlist)
        return playlist

    def get_items(self, session_id: str) -> List[PlaylistItem]:
        return self.db.query(PlaylistItem).filter(PlaylistItem.session_id == session_id).order_by(PlaylistItem.added_at.asc()).all()

    def get_item_by_video_id(self, session_id: str, video_id: str) -> Optional[PlaylistItem]:
        return self.db.query(PlaylistItem).filter(
            PlaylistItem.session_id == session_id,
            PlaylistItem.video_id == video_id
        ).first()

    def add_item(self, session_id: str, item_data: dict) -> PlaylistItem:
        # Ensure playlist exists
        self.get_or_create_playlist(session_id)
        
        new_item = PlaylistItem(
            session_id=session_id,
            video_id=item_data["video_id"],
            title=item_data["title"],
            channel=item_data["channel"],
            thumbnail=item_data["thumbnail"],
            source=item_data["source"],
            url=item_data["url"]
        )
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        return new_item

    def remove_item(self, session_id: str, video_id: str) -> bool:
        item = self.get_item_by_video_id(session_id, video_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False

    def clear_playlist(self, session_id: str) -> bool:
        items = self.db.query(PlaylistItem).filter(PlaylistItem.session_id == session_id).all()
        for item in items:
            self.db.delete(item)
        self.db.commit()
        return True
