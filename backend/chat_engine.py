"""
Rule-based AI Chat Engine for Math Video Recommendation.
Analyzes student level, identifies weak topics, and generates search keywords.
"""
import uuid
import re
from datetime import datetime, timezone


# ──────────────────────────────────────────────
# Math topic taxonomy
# ──────────────────────────────────────────────
MATH_TOPICS = {
    "middle": {
        "label": "중학교 수학",
        "topics": [
            "일차방정식", "일차함수", "이차방정식", "이차함수",
            "연립방정식", "부등식", "피타고라스", "삼각비",
            "통계", "확률", "도형", "원", "인수분해",
            "제곱근", "다항식"
        ]
    },
    "high": {
        "label": "고등학교 수학",
        "topics": [
            "다항식", "방정식과 부등식", "도형의 방정식",
            "집합과 명제", "함수", "경우의 수",
            "지수와 로그", "삼각함수", "수열",
            "수학I", "수학II", "미적분", "확률과 통계", "기하"
        ]
    },
    "suneung": {
        "label": "수능 수학",
        "topics": [
            "수학I", "수학II", "미적분", "확률과 통계", "기하",
            "수능특강", "수능완성", "킬러문항", "준킬러",
            "4점 공략", "가형", "나형", "공통과목", "선택과목"
        ]
    }
}

# ──────────────────────────────────────────────
# Conversation states & transitions
# ──────────────────────────────────────────────
STATE_GREETING = "greeting"
STATE_ASK_LEVEL = "ask_level"
STATE_ASK_TOPIC = "ask_topic"
STATE_ASK_DIFFICULTY = "ask_difficulty"
STATE_RECOMMEND = "recommend"
STATE_FREE_CHAT = "free_chat"

# Level detection keywords
LEVEL_KEYWORDS = {
    "middle": ["중학", "중1", "중2", "중3", "중등"],
    "high": ["고등", "고1", "고2", "고3", "고등학교"],
    "suneung": ["수능", "수특", "수완", "ebs", "모의고사", "대입", "입시", "n수생"]
}

# Difficulty keywords
DIFFICULTY_KEYWORDS = {
    "beginner": ["기초", "처음", "쉬운", "입문", "기본", "개념", "못해", "어려워", "모르"],
    "intermediate": ["보통", "중간", "복습", "다시", "심화 전"],
    "advanced": ["심화", "어려운", "킬러", "고난도", "4점", "만점", "상위권"]
}


class ConversationState:
    """Tracks state for a single chat session."""

    def __init__(self):
        self.session_id: str = str(uuid.uuid4())
        self.state: str = STATE_GREETING
        self.level: str | None = None          # middle / high / suneung
        self.topics: list[str] = []
        self.difficulty: str | None = None      # beginner / intermediate / advanced
        self.history: list[dict] = []
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "state": self.state,
            "level": self.level,
            "topics": self.topics,
            "difficulty": self.difficulty,
        }


