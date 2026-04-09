"""
chat_service.py - AI 챗봇 서비스
OpenAI API를 활용하여 학생과의 대화에서 학습 니즈를 파악하고
영상 추천에 필요한 정보(학년, 단원, 난이도)를 추출한다.
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from config import get_settings

settings = get_settings()


# ──────────────────────────────────────
# 시스템 프롬프트
# ──────────────────────────────────────
SYSTEM_PROMPT = """당신은 수학 학습 도우미 AI입니다. 학생과 자연스럽게 대화하면서 다음을 수행합니다:

1. 학생의 학년(중1~고3)을 파악합니다.
2. 어려워하는 수학 단원/개념을 파악합니다.
3. 학생의 수준(기초/보통/심화)을 판단합니다.
4. 파악된 정보를 바탕으로 적절한 영상을 추천합니다.

응답 형식:
- 친절하고 격려하는 톤으로 대화하세요.
- 정보를 충분히 파악하면, 응답 마지막에 다음 JSON 블록을 포함하세요:

```json
{"grade": "중2", "topic": "함수", "subtopic": "일차함수", "difficulty": "medium"}
```

- 아직 정보가 부족하면 JSON 없이 추가 질문만 하세요.
- 수학 관련 질문이 아닌 경우에도 친절하게 대화하되, 자연스럽게 학습 주제로 유도하세요.

[수학 교과 단원 목록]
중1: 자연수의 성질, 정수와 유리수, 문자와 식, 일차방정식, 좌표평면과 그래프, 기본 도형, 작도와 합동, 평면도형, 입체도형, 통계
중2: 유리수와 순환소수, 식의 계산, 일차부등식, 연립방정식, 일차함수, 삼각형의 성질, 사각형의 성질, 도형의 닮음, 확률
중3: 제곱근과 실수, 다항식의 곱셈과 인수분해, 이차방정식, 이차함수, 통계, 피타고라스 정리, 삼각비, 원의 성질
고1: 다항식, 방정식과 부등식, 도형의 방정식, 집합과 명제, 함수, 경우의 수
고2: 지수와 로그, 삼각함수, 수열, 극한, 미분, 적분
고3: 벡터, 공간좌표, 공간도형, 이차곡선, 확률과 통계, 미적분II
"""


class ChatService:
    """AI 챗봇 서비스 클래스"""

    def __init__(self):
        self._client = None

    @property
    def client(self) -> Optional[OpenAI]:
        """OpenAI 클라이언트 (lazy init)"""
        if self._client is None and settings.OPENAI_API_KEY:
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def extract_learning_info(self, text: str) -> Dict:
        """
        AI 응답 또는 사용자 메시지에서 학습 정보 JSON을 추출한다.
        """
        # JSON 블록 추출 시도
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 인라인 JSON 추출 시도
        json_match = re.search(r'\{[^{}]*"grade"[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # 키워드 기반 휴리스틱 추출
        return self._heuristic_extract(text)

    def _heuristic_extract(self, text: str) -> Dict:
        """키워드 매칭으로 학년/단원/난이도 추출 (fallback)"""
        info = {}

        # 학년 추출
        grade_patterns = {
            r'중학교?\s*1|중1': '중1', r'중학교?\s*2|중2': '중2', r'중학교?\s*3|중3': '중3',
            r'고등학교?\s*1|고1': '고1', r'고등학교?\s*2|고2': '고2', r'고등학교?\s*3|고3': '고3',
        }
        for pattern, grade in grade_patterns.items():
            if re.search(pattern, text):
                info['grade'] = grade
                break

        # 단원 추출
        topics = [
            '함수', '방정식', '부등식', '도형', '통계', '확률', '미분', '적분',
            '수열', '벡터', '삼각함수', '인수분해', '제곱근', '피타고라스',
            '일차함수', '이차함수', '이차방정식', '연립방정식', '삼각비',
            '집합', '명제', '경우의 수', '지수', '로그', '극한',
        ]
        for topic in topics:
            if topic in text:
                info['topic'] = topic
                break

        # 난이도 추출
        if any(w in text for w in ['기초', '쉬운', '기본', '처음']):
            info['difficulty'] = 'easy'
        elif any(w in text for w in ['심화', '어려운', '고급', '응용']):
            info['difficulty'] = 'hard'
        elif any(w in text for w in ['보통', '중간', '표준']):
            info['difficulty'] = 'medium'

        return info

    async def chat(self, message: str, history: List[Dict] = None) -> Tuple[str, Dict]:
        """
        사용자 메시지에 대해 AI 응답을 생성한다.
        Returns: (reply_text, extracted_info)
        """
        if not self.client:
            # API 키가 없을 때 → 룰 기반 응답
            return self._fallback_chat(message, history)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 이전 대화 이력 추가
        if history:
            for msg in history[-settings.MAX_CHAT_HISTORY:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
            )
            reply = response.choices[0].message.content
            extracted = self.extract_learning_info(reply)
            return reply, extracted

        except Exception as e:
            # API 에러 시 fallback
            return self._fallback_chat(message, history)

    def _fallback_chat(self, message: str, history: List[Dict] = None) -> Tuple[str, Dict]:
        """
        OpenAI API 없이 동작하는 룰 기반 챗봇 (데모용)
        """
        extracted = self._heuristic_extract(message)

        if not extracted:
            reply = (
                "안녕하세요! 수학 학습 도우미입니다 😊\n\n"
                "어떤 학년이시고, 어떤 수학 단원이 어렵나요?\n"
                "예: '중학교 2학년인데 일차함수가 어려워요'"
            )
            return reply, {}

        parts = []
        if 'grade' in extracted:
            parts.append(f"{extracted['grade']} 학생이시군요!")
        if 'topic' in extracted:
            parts.append(f"**{extracted['topic']}** 단원을 공부하고 싶으시군요.")
        if 'difficulty' not in extracted:
            extracted['difficulty'] = 'medium'

        difficulty_names = {'easy': '기초', 'medium': '보통', 'hard': '심화'}
        diff_name = difficulty_names.get(extracted.get('difficulty', 'medium'), '보통')

        reply = (
            " ".join(parts) + "\n\n"
            f"📚 {diff_name} 수준의 관련 영상을 찾아볼게요!\n"
            "아래 추천 영상을 확인해 보세요."
        )
        return reply, extracted


# 싱글턴 인스턴스
chat_service = ChatService()
