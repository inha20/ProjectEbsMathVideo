from fastapi import APIRouter, Depends
from app.schemas.youtube import SearchRequest, SearchResponse
from app.services.youtube_service import YouTubeService

router = APIRouter(prefix="/api/youtube", tags=["youtube"])

def get_youtube_service() -> YouTubeService:
    return YouTubeService()

@router.post("/search", response_model=SearchResponse)
async def map_youtube_search(req: SearchRequest, youtube_service: YouTubeService = Depends(get_youtube_service)):
    """Search YouTube for math videos."""
    results = await youtube_service.search(req.query, req.max_results)
    return {
        "query": req.query,
        "results": results,
        "search_url": youtube_service.get_youtube_search_url(req.query)
    }
