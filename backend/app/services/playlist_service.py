from typing import List, Dict, Any
from app.repositories.playlist_repository import PlaylistRepository

class PlaylistService:
    def __init__(self, repo: PlaylistRepository):
        self.repo = repo

    def add_to_playlist(self, session_id: str, item_data: dict) -> Dict[str, Any]:
        existing = self.repo.get_item_by_video_id(session_id, item_data["video_id"])
        if existing:
            return {"message": "이미 재생목록에 있습니다.", "playlist": self.get_playlist(session_id)}
            
        self.repo.add_item(session_id, item_data)
        return {"message": "추가되었습니다!", "playlist": self.get_playlist(session_id)}

    def get_playlist(self, session_id: str) -> List[Dict[str, Any]]:
        items = self.repo.get_items(session_id)
        return [
            {
                "video_id": item.video_id,
                "title": item.title,
                "channel": item.channel,
                "thumbnail": item.thumbnail,
                "source": item.source,
                "url": item.url
            } for item in items
        ]

    def remove_from_playlist(self, session_id: str, video_id: str) -> Dict[str, Any]:
        success = self.repo.remove_item(session_id, video_id)
        msg = "삭제되었습니다." if success else "항목을 찾을 수 없습니다."
        return {"message": msg, "playlist": self.get_playlist(session_id)}

    def clear_playlist(self, session_id: str) -> Dict[str, Any]:
        self.repo.clear_playlist(session_id)
        return {"message": "재생목록을 비웠습니다.", "playlist": []}
