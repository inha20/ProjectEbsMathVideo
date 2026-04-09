"""
playlist_service.py - 재생목록 관리 서비스
재생목록 CRUD + 영상 추가/삭제/순서 변경
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from models import Playlist, PlaylistVideo, Video


class PlaylistService:
    """재생목록 CRUD 서비스"""

    def create_playlist(
        self, db: Session, user_id: int, name: str, description: str = ""
    ) -> Playlist:
        """새 재생목록 생성"""
        playlist = Playlist(
            user_id=user_id,
            name=name,
            description=description,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        return playlist

    def get_user_playlists(self, db: Session, user_id: int) -> List[Playlist]:
        """사용자의 전체 재생목록 조회"""
        return (
            db.query(Playlist)
            .filter(Playlist.user_id == user_id)
            .order_by(Playlist.updated_at.desc())
            .all()
        )

    def get_playlist_detail(
        self, db: Session, playlist_id: int, user_id: int
    ) -> Optional[Playlist]:
        """재생목록 상세 조회 (영상 포함)"""
        return (
            db.query(Playlist)
            .filter(Playlist.id == playlist_id, Playlist.user_id == user_id)
            .first()
        )

    def add_video_to_playlist(
        self, db: Session, playlist_id: int, video_id: int, position: Optional[int] = None
    ) -> PlaylistVideo:
        """재생목록에 영상 추가"""
        # 현재 마지막 위치 확인
        if position is None:
            max_pos = (
                db.query(PlaylistVideo.position)
                .filter(PlaylistVideo.playlist_id == playlist_id)
                .order_by(PlaylistVideo.position.desc())
                .first()
            )
            position = (max_pos[0] + 1) if max_pos else 0

        pv = PlaylistVideo(
            playlist_id=playlist_id,
            video_id=video_id,
            position=position,
        )
        db.add(pv)
        db.commit()
        db.refresh(pv)
        return pv

    def remove_video_from_playlist(
        self, db: Session, playlist_id: int, video_id: int
    ) -> bool:
        """재생목록에서 영상 제거"""
        pv = (
            db.query(PlaylistVideo)
            .filter(
                PlaylistVideo.playlist_id == playlist_id,
                PlaylistVideo.video_id == video_id,
            )
            .first()
        )
        if pv:
            db.delete(pv)
            db.commit()
            return True
        return False

    def delete_playlist(self, db: Session, playlist_id: int, user_id: int) -> bool:
        """재생목록 삭제"""
        playlist = (
            db.query(Playlist)
            .filter(Playlist.id == playlist_id, Playlist.user_id == user_id)
            .first()
        )
        if playlist:
            db.delete(playlist)
            db.commit()
            return True
        return False

    def get_playlist_video_count(self, db: Session, playlist_id: int) -> int:
        """재생목록 내 영상 수 조회"""
        return (
            db.query(PlaylistVideo)
            .filter(PlaylistVideo.playlist_id == playlist_id)
            .count()
        )


# 싱글턴 인스턴스
playlist_service = PlaylistService()
