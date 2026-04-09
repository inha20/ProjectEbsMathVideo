"""
tests/test_recommendation.py - 추천 엔진 테스트
"""

import pytest
import asyncio
from services.chat_service import ChatService
from services.ebs_service import EBSService
from services.recommendation_service import RecommendationService


class TestChatService:
    """ChatService 테스트"""

    def setup_method(self):
        self.service = ChatService()

    def test_extract_grade_from_text(self):
        """학년 추출 테스트"""
        info = self.service.extract_learning_info("중학교 2학년입니다")
        assert info.get("grade") == "중2"

    def test_extract_topic_from_text(self):
        """단원 추출 테스트"""
        info = self.service.extract_learning_info("일차함수가 어려워요")
        assert info.get("topic") == "일차함수"

    def test_extract_difficulty_easy(self):
        """기초 난이도 추출 테스트"""
        info = self.service.extract_learning_info("기초부터 배우고 싶어요")
        assert info.get("difficulty") == "easy"

    def test_extract_difficulty_hard(self):
        """심화 난이도 추출 테스트"""
        info = self.service.extract_learning_info("심화 문제를 풀고 싶어요")
        assert info.get("difficulty") == "hard"

    def test_extract_json_block(self):
        """JSON 블록 추출 테스트"""
        text = '좋아요! ```json\n{"grade": "고1", "topic": "함수"}\n``` 추천해드릴게요.'
        info = self.service.extract_learning_info(text)
        assert info.get("grade") == "고1"
        assert info.get("topic") == "함수"

    def test_extract_high_school(self):
        """고등학교 학년 추출"""
        info = self.service.extract_learning_info("고등학교 2학년 수열")
        assert info.get("grade") == "고2"
        assert info.get("topic") == "수열"

    def test_empty_message(self):
        """빈 메시지에서는 빈 dict 반환"""
        info = self.service.extract_learning_info("안녕하세요")
        assert info == {} or "grade" not in info

    def test_fallback_chat(self):
        """Fallback 챗봇 테스트"""
        reply, info = self.service._fallback_chat("중2 함수 어려워요")
        assert "함수" in reply or len(reply) > 0
        assert info.get("topic") == "함수"


class TestEBSService:
    """EBSService 테스트"""

    def setup_method(self):
        self.service = EBSService()

    def test_load_data(self):
        """데이터 로드 테스트"""
        self.service._load_data()
        assert len(self.service._videos) > 0

    def test_search_by_grade(self):
        """학년 필터링 테스트"""
        results = asyncio.get_event_loop().run_until_complete(
            self.service.search_videos(grade="중2", max_results=5)
        )
        assert len(results) > 0
        for v in results:
            assert v["grade"] == "중2"

    def test_search_by_topic(self):
        """단원 필터링 테스트"""
        results = asyncio.get_event_loop().run_until_complete(
            self.service.search_videos(topic="함수", max_results=5)
        )
        assert len(results) > 0

    def test_search_by_difficulty(self):
        """난이도 필터링 테스트"""
        results = asyncio.get_event_loop().run_until_complete(
            self.service.search_videos(difficulty="easy", max_results=5)
        )
        for v in results:
            assert v["difficulty"] == "easy"

    def test_get_all_topics(self):
        """전체 단원 목록 테스트"""
        topics = asyncio.get_event_loop().run_until_complete(
            self.service.get_all_topics()
        )
        assert len(topics) > 0


class TestRecommendationService:
    """RecommendationService 테스트"""

    def setup_method(self):
        self.service = RecommendationService()

    def test_rule_based_recommendation(self):
        """Rule-based 추천 테스트"""
        results = asyncio.get_event_loop().run_until_complete(
            self.service.recommend_by_rules(grade="중2", topic="함수", limit=5)
        )
        assert len(results) > 0
        assert len(results) <= 5

    def test_recommendation_has_reason(self):
        """추천 결과에 사유 포함 여부"""
        results = asyncio.get_event_loop().run_until_complete(
            self.service.recommend_by_rules(grade="중1", topic="방정식", limit=3)
        )
        for v in results:
            assert "reason" in v
            assert len(v["reason"]) > 0

    def test_weakness_recommendation_text(self):
        """취약도별 권고 텍스트 테스트"""
        assert "매우 취약" in self.service._get_weakness_recommendation(20)
        assert "취약" in self.service._get_weakness_recommendation(40)
        assert "보통" in self.service._get_weakness_recommendation(60)
        assert "양호" in self.service._get_weakness_recommendation(80)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
