from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

from app.repositories.chat_repository import ChatRepository
from app.services.chat_service import ChatService
from app.services.ebs_service import EBSService
from app.schemas.chat import ChatMessageRequest, ChatResponse, ChatStateResponse

def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    repo = ChatRepository(db)
    return ChatService(repo)

def get_ebs_service() -> EBSService:
    return EBSService()

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/start", response_model=ChatResponse)
def start_chat(chat_service: ChatService = Depends(get_chat_service)):
    """Start a new chat session."""
    return chat_service.start_session()

@router.post("/message", response_model=ChatResponse)
def send_message(req: ChatMessageRequest, chat_service: ChatService = Depends(get_chat_service), ebs_service: EBSService = Depends(get_ebs_service)):
    """Send a message in an existing chat."""
    if not req.session_id:
        raise HTTPException(status_code=400, detail="session_id required")
        
    result = chat_service.process_message(req.session_id, req.message)
    
    # Process recommendations if present
    rec = result.get("recommendations")
    if rec:
        result["ebs_courses"] = ebs_service.recommend(
            level=rec.get("level"),
            topics=rec.get("topics"),
            difficulty=rec.get("difficulty")
        )
        
    return result
