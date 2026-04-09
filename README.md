# ProjectEbsMathVideo

## 📐 EBS 수학 영상 학습 추천 시스템

학생과 AI의 대화를 통해 학생에게 필요한 **유튜브 영상 링크**와 **EBS 영상 링크**를 불러오는 프로그램입니다.
**유튜브 재생목록 만들기**와 **EBS 강좌 추천** 기능을 제공합니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 🤖 **AI 학습 도우미** | OpenAI 기반 챗봇이 대화를 통해 학년/단원/난이도를 파악하여 맞춤 영상 추천 |
| 🔍 **통합 영상 검색** | EBS + YouTube에서 수학 강의를 학년/난이도별로 검색 |
| 📋 **재생목록 관리** | 개인 재생목록 생성/편집/삭제 (CRUD) |
| 📊 **학습 대시보드** | 시청 기록, 진도율, 퀴즈 점수, 취약 단원 분석 |
| 🎯 **추천 엔진** | Rule-based + Score-based 하이브리드 추천 |
| 📌 **이어보기** | 시청 중단 위치 저장 및 이어보기 |

---

## ⚙️ 기술 스택

| 영역 | 기술 |
|---|---|
| Backend | Python 3.11+ / FastAPI / SQLAlchemy |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Database | SQLite (dev) → PostgreSQL (prod) |
| AI | OpenAI GPT-3.5 Turbo |
| Video API | YouTube Data API v3 |
| Auth | JWT (python-jose + bcrypt) |

---

## 🚀 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 API 키를 입력하세요
```

> ⚠️ API 키가 없어도 데모 모드로 동작합니다 (Fallback 챗봇 + 샘플 영상 데이터)

### 3. 서버 실행
```bash
python main.py
```

### 4. 접속
- **웹 UI**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **데모 계정**: `demo_student` / `1234`

---

## 📁 프로젝트 구조

```
ProjectEbsMathVideo/
├── main.py                  # FastAPI 앱 진입점
├── config.py                # 환경 변수 설정
├── database.py              # DB 엔진/세션
├── models.py                # ORM 모델 (User, Video, Progress, Playlist)
├── schemas.py               # Pydantic 스키마
├── services/
│   ├── chat_service.py      # AI 챗봇 (OpenAI + Fallback)
│   ├── youtube_service.py   # YouTube API 연동
│   ├── ebs_service.py       # EBS 영상 데이터 관리
│   ├── recommendation_service.py  # 추천 엔진
│   └── playlist_service.py  # 재생목록 CRUD
├── routers/
│   ├── chat.py              # /api/chat 엔드포인트
│   ├── videos.py            # /api/videos 엔드포인트
│   ├── playlists.py         # /api/playlists 엔드포인트
│   └── users.py             # /api/users 엔드포인트
├── templates/
│   └── index.html           # 메인 페이지
├── static/
│   ├── css/style.css        # 프리미엄 다크 테마
│   └── js/app.js            # 프론트엔드 로직
├── data/
│   └── ebs_math_videos.json # EBS 영상 시드 데이터
├── tests/
│   └── test_recommendation.py  # 추천 엔진 테스트
├── docs/
│   ├── analysis.md          # 프로젝트 분석 보고서 (11개 섹션)
│   ├── architecture.md      # 시스템 아키텍처
│   └── api_docs.md          # REST API 명세
└── requirements.txt
```

---

## 🏗️ 시스템 아키텍처

```
[Client: HTML/CSS/JS] → [FastAPI Server] → [SQLite DB]
                                        → [OpenAI API]
                                        → [YouTube Data API]
```

### 추천 엔진 흐름
```
학생 채팅 → AI가 학년/단원/난이도 추출
          → Rule-based: EBS 필터링 + YouTube 검색
          → Score-based: 퀴즈 점수 기반 취약 단원 보강
          → 추천 사유와 함께 결과 반환
```

---

## 📖 문서

- [프로젝트 분석 보고서](docs/analysis.md) — 11개 섹션 분석 + 면접 Q&A 10개
- [시스템 아키텍처](docs/architecture.md) — 전체 구조도
- [REST API 명세](docs/api_docs.md) — 엔드포인트 목록

---

## 🧪 테스트

```bash
python -m pytest tests/ -v
```

---

## 📄 라이선스

MIT License
