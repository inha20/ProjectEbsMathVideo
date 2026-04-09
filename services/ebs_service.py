"""
ebs_service.py - EBS 수학 영상 관리 서비스
사전 구축된 EBS 영상 데이터셋을 로드하고 조건 기반 필터링을 수행한다.
"""

import json
import os
from typing import List, Dict, Optional
from config import get_settings

settings = get_settings()


class EBSService:
    """EBS 수학 영상 데이터 관리 및 검색 서비스"""

    def __init__(self):
        self._videos: List[Dict] = []
        self._loaded = False

    def _load_data(self):
        """JSON 파일에서 EBS 영상 데이터 로드"""
        if self._loaded:
            return

        try:
            data_path = settings.EBS_DATA_PATH
            if os.path.exists(data_path):
                with open(data_path, "r", encoding="utf-8") as f:
                    self._videos = json.load(f)
            else:
                # 데이터 파일이 없으면 기본 데이터 생성
                self._videos = self._generate_default_data()
                # 저장
                os.makedirs(os.path.dirname(data_path), exist_ok=True)
                with open(data_path, "w", encoding="utf-8") as f:
                    json.dump(self._videos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[EBSService] 데이터 로드 오류: {e}")
            self._videos = self._generate_default_data()

        self._loaded = True

    def _generate_default_data(self) -> List[Dict]:
        """EBS 수학 영상 기본 데이터셋 생성"""
        videos = []
        video_id = 1

        curriculum = {
            "중1": {
                "자연수의 성질": ["소인수분해", "최대공약수와 최소공배수"],
                "정수와 유리수": ["정수와 유리수의 개념", "정수와 유리수의 계산"],
                "문자와 식": ["문자의 사용과 식의 계산", "일차식의 계산"],
                "일차방정식": ["일차방정식의 풀이", "일차방정식의 활용"],
                "좌표평면과 그래프": ["좌표평면", "정비례와 반비례"],
                "기본 도형": ["점, 선, 면", "각도와 평행선"],
                "통계": ["자료의 정리와 해석", "도수분포표와 히스토그램"],
            },
            "중2": {
                "유리수와 순환소수": ["유리수와 순환소수 변환", "순환소수의 계산"],
                "식의 계산": ["단항식의 계산", "다항식의 계산"],
                "일차부등식": ["부등식의 성질", "일차부등식의 풀이"],
                "연립방정식": ["연립방정식의 풀이", "연립방정식의 활용"],
                "일차함수": ["일차함수의 그래프", "일차함수와 일차방정식"],
                "삼각형의 성질": ["이등변삼각형", "삼각형의 외심과 내심"],
                "사각형의 성질": ["평행사변형", "여러 가지 사각형"],
                "확률": ["경우의 수", "확률의 계산"],
            },
            "중3": {
                "제곱근과 실수": ["제곱근의 뜻", "무리수와 실수"],
                "다항식의 곱셈과 인수분해": ["다항식의 곱셈", "인수분해"],
                "이차방정식": ["이차방정식의 풀이", "이차방정식의 활용"],
                "이차함수": ["이차함수의 그래프", "이차함수의 최댓값과 최솟값"],
                "피타고라스 정리": ["피타고라스 정리의 증명", "피타고라스 정리의 활용"],
                "삼각비": ["삼각비의 뜻", "삼각비의 활용"],
                "원의 성질": ["원과 직선", "원주각"],
                "통계": ["대푯값과 산포도", "상관관계"],
            },
            "고1": {
                "다항식": ["다항식의 연산", "나머지 정리와 인수분해"],
                "방정식과 부등식": ["복소수", "이차방정식", "이차함수와 이차방정식"],
                "도형의 방정식": ["직선의 방정식", "원의 방정식"],
                "집합과 명제": ["집합", "명제"],
                "함수": ["함수의 뜻", "유리함수와 무리함수"],
                "경우의 수": ["순열과 조합", "이항정리"],
            },
            "고2": {
                "지수와 로그": ["지수", "로그"],
                "삼각함수": ["삼각함수의 뜻", "삼각함수의 그래프"],
                "수열": ["등차수열", "등비수열", "수열의 합"],
                "극한": ["수열의 극한", "급수"],
                "미분": ["미분계수와 도함수", "도함수의 활용"],
                "적분": ["부정적분과 정적분", "정적분의 활용"],
            },
            "고3": {
                "벡터": ["벡터의 연산", "벡터의 내적"],
                "공간좌표": ["공간좌표", "공간도형"],
                "이차곡선": ["포물선", "타원과 쌍곡선"],
                "확률과 통계": ["확률분포", "통계적 추정"],
                "미적분II": ["여러 가지 미분법", "여러 가지 적분법"],
            },
        }

        difficulties = ["easy", "medium", "hard"]
        diff_names = {"easy": "기초", "medium": "개념정리", "hard": "심화"}

        for grade, topics in curriculum.items():
            for topic, subtopics in topics.items():
                for subtopic in subtopics:
                    for diff in difficulties:
                        diff_name = diff_names[diff]
                        videos.append({
                            "id": video_id,
                            "title": f"[EBS {grade}] {topic} - {subtopic} ({diff_name})",
                            "url": f"https://www.ebsi.co.kr/ebs/lms/player/onStepLsnView.ebs?courseId=S{video_id:04d}",
                            "thumbnail_url": "",
                            "source": "ebs",
                            "topic": topic,
                            "subtopic": subtopic,
                            "grade": grade,
                            "difficulty": diff,
                            "duration_seconds": 900 + (video_id % 5) * 300,
                            "description": f"EBS {grade} {topic} {subtopic} {diff_name} 강의",
                            "channel_name": "EBSi",
                            "view_count": 1000 + video_id * 50,
                        })
                        video_id += 1

        return videos

    async def search_videos(
        self,
        query: Optional[str] = None,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        subtopic: Optional[str] = None,
        difficulty: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Dict]:
        """
        조건 기반 EBS 영상 필터링
        """
        self._load_data()
        results = list(self._videos)

        # 필터링
        if grade:
            results = [v for v in results if v.get("grade") == grade]
        if topic:
            results = [v for v in results if topic in v.get("topic", "") or topic in v.get("subtopic", "")]
        if subtopic:
            results = [v for v in results if subtopic in v.get("subtopic", "")]
        if difficulty:
            results = [v for v in results if v.get("difficulty") == difficulty]
        if query:
            query_lower = query.lower()
            results = [
                v for v in results
                if query_lower in v.get("title", "").lower()
                or query_lower in v.get("topic", "").lower()
                or query_lower in v.get("subtopic", "").lower()
                or query_lower in v.get("description", "").lower()
            ]

        # 조회수 기준 정렬
        results.sort(key=lambda v: v.get("view_count", 0), reverse=True)

        return results[:max_results]

    async def get_all_topics(self, grade: Optional[str] = None) -> List[Dict]:
        """학년별 전체 단원 목록 반환"""
        self._load_data()

        topics_set = set()
        for v in self._videos:
            if grade and v.get("grade") != grade:
                continue
            topics_set.add((v.get("grade", ""), v.get("topic", ""), v.get("subtopic", "")))

        topics = [
            {"grade": g, "topic": t, "subtopic": s}
            for g, t, s in sorted(topics_set)
        ]
        return topics

    async def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        """ID로 영상 조회"""
        self._load_data()
        for v in self._videos:
            if v.get("id") == video_id:
                return v
        return None


# 싱글턴 인스턴스
ebs_service = EBSService()
