"""
recommendation_service.py - 추천 엔진 서비스
Rule-based + Score-based 하이브리드 추천 시스템

추천 전략:
1. Rule-based: 학년/단원/난이도 매칭
2. Score-based: 사용자 학습 이력 분석 (정답률, 시청률)
3. 취약 단원 분석: 낮은 점수의 단원 우선 추천
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Video, Progress, User
from services.ebs_service import ebs_service
from services.youtube_service import youtube_service


class RecommendationService:
    """하이브리드 추천 엔진"""

    # ──────────────────────────────────────
    # 1. Rule-based 추천
    # ──────────────────────────────────────

    async def recommend_by_rules(
        self,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict]:
        """
        학년/단원/난이도 기반 규칙 추천
        EBS + YouTube 결과를 병합하여 반환
        """
        results = []

        # EBS 검색
        ebs_results = await ebs_service.search_videos(
            grade=grade, topic=topic, difficulty=difficulty, max_results=limit
        )
        for v in ebs_results:
            v["reason"] = self._generate_rule_reason(v, grade, topic, difficulty)
        results.extend(ebs_results)

        # YouTube 검색 (EBS 결과가 부족할 때)
        if len(results) < limit:
            remaining = limit - len(results)
            query = topic or "수학"
            yt_results = await youtube_service.search_videos(
                query=query, grade=grade, max_results=remaining
            )
            for v in yt_results:
                v["reason"] = f"YouTube에서 '{query}' 관련 인기 강의"
            results.extend(yt_results)

        return results[:limit]

    def _generate_rule_reason(
        self, video: Dict, grade: str, topic: str, difficulty: str
    ) -> str:
        """추천 사유 생성"""
        parts = []
        if grade and video.get("grade") == grade:
            parts.append(f"{grade} 교과 과정")
        if topic and (topic in video.get("topic", "") or topic in video.get("subtopic", "")):
            parts.append(f"'{topic}' 단원 매칭")

        diff_names = {"easy": "기초", "medium": "보통", "hard": "심화"}
        if difficulty:
            parts.append(f"{diff_names.get(difficulty, difficulty)} 난이도")

        return " | ".join(parts) if parts else "교과 과정 기반 추천"

    # ──────────────────────────────────────
    # 2. Score-based 추천
    # ──────────────────────────────────────

    async def recommend_by_score(
        self, db: Session, user_id: int, limit: int = 5
    ) -> List[Dict]:
        """
        사용자의 학습 이력(퀴즈 점수, 시청률)을 분석하여
        취약 단원의 영상을 우선 추천한다.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        # 사용자의 학습 이력 분석
        weak_topics = await self.analyze_weak_topics(db, user_id)

        results = []
        for wt in weak_topics[:3]:  # 상위 3개 취약 단원
            topic_results = await ebs_service.search_videos(
                topic=wt["topic"],
                grade=user.grade,
                difficulty="easy" if wt["avg_score"] < 50 else "medium",
                max_results=2,
            )
            for v in topic_results:
                v["reason"] = (
                    f"취약 단원 보강: {wt['topic']} "
                    f"(평균 점수 {wt['avg_score']:.0f}점)"
                )
            results.extend(topic_results)

        # 결과 부족 시 규칙 기반으로 보충
        if len(results) < limit:
            remaining = limit - len(results)
            rule_results = await self.recommend_by_rules(
                grade=user.grade, limit=remaining
            )
            results.extend(rule_results)

        return results[:limit]

    # ──────────────────────────────────────
    # 3. 취약 단원 분석
    # ──────────────────────────────────────

    async def analyze_weak_topics(
        self, db: Session, user_id: int
    ) -> List[Dict]:
        """
        퀴즈 점수가 낮은 단원을 취약 단원으로 분류한다.
        """
        # Progress + Video JOIN으로 단원별 평균 점수 계산
        results = (
            db.query(
                Video.topic,
                Video.subtopic,
                func.avg(Progress.quiz_score).label("avg_score"),
                func.count(Progress.id).label("watch_count"),
                func.avg(Progress.watch_percentage).label("avg_watch_pct"),
            )
            .join(Video, Progress.video_id == Video.id)
            .filter(Progress.user_id == user_id)
            .filter(Progress.quiz_score.isnot(None))
            .group_by(Video.topic, Video.subtopic)
            .order_by(func.avg(Progress.quiz_score).asc())
            .all()
        )

        weak_topics = []
        for row in results:
            avg_score = row.avg_score or 0
            if avg_score < 70:  # 70점 미만 = 취약
                recommendation = self._get_weakness_recommendation(avg_score)
                weak_topics.append({
                    "topic": row.topic,
                    "subtopic": row.subtopic or "",
                    "avg_score": round(avg_score, 1),
                    "watch_count": row.watch_count,
                    "avg_watch_percentage": round(row.avg_watch_pct or 0, 1),
                    "recommendation": recommendation,
                })

        return weak_topics

    def _get_weakness_recommendation(self, avg_score: float) -> str:
        """취약도별 학습 권고 생성"""
        if avg_score < 30:
            return "🔴 매우 취약 — 기초 개념 영상부터 다시 학습하세요"
        elif avg_score < 50:
            return "🟠 취약 — 개념 정리 영상을 반복 시청하세요"
        elif avg_score < 70:
            return "🟡 보통 — 유형별 문제풀이 영상으로 보강하세요"
        else:
            return "🟢 양호 — 심화 문제에 도전해 보세요"

    # ──────────────────────────────────────
    # 4. 이어보기 추천
    # ──────────────────────────────────────

    async def get_continue_watching(
        self, db: Session, user_id: int, limit: int = 5
    ) -> List[Dict]:
        """
        시청 중이지만 완료하지 않은 영상을 반환한다 (이어보기).
        """
        records = (
            db.query(Progress)
            .filter(
                Progress.user_id == user_id,
                Progress.completed == False,
                Progress.watched_seconds > 0,
            )
            .order_by(Progress.updated_at.desc())
            .limit(limit)
            .all()
        )

        results = []
        for record in records:
            video = record.video
            if video:
                results.append({
                    "id": video.id,
                    "title": video.title,
                    "url": video.url,
                    "source": video.source,
                    "topic": video.topic,
                    "difficulty": video.difficulty,
                    "last_position": record.last_position,
                    "watch_percentage": record.watch_percentage,
                    "reason": f"이어보기 — {record.watch_percentage:.0f}% 시청 완료",
                })

        return results

    # ──────────────────────────────────────
    # 5. 통합 추천
    # ──────────────────────────────────────

    async def get_recommendations(
        self,
        db: Session,
        user_id: Optional[int] = None,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, List[Dict]]:
        """
        통합 추천 결과 반환
        {
            "continue_watching": [...],      # 이어보기
            "recommended_for_you": [...],    # 맞춤 추천
            "topic_based": [...],            # 단원 기반
        }
        """
        result = {
            "continue_watching": [],
            "recommended_for_you": [],
            "topic_based": [],
        }

        # 이어보기
        if user_id:
            result["continue_watching"] = await self.get_continue_watching(
                db, user_id, limit=3
            )

        # 맞춤 추천 (Score-based)
        if user_id:
            result["recommended_for_you"] = await self.recommend_by_score(
                db, user_id, limit=limit
            )
        else:
            # 비로그인: 규칙 기반
            result["recommended_for_you"] = await self.recommend_by_rules(
                grade=grade, topic=topic, difficulty=difficulty, limit=limit
            )

        # 단원 기반
        if topic:
            result["topic_based"] = await self.recommend_by_rules(
                grade=grade, topic=topic, difficulty=difficulty, limit=limit
            )

        return result


# 싱글턴 인스턴스
recommendation_service = RecommendationService()
