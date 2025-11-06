# MockinJay - CKD 환자 지원 AI 챗봇

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

만성 콩팥병(CKD) 환자를 위한 AI 기반 의료 정보 제공 시스템입니다.

---

## 🎯 프로젝트 개요

**MockinJay**는 CKD(만성 콩팥병) 환자와 보호자를 위한 AI 챗봇으로, LLM과 RAG(검색 증강 생성)를 활용하여 의료 논문과 가이드라인 기반의 신뢰할 수 있는 답변을 제공합니다.

### 핵심 기능

- **🎯 질문 의도 분류**: 9가지 의도 자동 분류 (MEDICAL_INFO, POLICY, RESEARCH 등)
- **🔍 RAG 검색 엔진**: Vector DB 기반 의료 논문 및 가이드라인 검색
- **📝 문서 요약**: LLM 기반 논문 요약 및 평이한 언어 변환
- **💬 통합 챗봇 파이프라인**: End-to-End 질의응답 시스템
- **📊 성능 모니터링**: 응답 시간, 정확도, 에러율 실시간 추적
- **🚨 안전 장치**: 응급 상황 감지, 의료 판단 차단, 비윤리적 질문 필터링

### 지원 의도 (Intent)

| 의도 | 설명 | 상태 |
|------|------|------|
| **MEDICAL_INFO** | 의학 정보 (질병, 검사, 약물) | ✅ 지원 |
| **POLICY** | 의료 정책 및 가이드라인 | ✅ 지원 |
| **RESEARCH** | 최신 연구 및 논문 검색 | ✅ 지원 |
| **WELFARE_INFO** | 복지 정보 | 🔜 예정 |
| **DIET_INFO** | 식단 정보 | 🔜 예정 |
| **LEARNING** | 퀴즈 학습 | 🔜 예정 |
| **HEALTH_RECORD** | 건강 기록 | 🔜 예정 |
| **CHIT_CHAT** | 일상 대화 | ✅ 지원 |
| **NON_MEDICAL** | 의료 외 질문 | ✅ 지원 |
| **NON_ETHICAL** | 비윤리적 질문 | ✅ 차단 |

---

## 🏗️ 시스템 아키텍처

```
User Question
     ↓
┌─────────────────────────────────────┐
│  1. 안전 검사 (Emergency/Medical)   │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  2. 의도 분류 (LLM + Cache)         │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  3. DB 선택 (Intent → Vector DB)    │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  4. RAG 검색 (Qdrant + PubMed API)  │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  5. 문서 요약 (LLM)                 │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  6. 응답 검증 및 출력               │
└─────────────────────────────────────┘
```

---

## 📁 프로젝트 구조

```
MockinJay/
├── backend/                    # FastAPI 백엔드
│   ├── api/v1/                # API 엔드포인트
│   │   ├── chat.py           # 통합 챗봇 API
│   │   ├── intent.py         # 의도 분류 API
│   │   ├── rag.py            # RAG 검색 API
│   │   ├── summarizer.py     # 요약 API
│   │   ├── vector.py         # 벡터 DB 관리 API
│   │   └── performance.py    # 성능 모니터링 API
│   ├── core/                 # 핵심 설정
│   │   ├── config.py         # 환경 설정
│   │   ├── logging.py        # 로깅 설정
│   │   └── errors.py         # 에러 핸들링
│   ├── schemas/              # Pydantic 모델
│   ├── services/             # 비즈니스 로직
│   │   ├── chat_pipeline.py # End-to-End 파이프라인
│   │   ├── intent.py         # 의도 분류 서비스
│   │   ├── rag_search.py     # RAG 검색 서비스
│   │   ├── summarizer.py     # 요약 서비스
│   │   ├── vector_db.py      # 벡터 DB 서비스
│   │   ├── cache.py          # Redis 캐싱
│   │   └── performance.py    # 성능 모니터링
│   └── main.py               # FastAPI 앱
├── data/                      # 데이터 파일
│   ├── raw/                  # 원본 데이터
│   ├── processed/            # 전처리 데이터
│   └── embeddings/           # 임베딩 데이터
├── tests/                     # 테스트
├── scripts/                   # 유틸리티 스크립트
├── requirements.txt           # Python 의존성
├── .env.example              # 환경 변수 예시
└── README.md                 # 본 문서
```

