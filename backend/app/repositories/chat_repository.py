from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from app.models.domain import ChatSession, ChatMessage
import uuid

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    def create_session(self) -> ChatSession:
        new_session = ChatSession(session_id=str(uuid.uuid4()))
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def update_session(self, session: ChatSession):
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        return self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .limit(limit).all()
