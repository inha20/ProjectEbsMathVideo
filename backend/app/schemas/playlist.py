from pydantic import BaseModel
from typing import List

class PlaylistAddRequest(BaseModel):
    session_id: str
    video_id: str
    title: str
    channel: str
    thumbnail: str
    source: str  # youtube / ebs
    url: str

class PlaylistItemResponse(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: str
    source: str
    url: str

class PlaylistResponse(BaseModel):
    message: str = ""
    playlist: List[PlaylistItemResponse]