class ChatEngine:
    """Rule-based conversational engine."""

    def __init__(self):
        self.sessions: dict[str, ConversationState] = {}

    # ── public API ────────────────────────────

    def create_session(self) -> str:
        conv = ConversationState()
        self.sessions[conv.session_id] = conv
        return conv.session_id

    def get_session(self, session_id: str) -> ConversationState | None:
        return self.sessions.get(session_id)

    def chat(self, session_id: str, user_message: str) -> dict:
        conv = self.sessions.get(session_id)
        if conv is None:
            session_id = self.create_session()
            conv = self.sessions[session_id]

        conv.history.append({"role": "user", "content": user_message})

        response = self._process(conv, user_message)

        conv.history.append({"role": "assistant", "content": response["message"]})

        return {
            "session_id": session_id,
            "message": response["message"],
            "state": conv.to_dict(),
            "recommendations": response.get("recommendations"),
            "search_keywords": response.get("search_keywords"),
        }

    def get_greeting(self, session_id: str) -> dict:
        conv = self.sessions.get(session_id)
        if conv is None:
            session_id = self.create_session()
            conv = self.sessions[session_id]

        msg = (
            "안녕하세요! 🎓 수학 영상 추천 도우미입니다.\n\n"
            "저와 대화하면서 딱 맞는 수학 강의 영상을 찾아드릴게요.\n"
            "먼저, 현재 학년이 어떻게 되시나요?\n\n"
            "• 중학생 (중1~중3)\n"
            "• 고등학생 (고1~고3)\n"
            "• 수능 준비생"
        )
        conv.state = STATE_ASK_LEVEL
        conv.history.append({"role": "assistant", "content": msg})
        return {
            "session_id": session_id,
            "message": msg,
            "state": conv.to_dict(),
        }

    # ── internal routing ──────────────────────

    def _process(self, conv: ConversationState, msg: str) -> dict:
        msg_lower = msg.strip().lower()

        if conv.state == STATE_ASK_LEVEL:
            return self._handle_level(conv, msg_lower)
        elif conv.state == STATE_ASK_TOPIC:
            return self._handle_topic(conv, msg_lower, msg)
        elif conv.state == STATE_ASK_DIFFICULTY:
            return self._handle_difficulty(conv, msg_lower)
        elif conv.state == STATE_RECOMMEND:
            return self._handle_recommend(conv, msg_lower, msg)
        else:
            return self._handle_free_chat(conv, msg_lower, msg)

    # ── state handlers ────────────────────────

    def _handle_level(self, conv: ConversationState, msg: str) -> dict:
        detected = self._detect_level(msg)

        if detected:
            conv.level = detected
            conv.state = STATE_ASK_TOPIC
            label = MATH_TOPICS[detected]["label"]
            topic_list = MATH_TOPICS[detected]["topics"]
            topics_str = ", ".join(topic_list[:8])

            return {
                "message": (
                    f"**{label}** 과정이시군요! 👍\n\n"
                    f"어떤 단원이 어렵거나, 공부하고 싶은 주제가 있나요?\n"
                    f"예시: {topics_str}\n\n"
                    f"자유롭게 말씀해주세요! 여러 주제도 괜찮아요."
                )
            }
        else:
            return {
                "message": (
                    "죄송해요, 학년을 잘 이해하지 못했어요. 😅\n"
                    "아래 중 하나를 선택해주세요:\n\n"
                    "• **중학생** (중1~중3)\n"
                    "• **고등학생** (고1~고3)\n"
                    "• **수능 준비생**"
                )
            }

    def _handle_topic(self, conv: ConversationState, msg_lower: str, msg_raw: str) -> dict:
        topics = self._extract_topics(conv.level, msg_lower)

        if not topics:
            # Try to use raw message as topic keyword
            cleaned = re.sub(r'[^\w\s가-힣]', '', msg_raw).strip()
            if len(cleaned) >= 2:
                topics = [cleaned]

        if topics:
            conv.topics = topics
            conv.state = STATE_ASK_DIFFICULTY
            topics_str = ", ".join(topics)
            return {
                "message": (
                    f"**{topics_str}** 관련해서 찾아드릴게요! 📚\n\n"
                    f"실력 수준은 어느 정도인가요?\n\n"
                    f"• 🌱 **기초** - 개념부터 차근차근\n"
                    f"• 🌿 **중급** - 개념은 알지만 문제풀이 연습\n"
                    f"• 🌳 **심화** - 고난도 문제 도전"
                )
            }
        else:
            topic_list = MATH_TOPICS.get(conv.level, MATH_TOPICS["high"])["topics"]
            return {
                "message": (
                    "어떤 주제를 공부하고 싶은지 좀 더 구체적으로 알려주세요! 🤔\n\n"
                    f"예시: {', '.join(topic_list[:6])}\n\n"
                    "또는 '전체' 라고 하시면 전반적인 영상을 추천해드릴게요."
                )
            }

    def _handle_difficulty(self, conv: ConversationState, msg: str) -> dict:
        difficulty = self._detect_difficulty(msg)

        if not difficulty:
            # Default to intermediate if unclear
            difficulty = "intermediate"

        conv.difficulty = difficulty
        conv.state = STATE_RECOMMEND

        keywords = self._generate_keywords(conv)
        level_label = MATH_TOPICS.get(conv.level, {}).get("label", "수학")
        topics_str = ", ".join(conv.topics) if conv.topics else "전체"
        diff_labels = {"beginner": "기초", "intermediate": "중급", "advanced": "심화"}
        diff_label = diff_labels.get(difficulty, "중급")

        return {
            "message": (
                f"완벽해요! 맞춤 영상을 찾아볼게요 🔍\n\n"
                f"📋 **분석 결과:**\n"
                f"• 과정: {level_label}\n"
                f"• 주제: {topics_str}\n"
                f"• 수준: {diff_label}\n\n"
                f"아래에서 YouTube 영상과 EBS 강좌 추천을 확인해보세요!\n"
                f"추가로 다른 주제도 검색하고 싶으시면 말씀해주세요. 😊"
            ),
            "recommendations": {
                "level": conv.level,
                "topics": conv.topics,
                "difficulty": difficulty,
            },
            "search_keywords": keywords,
        }

    def _handle_recommend(self, conv: ConversationState, msg_lower: str, msg_raw: str) -> dict:
        # Check if user wants to change topic
        new_level = self._detect_level(msg_lower)
        if new_level:
            conv.level = new_level
            conv.state = STATE_ASK_TOPIC
            label = MATH_TOPICS[new_level]["label"]
            return {
                "message": (
                    f"**{label}** 과정으로 변경했어요! 📝\n"
                    f"어떤 주제를 공부하고 싶으세요?"
                )
            }

        # Check for new topics
        new_topics = self._extract_topics(conv.level, msg_lower)
        if not new_topics:
            cleaned = re.sub(r'[^\w\s가-힣]', '', msg_raw).strip()
            if len(cleaned) >= 2:
                new_topics = [cleaned]

        if new_topics:
            conv.topics = new_topics
            keywords = self._generate_keywords(conv)
            topics_str = ", ".join(new_topics)
            return {
                "message": (
                    f"**{topics_str}** 관련 영상도 찾아볼게요! 🔍\n"
                    f"아래 결과를 확인해주세요."
                ),
                "recommendations": {
                    "level": conv.level,
                    "topics": conv.topics,
                    "difficulty": conv.difficulty,
                },
                "search_keywords": keywords,
            }

        # General response
        return {
            "message": (
                "다른 주제를 검색하고 싶으시면 주제를 말씀해주세요! 😊\n"
                "예: '미적분 기초', '이차함수 심화', '확률과 통계' 등\n\n"
                "재생목록에 영상을 추가하시면 나중에 한꺼번에 볼 수 있어요!"
            )
        }

    def _handle_free_chat(self, conv: ConversationState, msg_lower: str, msg_raw: str) -> dict:
        conv.state = STATE_ASK_LEVEL
        return self.get_greeting(conv.session_id)

    # ── detection helpers ─────────────────────

    def _detect_level(self, msg: str) -> str | None:
        for level, keywords in LEVEL_KEYWORDS.items():
            for kw in keywords:
                if kw in msg:
                    return level
        return None

    def _detect_difficulty(self, msg: str) -> str | None:
        for diff, keywords in DIFFICULTY_KEYWORDS.items():
            for kw in keywords:
                if kw in msg:
                    return diff
        return None

    def _extract_topics(self, level: str | None, msg: str) -> list[str]:
        if level is None:
            level = "high"

        topics_db = MATH_TOPICS.get(level, MATH_TOPICS["high"])["topics"]
        found = []
        for topic in topics_db:
            if topic.lower() in msg:
                found.append(topic)

        if "전체" in msg or "전부" in msg or "다" == msg.strip():
            found = topics_db[:3]

        return found

    def _generate_keywords(self, conv: ConversationState) -> list[str]:
        """Generate YouTube/EBS search keywords from conversation state."""
        keywords = []
        level_label = MATH_TOPICS.get(conv.level, {}).get("label", "수학")
        diff_map = {"beginner": "기초 개념", "intermediate": "문제풀이", "advanced": "심화 고난도"}
        diff_label = diff_map.get(conv.difficulty, "")

        for topic in conv.topics:
            keywords.append(f"{level_label} {topic} {diff_label} 강의".strip())
            keywords.append(f"{topic} {diff_label} 설명".strip())

        if conv.level == "suneung":
            for topic in conv.topics:
                keywords.append(f"수능 {topic} 기출 풀이")

        if not keywords:
            keywords.append(f"{level_label} {diff_label} 강의")

        return keywords


# Singleton
chat_engine = ChatEngine()
