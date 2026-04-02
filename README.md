# 📐 ProjectEbsMathVideo

**AI 대화 기반 맞춤형 수학 교육 영상 큐레이팅 플랫폼**

학생과 AI의 대화를 통해 수준(학년), 취약 단원, 학습 난이도를 정밀하게 분석하여 **YouTube 강의**와 **EBS 강좌** 중 가장 적합한 영상을 인공지능 기반으로 큐레이팅하는 웹 서비스입니다. 
비즈니스 로직과 데이터 검증이 분리된 유지보수성 높은 Controller-Service-Repository 계층형 아키텍처로 구성된 프로덕션 준비 애플리케이션입니다.

## 🎯 핵심 기능 및 가치

- 🤖 **AI 채팅 진단 머신** — 규칙 기반 상태 머신(State Machine)을 통해 자연스러운 대화로 학생의 레벨과 취약점 진단
- ▶️ **YouTube 영상 통합 큐레이션** — Async I/O 기반 YouTube Data API를 통해 최적화된 강의 영상 고속 검색 (장애 대비 Mock Fallback 지원)
- 📚 **EBS 강좌 맞춤 추천** — 자체 개발한 휴리스틱 채점 알고리즘(Scoring Algorithm) 기반으로 일치하는 수준별 EBSi 강좌 제공
- 📋 **개인화된 플레이리스트 플랫폼** — SQLite RDBMS 기반으로 사용자별 플레이리스트 영구 보존 및 연속 재생 제공

## 🛠️ 기술 스택 (Tech Stack)

| 계층 | 기술 |
|------|------|
| **Frontend** | HTML5, CSS3 (Premium Dark UI), Vanilla JS |
| **Backend Framework** | Python 3.10+, FastAPI, Uvicorn |
| **Database & ORM** | SQLite, SQLAlchemy, Pydantic |
| **Architecture** | 3-Tier Layered Architecture (Controller-Service-Repository) |
| **External API & Testing**| YouTube Data API v3 (httpx), pytest |

## 🚀 실행 가이드

### 1단계: 필수 구성요소 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2단계: API 키 설정 (선택적)
`backend/.env` 파일을 만들고 YouTube API를 기입하세요. 미기입시 자동으로 Mock 데모 데이터로 동작합니다.
```env
YOUTUBE_API_KEY=당신의_유튜브_발급_키
```

### 3단계: 애플리케이션 실행
백엔드 서버 켜기 (새 터미널 환경):
```bash
cd backend
python main.py
# http://localhost:8000/docs 에서 API 테스팅 가능
```

프론트엔드 서버 켜기 (새 터미널 환경):
```bash
cd frontend
python -m http.server 3000
# http://localhost:3000 접속 시작
```

## 📁 디렉토리 구조 및 아키텍처

기술 면접을 대비한 아키텍처 가이드와 예상 질문은 다음 문서들을 참고하세요:
- [📖시스템 아키텍처 가이드](./docs/ARCHITECTURE.md)
- [🎤기술 면접 Q&A](./docs/INTERVIEW_QA.md)

```text
ProjectEbsMathVideo/
├── backend/
│   ├── app/
│   │   ├── routers/       # Controller 계층 (요청/응답/라우팅)
│   │   ├── services/      # Service 계층 (비즈니스/채점 로직)
│   │   ├── repositories/  # Repository 계층 (DB 읽기/쓰기 캡슐화)
│   │   ├── schemas/       # DTO 계층 (Pydantic 모델)
│   │   ├── models/        # SQLAlchemy DB 모델 매핑
│   │   ├── main.py        # FastAPI 앱 초기화
│   │   └── config.py      # 환경 변수 로딩
│   ├── tests/             # Pytest 유닛테스트
│   ├── data/              # EBS 데이터 및 SQLite DB
│   └── main.py            # Uvicorn 진입점 프록시
├── docs/                  # 프로젝트 가이드 문서
└── frontend/              # View 통합단 (JS/CSS/HTML)
```

## 📝 소프트웨어 라이선스
MIT License
