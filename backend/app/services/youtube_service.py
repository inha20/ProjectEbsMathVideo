import httpx
import logging
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

logger = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

MOCK_VIDEOS = {
    # Keep the mock video behavior for development
    "default": [
        {"video_id": "dQw4w9WgXcQ", "title": "수학 기초 개념", "channel": "수학왕TV", "thumbnail": "", "description": "", "url": "", "published_at": "", "view_count": ""}
    ]
}

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.use_real_api = bool(self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search(self, query: str, max_results: int = 6) -> List[Dict[str, Any]]:
        """Search YouTube videos with retry and error handling."""
        if self.use_real_api:
            try:
                return await self._search_api(query, max_results)
            except Exception as e:
                logger.error(f"YouTube API failed: {e}")
                return self._search_mock(query, max_results)
        return self._search_mock(query, max_results)

    async def _search_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": self.api_key,
            "relevanceLanguage": "ko",
            "regionCode": "KR",
            "videoCategoryId": "27"  # Education category
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
            resp.raise_for_status()
            
            data = resp.json()
            results = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                vid = item.get("id", {}).get("videoId", "")
                results.append({
                    "video_id": vid,
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "description": snippet.get("description", ""),
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "published_at": snippet.get("publishedAt", "")[:10],
                    "view_count": "",
                })
            return results

    def _search_mock(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        result = MOCK_VIDEOS["default"].copy()
        
        # Add user query logically to simulate a real result
        modified = []
        for v in result:
            v2 = v.copy()
            v2["title"] = f"[{query}] " + v2["title"]
            v2["url"] = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            modified.append(v2)
            
        return modified

    def get_youtube_search_url(self, query: str) -> str:
        return f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
