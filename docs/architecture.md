# EBS 수학 영상 학습 추천 시스템 — 시스템 아키텍처

## 전체 구조

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ AI 채팅  │  │ 영상검색 │  │ 재생목록 │  │ 대시보드 │    │
│  │   View   │  │   View   │  │   View   │  │   View   │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └──────────────┴──────────────┴──────────────┘         │
│                         REST API                             │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────────┐
│                       SERVER LAYER (FastAPI)                  │
│                                                              │
│  ┌─────────────────── ROUTER LAYER ────────────────────┐    │
│  │ chat.py │ videos.py │ playlists.py │ users.py       │    │
│  └────┬────┴─────┬─────┴──────┬───────┴────┬───────────┘    │
│       │          │            │            │                 │
│  ┌────┴──────────┴────────────┴────────────┴────────────┐   │
│  │              SERVICE LAYER                            │   │
│  │ ChatService │ RecommendationService │ PlaylistService │   │
│  │ YouTubeService │ EBSService                           │   │
│  └────┬──────────┬────────────┬────────────┬────────────┘   │
│       │          │            │            │                 │
│  ┌────┴──────────┴────────────┴────────────┴────────────┐   │
│  │              DATA LAYER                               │   │
│  │ SQLAlchemy ORM │ models.py │ database.py              │   │
│  └──────────────────────┬────────────────────────────────┘   │
└─────────────────────────┼────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
     ┌────┴────┐   ┌──────┴─────┐  ┌─────┴─────┐
     │ SQLite  │   │ OpenAI API │  │ YouTube   │
     │   DB    │   │  (GPT)     │  │ Data API  │
     └─────────┘   └────────────┘  └───────────┘
```

## 추천 엔진 흐름

```
학생 메시지 입력
       │
       ▼
  ┌─────────────┐
  │ ChatService │ ─── OpenAI API (or Fallback)
  │ NLP 파싱    │
  └──────┬──────┘
         │ {grade, topic, difficulty}
         ▼
  ┌──────────────────────┐
  │ RecommendationService│
  ├──────────────────────┤
  │ 1. Rule-based        │ → EBS 필터링 + YouTube 검색
  │ 2. Score-based       │ → 퀴즈 점수 < 70 → 취약 단원 보강
  │ 3. Continue-watching │ → 미완료 영상 이어보기
  └──────────┬───────────┘
             │
             ▼
  추천 결과 (영상 + 추천 사유)
```

## 기술 스택

| Layer | Technology |
|---|---|
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Backend | Python 3.11+ / FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) → PostgreSQL (prod) |
| AI | OpenAI GPT-3.5 |
| Video API | YouTube Data API v3 |
| Auth | JWT (python-jose) |
| Password | bcrypt (passlib) |