---

## 🚀 빠른 시작

### 필수 요구사항

- **Python** 3.10 이상
- **Redis** 7.0 이상 (선택사항, 캐싱 기능)
- **Qdrant** 1.7 이상 (Vector DB)
- **LLM API 키**: OpenAI 또는 Anthropic Claude

### 1. 저장소 클론

```bash
git clone https://github.com/MockingJayDec/MockinJay.git
cd MockinJay
```

### 2. Python 가상 환경 설정

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일 편집
vim .env
```

**필수 환경 변수**:

```bash
# 프로젝트 설정
PROJECT_NAME="MockinJay"
ENVIRONMENT="development"  # development, production
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000"

# LLM API 키 (하나 이상 필수)
OPENAI_API_KEY="sk-..."           # OpenAI API 키
ANTHROPIC_API_KEY="sk-ant-..."    # Anthropic Claude API 키
LLM_PROVIDER="openai"              # openai 또는 anthropic

# Vector DB (Qdrant)
QDRANT_HOST="localhost"
QDRANT_PORT="6333"
QDRANT_API_KEY=""                  # 로컬 실행 시 불필요

# Redis (선택사항)
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD=""                  # 비밀번호 없으면 공백
REDIS_DB="0"

# PubMed API (RESEARCH 의도용)
PUBMED_EMAIL="your-email@example.com"
```

### 5. Qdrant 시작 (Vector DB)

**Option 1: Docker로 실행 (권장)**

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

**Option 2: 로컬 바이너리 실행**

```bash
# Qdrant 다운로드 및 실행
# https://qdrant.tech/documentation/quick-start/
```

### 6. Redis 시작 (선택사항)

**Option 1: Docker로 실행**

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Option 2: 로컬 설치**

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

### 7. 벡터 DB 데이터 업로드

```bash
# 임베딩 데이터가 준비되어 있다면
python scripts/upload_embeddings.py

# 또는 샘플 데이터 생성
python scripts/generate_sample_data.py
```

### 8. 백엔드 서버 시작

```bash
# 개발 모드 (자동 재시작)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 9. API 문서 확인

브라우저에서 다음 URL을 열어 API 문서를 확인하세요:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📖 API 사용법

### 1. 통합 채팅 API (권장)

**Endpoint**: `POST /api/v1/chat`

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "크레아티닌이 높으면 어떤 증상이 나타나나요?",
    "user_id": "user123"
  }'
```

**응답**:

```json
{
  "question": "크레아티닌이 높으면 어떤 증상이 나타나나요?",
  "intent": "MEDICAL_INFO",
  "intent_confidence": 0.95,
  "answer": "크레아티닌 수치가 높을 때 나타나는 증상...",
  "summaries": [
    {
      "title": "만성 콩팥병의 증상",
      "content": "...",
      "source": "QnA DB"
    }
  ],
  "selected_databases": ["qna_db"],
  "total_documents": 5,
  "processing_time": 3.2,
  "is_emergency": false,
  "is_medical_judgment": false,
  "is_safe": true,
  "timestamp": "2025-11-06T15:30:00"
}
```

### 2. 성능 모니터링 API

**메트릭 조회**: `GET /api/v1/performance/metrics`

```bash
curl "http://localhost:8000/api/v1/performance/metrics"
```

**응답**:

```json
{
  "response_times": {
    "p50": 2.5,
    "p95": 8.3,
    "p99": 12.1,
    "mean": 3.2,
    "min": 1.1,
    "max": 15.4
  },
  "intent_accuracy": {
    "overall": 0.92,
    "by_intent": {
      "MEDICAL_INFO": 0.95,
      "POLICY": 0.88,
      "RESEARCH": 0.91
    },
    "labeled_count": 150,
    "total_count": 200
  },
  "error_rate": 0.005,
  "total_requests": 200,
  "error_count": 1,
  "timestamp": "2025-11-06T15:30:00"
}
```

**임계값 검증**: `GET /api/v1/performance/thresholds`

```bash
curl "http://localhost:8000/api/v1/performance/thresholds"
```

**응답**:

```json
{
  "response_time_ok": true,   // P95 < 25초
  "accuracy_ok": true,         // 정확도 >= 90%
  "error_rate_ok": true,       // 에러율 < 1%
  "all_ok": true
}
```

---

## 🧪 테스트

### 전체 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=backend --cov-report=html

# 특정 테스트 파일만
pytest tests/test_chat_pipeline.py

# 특정 테스트 함수만
pytest tests/test_chat_pipeline.py::TestChatPipeline::test_emergency_detection
```

