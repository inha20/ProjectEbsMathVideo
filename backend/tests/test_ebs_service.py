import pytest
from app.services.ebs_service import EBSService

@pytest.fixture
def ebs_service():
    service = EBSService()
    # Mock data directly for tests to avoid relying on fs
    service.courses = [
        {"id": "c1", "level": "high", "difficulty": "advanced", "topics": ["수학I"], "title": "고급 수학I"},
        {"id": "c2", "level": "middle", "difficulty": "beginner", "topics": ["일차방정식"], "title": "기초 일차방정식"},
    ]
    return service

def test_recommend_exact_match(ebs_service):
    res = ebs_service.recommend(level="high", difficulty="advanced", list=["수학I"])
    assert len(res) > 0
    assert res[0]["id"] == "c1"

def test_search(ebs_service):
    res = ebs_service.search("기초 일차")
    assert len(res) == 1
    assert res[0]["id"] == "c2"
