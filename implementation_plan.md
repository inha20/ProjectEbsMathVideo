# ProjectEbsMathVideo 기술 면접 수준 개선 계획

## 현재 프로젝트 수준 평가: **중하**

현재 프로젝트는 "동작하는 프로토타입" 수준이며, 기술 면접에서 깊이 있는 질문에 대응하기 어려운 구조입니다.

---

## 1. 문제 정의 재설계

### 현재 문제점
- "수학 영상 추천"이라는 목표는 있으나, **왜 기존 YouTube/EBS 검색으로 부족한지** 설명 불가
- 타겟 사용자의 Pain Point가 불명확

### 재정의
| 항목 | 내용 |
|------|------|
| **타겟 사용자** | 중·고등학생, 수능 준비생 (자기주도 학습자) |
| **핵심 문제** | "내 수준에 맞는 수학 강의를 찾는 데 시간이 너무 오래 걸린다" |
| **사용 시나리오** | AI 대화 → 수준 파악 → YouTube+EBS 통합 추천 → 학습 플레이리스트 관리 |
| **차별점** | ① YouTube+EBS 통합 검색 ② 대화 기반 수준 진단 ③ 큐레이션된 재생목록 |

---

## 2. 시스템 아키텍처 재설계

### 현재 문제점
- `main.py`에 라우터 + 비즈니스 로직 + 인메모리 저장소가 혼재 (God Object)
- Service 클래스가 Singleton 전역 변수로 존재 (테스트 불가)
- DB 모델(`models.py`)을 정의했으나 실제 사용하지 않음 (인메모리 dict 사용)
- Controller/Service/Repository 계층 분리 없음

### 개선 아키텍처

```
[Frontend] → HTTP → [Router Layer] → [Service Layer] → [Repository Layer] → [SQLite DB]
                          │                  │
                     Pydantic DTO      비즈니스 로직
                     입력 검증         (ChatEngine, EBS추천, YouTube검색)
```

