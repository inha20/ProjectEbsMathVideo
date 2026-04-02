from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatMessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatStateResponse(BaseModel):
    session_id: str
    state: str
    level: Optional[str] = None
    topics: List[str] = []
    difficulty: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    state: Optional[ChatStateResponse] = None
    recommendations: Optional[Dict[str, Any]] = None
    search_keywords: Optional[List[str]] = None
    ebs_courses: Optional[List[Dict[str, Any]]] = None
