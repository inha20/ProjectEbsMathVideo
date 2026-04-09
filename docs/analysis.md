# EBS 수학 영상 학습 추천 시스템 — 프로젝트 분석 보고서

> 10년차 백엔드 엔지니어 / 추천 시스템 전문가 / 기술 면접관 관점

---

## 1. 시스템 구조 분석

### 현재 아키텍처

```
[Client: HTML/CSS/JS]
        ↓ (REST API)
[Server: FastAPI + Jinja2]
        ↓ (ORM)
[Database: SQLite + SQLAlchemy]
        ↓ (External API)
[YouTube Data API v3 / EBS 데이터셋]
```

| 구분 | 설명 |
|---|---|
| **영상 데이터 처리** | EBS: JSON 시드 데이터 → DB 적재, YouTube: API 실시간 검색 |
| **사용자 입력** | 채팅 메시지 → NLP 파싱 → 학년/단원/난이도 추출 |
| **출력** | 추천 영상 리스트 (제목, URL, 추천 사유) |
| **UI → 로직 → 데이터** | Jinja2 → FastAPI Router → Service Layer → DB/API |

### 결론: **학습 시스템 구조**

- ~~단순 플레이어~~ → ❌
- 학습 시스템 구조 → ✅ (추천 엔진 + 학습 이력 + 취약 분석)

---

## 2. 코드 품질 분석

### 2.1 함수 책임 분리 (SRP)

| 항목 | 평가 | 설명 |
|---|---|---|
| Service Layer | ✅ 양호 | `ChatService`, `RecommendationService` 등 역할 분리 |
| Router Layer | ✅ 양호 | `/api/chat`, `/api/videos` 등 리소스 기반 분리 |
| Model Layer | ✅ 양호 | User, Video, Progress, Playlist 단일 책임 |

### 2.2 네이밍 일관성

- **패턴**: `snake_case` (Python 표준)
- **서비스**: `{도메인}_service.py` 일관 적용
- **라우터**: `{리소스}.py` 일관 적용

### 2.3 하드코딩 여부

| 문제 | 원인 | 개선 |
|---|---|---|
| `user_id=1` 하드코딩 | JWT 인증 미완성 | `Depends(get_current_user)` 의존성 주입 |
| 퀴즈 합격 기준 `70점` | 상수 미분리 | `config.py`에 `WEAK_TOPIC_THRESHOLD` 정의 |

### 2.4 모듈화 수준: **상**

```
main.py → routers/ → services/ → models.py + database.py
                                    ↑
                              config.py (설정 중앙화)
```

---

## 3. 영상 처리 로직 분석

| 기준 | 현재 상태 |
|---|---|
| 단순 리스트 출력 | ❌ 아님 |
| 조건 기반 필터링 | ✅ 학년/단원/난이도/소스 필터링 |
| 추천 로직 존재 | ✅ Rule-based + Score-based 하이브리드 |

### 추천 흐름

```
학생 채팅 → AI가 학년/단원/난이도 추출
          → RecommendationService.recommend_by_rules()
          → EBS 필터링 + YouTube API 검색
          → 추천 사유와 함께 결과 반환
```

---

## 4. 추천 시스템 설계

### ① Rule-based 추천

| 항목 | 내용 |
|---|---|
| **구현** | `recommend_by_rules(grade, topic, difficulty)` |
| **장점** | 구현 단순, Cold Start 문제 없음, 설명 가능 |
| **단점** | 개인화 불가, 학습 패턴 반영 불가 |

### ② Score-based 추천

| 항목 | 내용 |
|---|---|
| **구현** | `recommend_by_score(db, user_id)` — 퀴즈 점수 < 70 → 취약 단원 |
| **장점** | 사용자별 맞춤, 취약점 보강, 데이터 기반 |
| **단점** | 충분한 학습 데이터 필요 (Cold Start) |

### ③ AI 기반 추천 (확장)

| 항목 | 내용 |
|---|---|
| **구현 방향** | Collaborative Filtering / Content-based / 하이브리드 |
| **장점** | 학습 패턴 분석, 유사 학생 추천, 높은 정확도 |
| **단점** | 대량 데이터 필요, 복잡한 인프라, 설명 어려움 |

---

## 5. 데이터 구조 설계

### 관계형 구조 (현재 적용)

