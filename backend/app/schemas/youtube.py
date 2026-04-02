from pydantic import BaseModel
from typing import List, Dict, Any

class SearchRequest(BaseModel):
    query: str
    max_results: int = 6

class YouTubeVideoResponse(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: str
    description: str
    url: str
    published_at: str
    view_count: str

class SearchResponse(BaseModel):
    query: str
    results: List[YouTubeVideoResponse]
    search_url: str
