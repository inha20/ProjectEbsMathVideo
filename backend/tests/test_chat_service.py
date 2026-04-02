import pytest
from app.services.chat_service import ChatService
from app.repositories.chat_repository import ChatRepository
from app.models.domain import ChatSession

class MockChatRepository:
    def __init__(self):
        self.sessions = {}
        self.messages = []

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def create_session(self):
        session = ChatSession(session_id="test_session", student_level="unknown", topics=[])
        self.sessions[session.session_id] = session
        return session

    def update_session(self, session):
        self.sessions[session.session_id] = session
        return session

    def add_message(self, session_id, role, content):
        self.messages.append({"session_id": session_id, "role": role, "content": content})
        return True

@pytest.fixture
def chat_service():
    repo = MockChatRepository()
    return ChatService(repo)

def test_start_session(chat_service):
    res = chat_service.start_session()
    assert "test_session" == res["session_id"]
    assert "state" in res
    assert res["state"]["state"] == "ask_level"

def test_process_message_level(chat_service):
    chat_service.start_session()
    res = chat_service.process_message("test_session", "중학생입니다")
    assert "중학교 수학" in res["message"]
    assert res["state"]["state"] == "ask_topic"
    assert res["state"]["level"] == "middle"

def test_process_message_topic(chat_service):
    chat_service.start_session()
    chat_service.process_message("test_session", "중학생입니다")
    res = chat_service.process_message("test_session", "이차함수 어려워요")
    assert "이차함수" in res["message"]
    assert res["state"]["state"] == "ask_difficulty"
    assert "이차함수" in res["state"]["topics"]