```
┌─────────┐     ┌──────────┐     ┌───────────┐
│  users  │──┬──│ progress │──┬──│  videos   │
│─────────│  │  │──────────│  │  │───────────│
│ id (PK) │  │  │ id (PK)  │  │  │ id (PK)   │
│ username│  │  │ user_id  │  │  │ title     │
│ grade   │  │  │ video_id │  │  │ url       │
│ pwd_hash│  │  │ score    │  │  │ source    │
└─────────┘  │  │ position │  │  │ topic     │
             │  └──────────┘  │  │ difficulty│
             │                │  └───────────┘
             │  ┌───────────┐ │
             └──│ playlists │ │  ┌────────────────┐
                │───────────│ └──│ playlist_videos │
                │ id (PK)   │────│────────────────│
                │ user_id   │    │ playlist_id    │
                │ name      │    │ video_id       │
                └───────────┘    │ position       │
                                 └────────────────┘
```

---

## 6. 학습 시스템 기능

| 기능 | 구현 상태 | 설명 |
|---|---|---|
| 시청 기록 저장 | ✅ | `POST /api/videos/progress` |
| 이어보기 | ✅ | `get_continue_watching()` — `last_position` 저장 |
| 학습 진도 추적 | ✅ | `watch_percentage`, `completed` 필드 |
| 취약 단원 추천 | ✅ | `analyze_weak_topics()` — 70점 미만 단원 |

---

## 7. 백엔드 아키텍처

### REST API 설계

| Method | Endpoint | 설명 |
|---|---|---|
| POST | `/api/chat/` | AI 대화 + 영상 추천 |
| POST | `/api/videos/search` | 통합 영상 검색 |
| GET | `/api/videos/topics` | 단원 목록 |
| POST | `/api/videos/recommendations` | 맞춤 추천 |
| POST | `/api/videos/progress` | 학습 진도 저장 |
| GET | `/api/videos/dashboard/{id}` | 학습 대시보드 |
| POST | `/api/playlists/` | 재생목록 생성 |
| GET | `/api/playlists/` | 재생목록 목록 |
| POST | `/api/users/register` | 회원가입 |
| POST | `/api/users/login` | 로그인 (JWT) |

---

## 8. 확장성 평가

### 10,000명 이상 사용자, 1,000개 이상 영상 시나리오

| 병목 | 원인 | 개선 방향 |
|---|---|---|
| SQLite 동시성 | Write Lock | PostgreSQL / MySQL 전환 |
| 영상 검색 속도 | 전체 스캔 | Elasticsearch + DB 인덱싱 |
| API 응답시간 | 매번 YouTube API 호출 | Redis 캐싱 (TTL 1시간) |
| 영상 전송 | 단일 서버 | CDN (CloudFront / Cloudflare) |
| 추천 연산 | 실시간 계산 | 배치 처리 + 캐시 (10분 TTL) |

---

## 9. 실무 서비스 요소

| 요소 | 현재 상태 | 개선 |
|---|---|---|
| 로그인 | ✅ JWT 구현 | OAuth2 (Google/Kakao) 추가 |
| API 인증 | ⚠️ 부분 적용 | `Depends(get_current_user)` 전역 적용 |
| 로그 수집 | ✅ `logging` 모듈 | ELK Stack / CloudWatch 연동 |
| 에러 처리 | ⚠️ try-except 기본 | 전역 Exception Handler + Sentry |

---

## 10. 면접 대비 질문 & 합격 수준 답변

### Q1. 이 프로젝트의 추천 시스템 아키텍처를 설명해주세요.

> **A**: Rule-based와 Score-based를 결합한 하이브리드 추천 시스템입니다. 1단계로 AI 챗봇이 대화에서 학년/단원/난이도를 추출하고, 2단계로 Rule-based 필터링으로 EBS/YouTube 영상을 매칭합니다. 로그인 사용자의 경우 퀴즈 점수 기반 취약 단원 분석을 추가하여 Score-based 추천을 병행합니다. Cold Start 문제는 Rule-based가 해결합니다.

### Q2. 왜 SQLite를 선택했고, 실서비스에서는 어떻게 전환하나요?

> **A**: 개발 단계에서 별도 DB 서버 없이 빠른 프로토타이핑이 가능하기 때문입니다. SQLAlchemy ORM을 사용했으므로 `DATABASE_URL`만 변경하면 PostgreSQL/MySQL로 무중단 전환 가능합니다. connection_args의 check_same_thread도 PostgreSQL에서는 불필요합니다.

### Q3. OpenAI API 없이도 동작하나요?