### 테스트 구조

```
tests/
├── test_intent.py           # 의도 분류 테스트
├── test_rag_search.py       # RAG 검색 테스트
├── test_summarizer.py       # 요약 테스트
├── test_chat_pipeline.py    # 통합 파이프라인 테스트
├── test_performance.py      # 성능 모니터링 테스트
└── test_*_api.py           # API 엔드포인트 테스트
```

---

## 📊 성능 목표

| 메트릭 | 목표 | 현재 상태 |
|--------|------|-----------|
| **응답 시간 (P95)** | < 25초 | ✅ 모니터링 중 |
| **의도 분류 정확도** | ≥ 90% | ✅ 모니터링 중 |
| **시스템 에러율** | < 1% | ✅ 모니터링 중 |

---

## 🔧 기술 스택

### Backend

- **Framework**: FastAPI 0.109+
- **LLM**: OpenAI GPT-4o / Anthropic Claude 3.5 Sonnet
- **Vector DB**: Qdrant
- **Cache**: Redis
- **Embedding**: OpenAI text-embedding-3-small
- **Testing**: pytest, pytest-asyncio

### Data Sources

- **논문**: PubMed API
- **가이드라인**: 대한신장학회, KDIGO
- **Q&A**: 자체 수집 및 검증

---

## ⚠️ 의료 안전 주의사항

이 시스템은 **정보 제공 목적**으로만 사용되며, 다음 사항을 반드시 준수해야 합니다:

- ❌ **의학적 진단이나 치료 권장 금지**: 이 시스템은 참고 정보만 제공합니다
- 🚨 **응급 상황**: 즉시 119에 연락하도록 안내합니다
- 👨‍⚕️ **의사 상담 권고**: 모든 의료 결정은 반드시 의료 전문가와 상담 필요
- 🛡️ **안전 장치**: 의료 판단 요청은 자동으로 차단됩니다

---

## 🐛 문제 해결

### 1. Qdrant 연결 실패

```bash
# Qdrant가 실행 중인지 확인
curl http://localhost:6333/collections

# Docker 로그 확인
docker logs <qdrant-container-id>
```

### 2. Redis 연결 실패

Redis는 **선택사항**입니다. Redis 없이도 시스템이 동작합니다 (캐싱 비활성화).

```bash
# Redis 연결 테스트
redis-cli ping
# 응답: PONG
```

### 3. LLM API 에러

```bash
# API 키 확인
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# 환경 변수 재로드
source venv/bin/activate
```

### 4. 임베딩 데이터 없음

```bash
# 벡터 DB 컬렉션 확인
curl http://localhost:6333/collections

# 데이터 업로드
python scripts/upload_embeddings.py
```

---

## 📚 추가 문서

- **API 문서**: http://localhost:8000/docs (서버 실행 후)
- **개발자 가이드**: [DEVELOPER.md](./DEVELOPER.md)
- **PRD**: [prd_ko.md](./prd_ko.md)
- **개발 체크리스트**: [TASK.md](./TASK.md)

---

## 🤝 기여하기

기여를 환영합니다! 다음 단계를 따라주세요:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](./LICENSE) 파일을 참조하세요.

---

## 👥 팀

**MockinJay Team**
- Website: https://github.com/MockingJayDec/MockinJay
- Email: contact@mockinjay.dev

---

**마지막 업데이트**: 2025-11-06
**버전**: 0.1.0
**상태**: Milestone 1 완료 (핵심 MVP)
