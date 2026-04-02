"""
YouTube Video Search Service.
Supports both real YouTube Data API v3 and fallback mock data.
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


# ──────────────────────────────────────────────
# Mock data for when no API key is available
# ──────────────────────────────────────────────
MOCK_VIDEOS = {
    "default": [
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "수학의 정석 - 기초 개념 총정리",
            "channel": "수학왕TV",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
            "description": "수학 기초 개념을 한 번에 정리하는 강의입니다.",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "view_count": "1,234,567",
            "published_at": "2025-01-15"
        }
    ],
    "수학I": [
        {
            "video_id": "math1_001",
            "title": "[수학I] 지수와 로그 개념 완벽 정리 | 1시간 총정리",
            "channel": "수학의 신",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "수학I 지수와 로그 단원의 핵심 개념을 빠짐없이 정리합니다.",
            "url": "https://www.youtube.com/results?search_query=수학I+지수와+로그+개념",
            "view_count": "523,000",
            "published_at": "2025-03-10"
        },
        {
            "video_id": "math1_002",
            "title": "[수학I] 삼각함수 그래프 완벽 이해 | sin cos tan",
            "channel": "큰별쌤 수학",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "삼각함수의 그래프를 시각적으로 이해하는 강의",
            "url": "https://www.youtube.com/results?search_query=수학I+삼각함수+그래프",
            "view_count": "389,000",
            "published_at": "2025-04-20"
        },
        {
            "video_id": "math1_003",
            "title": "[수학I] 등차수열 등비수열 공식 총정리",
            "channel": "수학 마스터",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "수열의 핵심 공식과 문제 풀이 전략",
            "url": "https://www.youtube.com/results?search_query=수학I+수열+공식",
            "view_count": "298,000",
            "published_at": "2025-05-15"
        }
    ],
    "수학II": [
        {
            "video_id": "math2_001",
            "title": "[수학II] 함수의 극한 개념 정리 | 극한값 구하기",
            "channel": "수학의 신",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "함수의 극한 개념과 극한값 계산 방법 총정리",
            "url": "https://www.youtube.com/results?search_query=수학II+함수의+극한",
            "view_count": "445,000",
            "published_at": "2025-02-28"
        },
        {
            "video_id": "math2_002",
            "title": "[수학II] 미분 완벽 정리 | 도함수부터 활용까지",
            "channel": "1등급 수학",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "미분의 기초부터 활용 문제까지 완벽 정리",
            "url": "https://www.youtube.com/results?search_query=수학II+미분+개념",
            "view_count": "567,000",
            "published_at": "2025-03-05"
        },
        {
            "video_id": "math2_003",
            "title": "[수학II] 정적분과 넓이 구하기 | 적분 활용",
            "channel": "수학 마스터",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "정적분을 활용한 넓이 계산 완벽 정리",
            "url": "https://www.youtube.com/results?search_query=수학II+적분+넓이",
            "view_count": "312,000",
            "published_at": "2025-06-01"
        }
    ],
    "미적분": [
        {
            "video_id": "calc_001",
            "title": "[미적분] 수열의 극한 총정리 | 수능 필수 개념",
            "channel": "수능 수학 King",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "수능 미적분 수열의 극한 핵심 정리",
            "url": "https://www.youtube.com/results?search_query=미적분+수열의+극한+수능",
            "view_count": "678,000",
            "published_at": "2025-01-20"
        },
        {
            "video_id": "calc_002",
            "title": "[미적분] 킬러문항 풀이 전략 | 4점 공략법",
            "channel": "수학의 신",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "수능 미적분 킬러문항 유형별 풀이 전략",
            "url": "https://www.youtube.com/results?search_query=미적분+킬러문항+풀이",
            "view_count": "892,000",
            "published_at": "2025-07-10"
        }
    ],
    "확률과 통계": [
        {
            "video_id": "ps_001",
            "title": "[확률과 통계] 순열과 조합 한 방 정리",
            "channel": "큰별쌤 수학",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "경우의 수, 순열, 조합 공식 한 번에 정리",
            "url": "https://www.youtube.com/results?search_query=확률과통계+순열+조합",
            "view_count": "445,000",
            "published_at": "2025-04-12"
        },
        {
            "video_id": "ps_002",
            "title": "[확률과 통계] 조건부확률과 독립사건 완벽 정리",
            "channel": "수학 마스터",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "조건부확률과 독립시행 확률 핵심 개념",
            "url": "https://www.youtube.com/results?search_query=확률과통계+조건부확률",
            "view_count": "334,000",
            "published_at": "2025-05-22"
        }
    ],
    "기하": [
        {
            "video_id": "geo_001",
            "title": "[기하] 이차곡선 총정리 | 포물선 타원 쌍곡선",
            "channel": "수능 수학 King",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "이차곡선 세 가지 유형의 핵심 성질 총정리",
            "url": "https://www.youtube.com/results?search_query=기하+이차곡선+포물선",
            "view_count": "267,000",
            "published_at": "2025-03-18"
        },
        {
            "video_id": "geo_002",
            "title": "[기하] 벡터의 내적과 외적 완벽 정리",
            "channel": "1등급 수학",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "벡터의 연산과 내적 개념 완벽 정리",
            "url": "https://www.youtube.com/results?search_query=기하+벡터+내적",
            "view_count": "198,000",
            "published_at": "2025-06-08"
        }
    ],
    "중학수학": [
        {
            "video_id": "mid_001",
            "title": "[중등수학] 일차방정식 완벽 정리 | 개념+문제풀이",
            "channel": "쉬운 수학",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "중학교 일차방정식 개념과 다양한 문제 풀이",
            "url": "https://www.youtube.com/results?search_query=중학수학+일차방정식",
            "view_count": "756,000",
            "published_at": "2025-02-14"
        },
        {
            "video_id": "mid_002",
            "title": "[중등수학] 이차함수 그래프 그리기 | 꼭짓점 축",
            "channel": "수학왕TV",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "이차함수 y=ax²+bx+c 그래프의 모든 것",
            "url": "https://www.youtube.com/results?search_query=중학수학+이차함수+그래프",
            "view_count": "534,000",
            "published_at": "2025-04-02"
        },
        {
            "video_id": "mid_003",
            "title": "[중등수학] 인수분해 공식 총정리 | 5가지 유형",
            "channel": "쉬운 수학",
            "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
            "description": "인수분해 5가지 공식과 활용법 총정리",
            "url": "https://www.youtube.com/results?search_query=중학수학+인수분해+공식",
            "view_count": "623,000",
            "published_at": "2025-05-10"
        }
    ]
}


class YouTubeService:
    """YouTube video search service with API + fallback mock."""

    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.use_real_api = bool(self.api_key)

    async def search(
        self,
        query: str,
        max_results: int = 6,
    ) -> list[dict]:
        """Search for YouTube videos."""
        if self.use_real_api:
            return await self._search_api(query, max_results)
        else:
            return self._search_mock(query, max_results)

    async def _search_api(self, query: str, max_results: int) -> list[dict]:
        """Search using real YouTube Data API v3."""
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": self.api_key,
            "relevanceLanguage": "ko",
            "regionCode": "KR",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)

            if resp.status_code != 200:
                # Fallback to mock on API error
                return self._search_mock(query, max_results)

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

    def _search_mock(self, query: str, max_results: int) -> list[dict]:
        """Search using mock data based on keyword matching."""
        query_lower = query.lower()
        results = []

        # Find best matching topic
        best_key = "default"
        best_score = 0

        for key in MOCK_VIDEOS:
            if key == "default":
                continue
            key_lower = key.lower()
            if key_lower in query_lower or query_lower in key_lower:
                score = len(key)
                if score > best_score:
                    best_score = score
                    best_key = key

        # If no direct match, check individual words
        if best_key == "default":
            for key in MOCK_VIDEOS:
                if key == "default":
                    continue
                for word in query.split():
                    if len(word) >= 2 and (word in key or key in word):
                        best_key = key
                        break

        # Check for level-based matching
        if best_key == "default":
            if "중학" in query or "중등" in query:
                best_key = "중학수학"
            elif "미적분" in query:
                best_key = "미적분"
            elif "확률" in query or "통계" in query:
                best_key = "확률과 통계"
            elif "기하" in query:
                best_key = "기하"

        results = MOCK_VIDEOS.get(best_key, MOCK_VIDEOS["default"])

        # Customize titles to include search query context
        customized = []
        for video in results[:max_results]:
            v = video.copy()
            # Update the URL to use actual YouTube search
            v["url"] = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            customized.append(v)

        return customized

    def get_youtube_search_url(self, query: str) -> str:
        """Get a YouTube search URL for a query."""
        return f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"


# Singleton
youtube_service = YouTubeService()
