# REST API 명세

Base URL: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

---

## 채팅 API

### POST /api/chat/
AI 대화 + 영상 추천

**Request:**
```json
{
    "message": "중학교 2학년인데 일차함수가 어려워요",
    "history": [
        {"role": "user", "content": "안녕"},
        {"role": "assistant", "content": "안녕하세요!"}
    ]
}
```

**Response:**
```json
{
    "reply": "중2 학생이시군요! 일차함수 관련 영상을 추천해 드릴게요.",
    "recommended_videos": [
        {
            "title": "[EBS 중2] 일차함수 - 기초",
            "url": "https://www.ebsi.co.kr/...",
            "source": "ebs",
            "topic": "일차함수",
            "difficulty": "easy",
            "reason": "중2 교과 과정 | '일차함수' 단원 매칭"
        }
    ],
    "extracted_info": {
        "grade": "중2",
        "topic": "일차함수",
        "difficulty": "medium"
    }
}
```

---

## 영상 API

### POST /api/videos/search
통합 영상 검색

**Request:**
```json
{
    "query": "일차함수",
    "grade": "중2",
    "difficulty": "easy",
    "source": "all",
    "max_results": 10
}
```

### GET /api/videos/topics?grade=중2
학년별 단원 목록

### POST /api/videos/recommendations
맞춤 추천

### POST /api/videos/progress
학습 진도 저장

### GET /api/videos/dashboard/{user_id}
학습 대시보드

---

## 재생목록 API

### POST /api/playlists/
재생목록 생성

### GET /api/playlists/
내 재생목록 조회

### GET /api/playlists/{id}
재생목록 상세

### POST /api/playlists/{id}/videos
영상 추가

### DELETE /api/playlists/{id}/videos/{video_id}
영상 제거

### DELETE /api/playlists/{id}
재생목록 삭제

---

## 사용자 API

### POST /api/users/register
회원가입

### POST /api/users/login
로그인 (JWT 발급)

### GET /api/users/me
현재 사용자 정보