### 개선할 파일 구조
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 팩토리
│   ├── config.py             # [NEW] 설정 관리
│   ├── dependencies.py       # [NEW] DI 의존성
│   ├── routers/              # [NEW] Controller 계층
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── youtube.py
│   │   ├── ebs.py
│   │   └── playlist.py
│   ├── services/             # [NEW] Service 계층
│   │   ├── __init__.py
│   │   ├── chat_service.py
│   │   ├── youtube_service.py
│   │   ├── ebs_service.py
│   │   └── playlist_service.py
│   ├── repositories/         # [NEW] Repository 계층
│   │   ├── __init__.py
│   │   ├── chat_repository.py
│   │   └── playlist_repository.py
│   ├── models/               # DB 모델
│   │   ├── __init__.py
│   │   └── database.py
│   └── schemas/              # [NEW] Pydantic DTO
│       ├── __init__.py
│       ├── chat.py
│       ├── youtube.py
│       ├── ebs.py
│       └── playlist.py
├── tests/                    # [NEW] 테스트
│   ├── __init__.py
│   ├── test_chat_service.py
│   ├── test_ebs_service.py
│   └── test_playlist_service.py
├── data/
│   └── ebs_courses.json
└── requirements.txt
```

---

## 3. 데이터 수집 및 모델링 개선

### 현재 문제점
- YouTube: 하드코딩된 MOCK_VIDEOS (200줄+) — 실데이터가 아닌 가짜 데이터
- EBS: 정적 JSON 파일 (15개 강좌) — 업데이트 메커니즘 없음
- DB 모델 정의만 있고 실제 CRUD 미구현

### 개선 테이블 설계

| 테이블 | 필드 | 타입 | 설명 |
|--------|------|------|------|
| `chat_sessions` | id | INTEGER PK | 자동증가 |
| | session_id | VARCHAR(64) UNIQUE | UUID |
| | student_level | VARCHAR(32) | middle/high/suneung |
| | topics | JSON | 관심 주제 배열 |
| | difficulty | VARCHAR(32) | beginner/intermediate/advanced |
| | created_at | DATETIME | 생성일시 |
| `chat_messages` | id | INTEGER PK | 자동증가 |
| | session_id | VARCHAR(64) FK | 세션 참조 |
| | role | VARCHAR(16) | user/assistant |
| | content | TEXT | 메시지 내용 |
| | created_at | DATETIME | 생성일시 |
| `playlist_items` | id | INTEGER PK | 자동증가 |
| | session_id | VARCHAR(64) INDEX | 세션 참조 |
| | video_id | VARCHAR(64) | 영상 고유 ID |
| | title | VARCHAR(512) | 영상 제목 |
| | channel | VARCHAR(256) | 채널명 |
| | thumbnail | VARCHAR(512) | 썸네일 URL |
| | source | VARCHAR(16) | youtube/ebs |
| | url | VARCHAR(512) | 영상 URL |
| | added_at | DATETIME | 추가일시 |
| `search_logs` | id | INTEGER PK | [NEW] 검색 로그 |
| | session_id | VARCHAR(64) | 세션 참조 |
| | query | VARCHAR(512) | 검색어 |
| | result_count | INTEGER | 결과 수 |
| | created_at | DATETIME | 검색일시 |

---

## 4. 검색 기능 고도화

### 현재 한계
- EBS: 단순 `if query_lower in searchable` 부분 문자열 매칭
- YouTube: Mock 데이터에서 key 매칭만 수행
- 동의어, 유사어, 오타 처리 없음

### 개선 방안
- **EBS 검색**: TF-IDF 기반 점수 계산 + 한국어 형태소 분석(초성 검색)
- **YouTube**: API 호출 시 `relevanceLanguage`, `videoCategoryId` 파라미터 활용
- **검색 로그 기반**: 인기 검색어 자동 제안

---

## 5. 성능 및 확장성 개선

### 현재 문제점
- 인메모리 `playlists: dict` → 서버 재시작 시 데이터 소실
- YouTube API 호출 시 Rate Limit 처리 없음
- EBS 데이터 매 요청마다 JSON 파싱 (메모리에 캐시되긴 함)
- Pagination 없음

### 개선 항목
| 항목 | 현재 | 개선 |
|------|------|------|
| 재생목록 저장 | 인메모리 dict | SQLite Repository |
| Pagination | 없음 | offset/limit 기반 |
| 캐싱 | 없음 | LRU 캐시 (functools) |
| DB 인덱스 | session_id만 | composite index 추가 |
| API Rate Limit | 없음 | httpx retry + exponential backoff |

---

## 6. 코드 품질 개선 핵심 포인트

| 문제 | 위치 | 개선 |
|------|------|------|
| God Object | `main.py` | Router 분리 |
| 전역 Singleton | `chat_engine = ChatEngine()` | FastAPI Depends DI |
| DB 미사용 | `playlists: dict` | Repository 패턴 |
| 하드코딩 Mock 200줄 | `youtube_service.py` | 별도 JSON 파일 분리 |
| 에러 핸들링 없음 | 전체 | 글로벌 예외 핸들러 |
| 타입 힌트 불완전 | Service 반환값 | Pydantic 스키마 |
| 로깅 없음 | 전체 | `logging` 모듈 도입 |

---

## 7. 실행 순서 (파일 출력 순서)

### Phase 1: 백엔드 기반 구조
1. `backend/app/config.py` — 설정 관리
2. `backend/app/models/database.py` — DB 연결 + 모델
3. `backend/app/schemas/` — Pydantic 스키마 (chat, youtube, ebs, playlist)
4. `backend/app/repositories/` — Repository 계층
5. `backend/app/services/` — Service 계층 (chat, youtube, ebs, playlist)
6. `backend/app/routers/` — Router 계층
7. `backend/app/dependencies.py` — DI
8. `backend/app/main.py` — 앱 팩토리

### Phase 2: 테스트
9. `backend/tests/test_chat_service.py`
10. `backend/tests/test_ebs_service.py`
11. `backend/tests/test_playlist_service.py`

### Phase 3: 프론트엔드 개선 (구조 유지, API 호환)
12. 프론트엔드는 API 엔드포인트가 동일하므로 변경 불필요

### Phase 4: 문서화
13. `README.md` — 개선된 문서
14. `docs/INTERVIEW_QA.md` — 면접 대비 Q&A
15. `docs/ARCHITECTURE.md` — 아키텍처 문서

---

## 검증 계획
- `pytest` 로 Unit/Integration 테스트 실행
- `uvicorn` 서버 기동 후 `/docs` Swagger 확인
- 기존 프론트엔드와 호환성 확인