> **A**: 네. ChatService에 fallback 메서드를 구현했습니다. API 키가 없거나 API 오류 시 정규표현식 기반 휴리스틱 파싱으로 학년/단원/난이도를 추출합니다. 이는 Graceful Degradation 패턴으로, 외부 의존성 장애에도 핵심 기능을 유지합니다.

### Q4. 취약 단원 분석 로직을 설명해주세요.

> **A**: Progress 테이블과 Video 테이블을 JOIN하여 단원(topic)별 평균 퀴즈 점수를 계산합니다. 70점 미만인 단원을 취약으로 분류하고, 점수 구간별(30미만/50미만/70미만) 차등 학습 권고를 생성합니다. 해당 단원의 기초 수준 영상을 우선 추천합니다.

### Q5. 이 시스템의 병목은 어디이고, 어떻게 해결하나요?

> **A**: 주요 병목은 세 곳입니다. ①YouTube API 호출 지연 → Redis 캐싱(TTL 1시간). ②SQLite 동시 쓰기 제한 → PostgreSQL 전환. ③추천 연산 → 배치 계산 후 캐시. 현재 구조에서 10,000명까지는 PostgreSQL + Redis만으로 충분합니다.

### Q6. Service Layer와 Router Layer를 분리한 이유는?

> **A**: SRP(단일 책임 원칙)와 테스트 용이성 때문입니다. Router는 HTTP 요청/응답 처리만, Service는 비즈니스 로직만 담당합니다. Service는 DB 세션을 주입받으므로 단위 테스트 시 Mock DB를 주입할 수 있고, Router 변경 없이 비즈니스 로직을 교체할 수 있습니다.

### Q7. JWT 인증의 보안 취약점은 무엇이고, 어떻게 보완하나요?

> **A**: ①토큰 탈취 → HTTPS 필수 + HttpOnly Cookie 저장. ②토큰 무효화 불가 → Redis Blacklist + Refresh Token 도입. ③시크릿 키 노출 → 환경변수 관리 + 키 로테이션. 현재 프로젝트는 `.env`파일을 `.gitignore`에 등록하여 키 노출을 방지합니다.

### Q8. EBS 영상 데이터를 어떻게 확보하고 관리하나요?

> **A**: 현재는 교과 과정 기반으로 시드 데이터를 프로그래밍적으로 생성합니다. 실서비스에서는 ①EBS 공식 API/RSS, ②웹 스크래핑(robots.txt 준수), ③관리자 CMS를 통한 수동 등록을 병행합니다. 데이터는 JSON → DB로 이중화 관리됩니다.

### Q9. 이 프로젝트에서 가장 어려웠던 기술적 도전은?

> **A**: AI 챗봇의 응답에서 구조화된 정보를 안정적으로 추출하는 것입니다. OpenAI 응답은 비결정적이므로, JSON 블록 파싱 → 인라인 JSON → 정규식 휴리스틱의 3단계 Fallback을 구현했습니다. 이를 통해 추출 실패율을 최소화했습니다.

### Q10. 이 프로젝트를 마이크로서비스로 분리한다면?

> **A**: ①Chat Service (AI 대화), ②Video Service (영상 CRUD + 검색), ③Recommendation Service (추천 엔진), ④User Service (인증/프로필)로 분리합니다. 서비스 간 통신은 REST + Message Queue(RabbitMQ)를 사용하고, API Gateway로 진입점을 통합합니다.

---

## 11. 전체 평가

### 현재 수준: **중상**

| 영역 | 수준 | 비고 |
|---|---|---|
| 코드 품질 | 상 | 계층 분리, 네이밍 일관성, 모듈화 우수 |
| 시스템 설계 | 중상 | REST API + 서비스 레이어 + ORM 적용 |
| 추천 로직 | 중 | Rule + Score 하이브리드, AI 확장 여지 |
| 프론트엔드 | 중 | 기능적 완성도 높으나 프레임워크 미사용 |
| 실무 적합도 | 중 | 인증/로깅 기본 적용, 모니터링 미흡 |

### 가장 큰 문제 3개

1. **JWT 인증 미완성** — 대부분 엔드포인트에서 `user_id=1` 하드코딩
2. **테스트 커버리지 부족** — 추천 엔진 단위 테스트 미흡
3. **에러 처리 일관성** — 전역 Exception Handler 부재

### 개선 시 기대 수준: **상**

JWT 전역 적용 + 테스트 80% 커버리지 + 전역 에러 핸들링 + Docker 배포 시
포트폴리오 EdTech 프로젝트로 **면접에서 충분히 어필 가능**한 수준.
