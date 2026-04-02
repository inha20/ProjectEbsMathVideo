# 📐 ProjectEbsMathVideo

**AI 대화 기반 수학 영상 추천 시스템** — YouTube & EBS 강좌를 한 곳에서!

## 🎯 소개

학생과 AI의 대화를 통해 학습 수준과 필요를 파악하고, 맞춤형 **YouTube 수학 강의**와 **EBS 강좌**를 추천하는 웹 애플리케이션입니다.

### 주요 기능
- 🤖 **AI 채팅** — 대화를 통해 학습 수준·주제·난이도를 파악
- ▶️ **YouTube 영상 검색** — 맞춤 수학 강의 영상 검색
- 📚 **EBS 강좌 추천** — EBSi 수학 강좌 수준별 추천
- 📋 **재생목록 관리** — 영상 저장, 내보내기, 연속 재생

## 🚀 실행 방법

### 간편 실행
```
start.bat 더블클릭
```

### 수동 실행

**1. 백엔드 서버**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**2. 프론트엔드 서버**
```bash
cd frontend
python -m http.server 3000
```

**3. 브라우저에서 접속**
```
http://localhost:3000
```

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | HTML + CSS + Vanilla JavaScript |
| Backend | Python FastAPI |
| Database | SQLite (SQLAlchemy) |
| AI Chat | 규칙 기반 상태 머신 |
| YouTube | YouTube Data API v3 (모의 데이터 지원) |
| EBS | 내장 JSON 데이터베이스 |

## 📁 프로젝트 구조

```
ProjectEbsMathVideo/
├── backend/
│   ├── main.py              # FastAPI 앱
│   ├── chat_engine.py       # AI 챗봇 엔진
│   ├── youtube_service.py   # YouTube 검색
│   ├── ebs_service.py       # EBS 추천
│   ├── models.py            # DB 모델
│   ├── database.py          # DB 연결
│   ├── requirements.txt
│   └── data/
│       └── ebs_courses.json # EBS 강좌 데이터
├── frontend/
│   ├── index.html           # 메인 페이지
│   ├── style.css            # 스타일링
│   ├── main.js              # 앱 컨트롤러
│   ├── chat.js              # 채팅 UI
│   ├── youtube.js           # YouTube 모듈
│   └── ebs.js               # EBS 모듈
├── start.bat                # 원클릭 실행
└── README.md
```

## 🔑 YouTube API 키 설정 (선택)

실제 YouTube 검색을 사용하려면:

1. [Google Cloud Console](https://console.cloud.google.com)에서 프로젝트 생성
2. YouTube Data API v3 활성화
3. API 키 발급
4. `backend/.env` 파일 생성:
```
YOUTUBE_API_KEY=your_api_key_here
```

> API 키 없이도 모의 데이터로 정상 동작합니다.

## 📝 라이선스

MIT License
