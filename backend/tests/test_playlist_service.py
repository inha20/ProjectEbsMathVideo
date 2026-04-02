import pytest
from app.services.playlist_service import PlaylistService
from app.models.domain import PlaylistItem

class MockPlaylistRepository:
    def __init__(self):
        self.items = []

    def get_items(self, session_id):
        return [i for i in self.items if i.session_id == session_id]

    def get_item_by_video_id(self, session_id, video_id):
        for item in self.items:
            if item.session_id == session_id and item.video_id == video_id:
                return item
        return None

    def add_item(self, session_id, item_data):
        item = PlaylistItem(
            session_id=session_id,
            video_id=item_data["video_id"],
            title=item_data["title"],
            channel=item_data["channel"],
            thumbnail=item_data["thumbnail"],
            source=item_data.get("source", "youtube"),
            url=item_data["url"]
        )
        self.items.append(item)
        return item

    def remove_item(self, session_id, video_id):
        item = self.get_item_by_video_id(session_id, video_id)
        if item:
            self.items.remove(item)
            return True
        return False

    def clear_playlist(self, session_id):
        self.items = [i for i in self.items if i.session_id != session_id]
        return True

@pytest.fixture
def playlist_service():
    repo = MockPlaylistRepository()
    return PlaylistService(repo)

def test_add_and_get_playlist(playlist_service):
    data = {
        "video_id": "v1", "title": "test", "channel": "ch", 
        "thumbnail": "tumb", "source": "youtube", "url": "url"
    }
    playlist_service.add_to_playlist("user1", data)
    
    pl = playlist_service.get_playlist("user1")
    assert len(pl) == 1
    assert pl[0]["video_id"] == "v1"

def test_remove_playlist(playlist_service):
    data = {"video_id": "v1", "title": "t", "channel": "c", "thumbnail": "t", "url": "u", "source": "youtube"}
    playlist_service.add_to_playlist("u1", data)
    playlist_service.remove_from_playlist("u1", "v1")
    
    assert len(playlist_service.get_playlist("u1")) == 0
