from pydantic import BaseModel
from typing import Optional, List

class EBSRecommendRequest(BaseModel):
    level: Optional[str] = None
    topics: Optional[List[str]] = None
    difficulty: Optional[str] = None
    limit: int = 6

class EBSCourse(BaseModel):
    id: str
    title: str
    teacher: str
    level: str
    subject: str
    series: str
    difficulty: str
    topics: List[str]
    description: str
    url: str
    thumbnail: str
    lectures: int
    rating: float

class EBSListResponse(BaseModel):
    courses: List[EBSCourse]
