"""
youtube_service.py - YouTube Data API 연동 서비스
수학 교육 영상 검색 및 메타데이터 수집
"""

from typing import List, Dict, Optional
from config import get_settings

settings = get_settings()


class YouTubeService:
    """YouTube Data API v3 기반 영상 검색 서비스"""

    def __init__(self):
        self._youtube = None

    @property
    def youtube(self):
        """YouTube API 클라이언트 (lazy init)"""
        if self._youtube is None and settings.YOUTUBE_API_KEY:
            from googleapiclient.discovery import build
            self._youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
        return self._youtube

    def _parse_duration(self, iso_duration: str) -> int:
        """ISO 8601 duration → 초 변환 (PT1H2M3S → 3723)"""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration or '')
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    async def search_videos(
        self,
        query: str,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Dict]:
        """
        YouTube에서 수학 관련 영상을 검색한다.
        - query: 검색어
        - grade: 학년 (검색어에 추가)
        - topic: 단원 (검색어에 추가)
        """
        if not self.youtube:
            return self._get_demo_results(query, grade, topic)

        # 검색어 조합
        search_query = f"수학 {query}"
        if grade:
            search_query = f"{grade} {search_query}"
        if topic:
            search_query = f"{search_query} {topic}"
        search_query += " 강의"

        try:
            # 검색 요청
            search_response = self.youtube.search().list(
                q=search_query,
                part="snippet",
                type="video",
                maxResults=max_results,
                order="relevance",
                videoCategoryId="27",  # Education
                relevanceLanguage="ko",
                regionCode="KR",
            ).execute()

            if not search_response.get("items"):
                return []

            # 영상 ID 수집
            video_ids = [item["id"]["videoId"] for item in search_response["items"]]

            # 상세 정보 조회 (재생시간, 조회수)
            videos_response = self.youtube.videos().list(
                part="contentDetails,statistics,snippet",
                id=",".join(video_ids),
            ).execute()

            results = []
            for item in videos_response.get("items", []):
                snippet = item["snippet"]
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                results.append({
                    "title": snippet["title"],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                    "thumbnail_url": snippet["thumbnails"].get("medium", {}).get("url", ""),
                    "source": "youtube",
                    "channel_name": snippet["channelTitle"],
                    "description": snippet.get("description", "")[:200],
                    "duration_seconds": self._parse_duration(content.get("duration", "")),
                    "view_count": int(stats.get("viewCount", 0)),
                    "topic": topic or query,
                    "grade": grade or "",
                    "difficulty": "medium",
                })

            return results

        except Exception as e:
            print(f"[YouTubeService] API 오류: {e}")
            return self._get_demo_results(query, grade, topic)

    def _get_demo_results(
        self, query: str, grade: Optional[str] = None, topic: Optional[str] = None
    ) -> List[Dict]:
        """
        API 키 없을 때 데모용 샘플 결과를 반환한다.
        """
        grade_str = grade or "중2"
        topic_str = topic or query or "수학"

        demo_channels = [
            ("수악중독", "https://www.youtube.com/@SuakJungDok"),
            ("칸아카데미 코리아", "https://www.youtube.com/@KhanAcademyKorean"),
            ("EBSi", "https://www.youtube.com/@ebsi"),
            ("큰수학", "https://www.youtube.com/@bigmath"),
            ("시대인재TV", "https://www.youtube.com/@sidaeinjaetv"),
        ]

        results = []
        difficulties = ["easy", "medium", "hard"]
        for i, (channel, _) in enumerate(demo_channels):
            diff = difficulties[i % 3]
            diff_kr = {"easy": "기초", "medium": "개념", "hard": "심화"}[diff]
            results.append({
                "title": f"[{grade_str}] {topic_str} {diff_kr} 완벽 정리 - {channel}",
                "url": f"https://www.youtube.com/watch?v=demo_{i+1}",
                "thumbnail_url": "",
                "source": "youtube",
                "channel_name": channel,
                "description": f"{grade_str} {topic_str} {diff_kr} 수준 강의입니다.",
                "duration_seconds": 600 + i * 300,
                "view_count": (5 - i) * 10000,
                "topic": topic_str,
                "grade": grade_str,
                "difficulty": diff,
            })

        return results


# 싱글턴 인스턴스
youtube_service = YouTubeService()
