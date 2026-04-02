from fastapi import APIRouter, Depends
from typing import Optional
from app.schemas.ebs import EBSRecommendRequest, EBSListResponse
from app.services.ebs_service import EBSService

router = APIRouter(prefix="/api/ebs", tags=["ebs"])

def get_ebs_service() -> EBSService:
    return EBSService()

@router.post("/recommend", response_model=EBSListResponse)
def ebs_recommend(req: EBSRecommendRequest, ebs_service: EBSService = Depends(get_ebs_service)):
    courses = ebs_service.recommend(req.level, req.topics, req.difficulty, req.limit)
    return {"courses": courses}

@router.get("/courses", response_model=EBSListResponse)
def ebs_all_courses(level: Optional[str] = None, ebs_service: EBSService = Depends(get_ebs_service)):
    return {"courses": ebs_service.get_all(level)}

@router.get("/search", response_model=EBSListResponse)
def ebs_search(q: str, ebs_service: EBSService = Depends(get_ebs_service)):
    return {"courses": ebs_service.search(q)}
