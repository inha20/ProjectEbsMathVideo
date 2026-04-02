import re
from typing import Dict, Any, Tuple
from app.repositories.chat_repository import ChatRepository

# Constants
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

LEVEL_KEYWORDS = {
    "middle": ["중학", "중1", "중2", "중3", "중등"],
    "high": ["고등", "고1", "고2", "고3", "고등학교"],
    "suneung": ["수능", "수특", "수완", "ebs", "모의고사", "대입", "입시", "n수생"]
}

DIFFICULTY_KEYWORDS = {
    "beginner": ["기초", "처음", "쉬운", "입문", "기본", "개념", "못해", "어려워", "모르"],
    "intermediate": ["보통", "중간", "복습", "다시", "심화 전"],
    "advanced": ["심화", "어려운", "킬러", "고난도", "4점", "만점", "상위권"]
}

STATE_GREETING = "greeting"
STATE_ASK_LEVEL = "ask_level"
STATE_ASK_TOPIC = "ask_topic"
STATE_ASK_DIFFICULTY = "ask_difficulty"
STATE_RECOMMEND = "recommend"

class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    def start_session(self) -> Dict[str, Any]:
        session = self.repo.create_session()
        msg = (
            "안녕하세요! 🎓 수학 영상 추천 도우미입니다.\n\n"
            "저와 대화하면서 딱 맞는 수학 강의 영상을 찾아드릴게요.\n"
            "먼저, 현재 학년이 어떻게 되시나요?\n\n"
            "• 중학생 (중1~중3)\n"
            "• 고등학생 (고1~고3)\n"
            "• 수능 준비생"
        )
        self.repo.add_message(session.session_id, "assistant", msg)
        
        return {
            "session_id": session.session_id,
            "message": msg,
            "state": {
                "session_id": session.session_id,
                "state": STATE_ASK_LEVEL,
                "level": session.student_level,
                "topics": session.topics,
                "difficulty": session.difficulty
            }
        }

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        session = self.repo.get_session(session_id)
        if not session:
            # Recreate or error
            return self.start_session()
        
        self.repo.add_message(session_id, "user", message)
        
        # Determine internal state based on DB fields
        if session.student_level == "unknown" or not session.student_level:
            internal_state = STATE_ASK_LEVEL
        elif not session.topics:
            internal_state = STATE_ASK_TOPIC
        elif not session.difficulty:
            internal_state = STATE_ASK_DIFFICULTY
        else:
            internal_state = STATE_RECOMMEND

        msg_lower = message.strip().lower()
        response_dict = {}

        if internal_state == STATE_ASK_LEVEL:
            response_dict = self._handle_level(session, msg_lower)
        elif internal_state == STATE_ASK_TOPIC:
            response_dict = self._handle_topic(session, msg_lower, message)
        elif internal_state == STATE_ASK_DIFFICULTY:
            response_dict = self._handle_difficulty(session, msg_lower)
        else:
            response_dict = self._handle_recommend(session, msg_lower, message)

        self.repo.update_session(session)
        self.repo.add_message(session_id, "assistant", response_dict["message"])
        
        # Add state
        response_dict["state"] = {
            "session_id": session.session_id,
            "state": "recommend" if session.difficulty else ("ask_difficulty" if session.topics else ("ask_topic" if session.student_level != "unknown" else "ask_level")),
            "level": session.student_level,
            "topics": session.topics,
            "difficulty": session.difficulty
        }
        response_dict["session_id"] = session_id

        return response_dict

    def _handle_level(self, session, msg_lower: str) -> Dict[str, Any]:
        detected = self._detect_level(msg_lower)
        if detected:
            session.student_level = detected
            label = MATH_TOPICS[detected]["label"]
            topics_str = ", ".join(MATH_TOPICS[detected]["topics"][:8])
            return {
                "message": f"**{label}** 과정이시군요! 👍\n\n어떤 단원이 어렵거나, 공부하고 싶은 주제가 있나요?\n예시: {topics_str}\n\n자유롭게 말씀해주세요!"
            }
        else:
            return {
                "message": "죄송해요, 학년을 잘 이해하지 못했어요. 😅\n아래 중 하나를 선택해주세요:\n\n• **중학생** (중1~중3)\n• **고등학생** (고1~고3)\n• **수능 준비생**"
            }

    def _handle_topic(self, session, msg_lower: str, msg_raw: str) -> Dict[str, Any]:
        topics = self._extract_topics(session.student_level, msg_lower)
        if not topics:
            cleaned = re.sub(r'[^\w\s가-힣]', '', msg_raw).strip()
            if len(cleaned) >= 2:
                topics = [cleaned]
        
        if topics:
            session.topics = topics
            topics_str = ", ".join(topics)
            return {
                "message": f"**{topics_str}** 관련해서 찾아드릴게요! 📚\n\n실력 수준은 어느 정도인가요?\n\n• 🌱 **기초** - 개념부터 차근차근\n• 🌿 **중급** - 개념은 알지만 문제풀이 연습\n• 🌳 **심화** - 고난도 문제 도전"
            }
        else:
            topic_list = MATH_TOPICS.get(session.student_level, MATH_TOPICS["high"])["topics"]
            return {
                "message": f"어떤 주제를 공부하고 싶은지 좀 더 구체적으로 알려주세요! 🤔\n\n예시: {', '.join(topic_list[:6])}\n\n또는 '전체' 라고 하시면 전반적인 영상을 추천해드릴게요."
            }

    def _handle_difficulty(self, session, msg_lower: str) -> Dict[str, Any]:
        difficulty = self._detect_difficulty(msg_lower) or "intermediate"
        session.difficulty = difficulty

        keywords = self._generate_keywords(session)
        level_label = MATH_TOPICS.get(session.student_level, {}).get("label", "수학")
        topics_str = ", ".join(session.topics) if session.topics else "전체"
        diff_labels = {"beginner": "기초", "intermediate": "중급", "advanced": "심화"}
        
        return {
            "message": f"완벽해요! 맞춤 영상을 찾아볼게요 🔍\n\n📋 **분석 결과:**\n• 과정: {level_label}\n• 주제: {topics_str}\n• 수준: {diff_labels.get(difficulty)}\n\n아래에서 추천 영상을 확인해보세요!",
            "recommendations": {
                "level": session.student_level,
                "topics": session.topics,
                "difficulty": difficulty
            },
            "search_keywords": keywords
        }

    def _handle_recommend(self, session, msg_lower: str, msg_raw: str) -> Dict[str, Any]:
        new_level = self._detect_level(msg_lower)
        if new_level:
            session.student_level = new_level
            session.topics = []
            session.difficulty = None
            return {"message": f"**{MATH_TOPICS[new_level]['label']}** 과정으로 변경했어요! 📝\n어떤 주제를 공부하고 싶으세요?"}
            
        new_topics = self._extract_topics(session.student_level, msg_lower)
        if not new_topics:
            cleaned = re.sub(r'[^\w\s가-힣]', '', msg_raw).strip()
            if len(cleaned) >= 2:
                new_topics = [cleaned]
                
        if new_topics:
            session.topics = new_topics
            keywords = self._generate_keywords(session)
            return {
                "message": f"**{', '.join(new_topics)}** 관련 영상도 찾아볼게요! 🔍\n아래 결과를 확인해주세요.",
                "recommendations": {
                    "level": session.student_level,
                    "topics": session.topics,
                    "difficulty": session.difficulty
                },
                "search_keywords": keywords
            }

        return {
            "message": "다른 주제를 검색하고 싶으시면 주제를 말씀해주세요! 😊\n예: '미적분 기초', '이차함수 심화'\n\n재생목록에 영상을 추가하시면 나중에 한꺼번에 볼 수 있어요!"
        }

    def _detect_level(self, msg: str) -> Optional[str]:
        for level, keywords in LEVEL_KEYWORDS.items():
            if any(kw in msg for kw in keywords):
                return level
        return None

    def _detect_difficulty(self, msg: str) -> Optional[str]:
        for diff, keywords in DIFFICULTY_KEYWORDS.items():
            if any(kw in msg for kw in keywords):
                return diff
        return None

    def _extract_topics(self, level: str, msg: str) -> list[str]:
        topics_db = MATH_TOPICS.get(level, MATH_TOPICS["high"])["topics"]
        found = [topic for topic in topics_db if topic.lower() in msg]
        if any(w in msg for w in ["전체", "전부", "다"]):
            found = topics_db[:3]
        return found

    def _generate_keywords(self, session) -> list[str]:
        keywords = []
        level_label = MATH_TOPICS.get(session.student_level, {}).get("label", "수학")
        diff_map = {"beginner": "기초 개념", "intermediate": "문제풀이", "advanced": "심화 고난도"}
        diff_label = diff_map.get(session.difficulty, "")

        for topic in session.topics:
            keywords.append(f"{level_label} {topic} {diff_label} 강의".strip())
            keywords.append(f"{topic} {diff_label} 설명".strip())

        if session.student_level == "suneung":
            for topic in session.topics:
                keywords.append(f"수능 {topic} 기출 풀이")

        if not keywords:
            keywords.append(f"{level_label} {diff_label} 강의")

        return keywords
