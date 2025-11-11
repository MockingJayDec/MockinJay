# MockinJay 개발자 가이드

이 문서는 MockinJay 프로젝트에 기여하거나 코드를 이해하려는 개발자를 위한 가이드입니다.

---

## 📋 목차

1. [개발 환경 설정](#개발-환경-설정)
2. [프로젝트 구조](#프로젝트-구조)
3. [핵심 컴포넌트](#핵심-컴포넌트)
4. [API 설계 원칙](#api-설계-원칙)
5. [테스트 가이드](#테스트-가이드)
6. [코딩 스타일](#코딩-스타일)
7. [Git 워크플로우](#git-워크플로우)
8. [성능 최적화](#성능-최적화)
9. [트러블슈팅](#트러블슈팅)

---

## 개발 환경 설정

### 필수 도구

```bash
# Python 3.10+
python --version

# Git
git --version

# Redis (선택)
redis-server --version

# ChromaDB (Vector DB - Python 패키지)
pip list | grep chromadb
```

### IDE 설정 (VS Code 권장)

**권장 확장 프로그램**:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-python.black-formatter",
    "ms-python.isort",
    "tamasfe.even-better-toml"
  ]
}
```

**설정 파일 (.vscode/settings.json)**:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.tabSize": 4
  }
}
```

### 로컬 개발 설정

```bash
# 1. 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 2. 개발 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구

# 3. Pre-commit 훅 설정
pre-commit install

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 개발용 API 키 설정
```

---

## 프로젝트 구조

### 디렉토리 구조 상세

```
MockinJay/
├── backend/
│   ├── api/                    # API 레이어
│   │   └── v1/                # API 버전 1
│   │       ├── __init__.py    # 라우터 통합
│   │       ├── chat.py        # 통합 채팅 엔드포인트
│   │       ├── intent.py      # 의도 분류 엔드포인트
│   │       ├── rag.py         # RAG 검색 엔드포인트
│   │       ├── summarizer.py  # 요약 엔드포인트
│   │       ├── vector.py      # 벡터 DB 관리 엔드포인트
│   │       └── performance.py # 성능 모니터링 엔드포인트
│   │
│   ├── core/                   # 핵심 설정 및 유틸리티
│   │   ├── config.py          # 환경 변수 및 설정 관리
│   │   ├── logging.py         # 로깅 설정
│   │   └── errors.py          # 에러 핸들링 및 커스텀 예외
│   │
│   ├── schemas/                # Pydantic 모델 (요청/응답 스키마)
│   │   ├── chat.py            # 채팅 관련 스키마
│   │   ├── intent.py          # 의도 관련 스키마
│   │   ├── rag.py             # RAG 관련 스키마
│   │   └── summarizer.py      # 요약 관련 스키마
│   │
│   ├── services/               # 비즈니스 로직 레이어
│   │   ├── chat_pipeline.py   # End-to-End 통합 파이프라인
│   │   ├── intent.py          # 의도 분류 서비스
│   │   ├── rag_search.py      # RAG 검색 서비스
│   │   ├── summarizer.py      # 문서 요약 서비스
│   │   ├── vector_db.py       # 벡터 DB 서비스 (ChromaDB)
│   │   ├── llm_client.py      # LLM API 클라이언트
│   │   ├── cache.py           # Redis 캐싱 서비스
│   │   ├── performance.py     # 성능 모니터링 서비스
│   │   ├── emergency_detector.py    # 응급 상황 감지
│   │   └── medical_judgment_detector.py  # 의료 판단 감지
│   │
│   └── main.py                 # FastAPI 애플리케이션 엔트리포인트
│
├── data/                       # 데이터 파일
│   ├── raw/                   # 원본 데이터
│   ├── processed/             # 전처리 데이터
│   └── embeddings/            # 임베딩 데이터
│
├── tests/                      # 테스트 코드
│   ├── conftest.py            # pytest 설정 및 fixture
│   ├── test_*.py              # 단위 테스트
│   └── test_*_api.py          # API 통합 테스트
│
├── scripts/                    # 유틸리티 스크립트
│   ├── upload_embeddings.py   # 임베딩 데이터 업로드
│   └── generate_sample_data.py # 샘플 데이터 생성
│
├── requirements.txt            # 프로덕션 의존성
├── requirements-dev.txt        # 개발 의존성
├── .env.example               # 환경 변수 예시
├── .gitignore                 # Git 무시 파일
├── pytest.ini                 # pytest 설정
├── pyproject.toml             # Python 프로젝트 설정
└── README.md                  # 사용자 가이드
```

---

## 핵심 컴포넌트

### 1. ChatPipeline (통합 파이프라인)

**위치**: `backend/services/chat_pipeline.py`

**역할**: 전체 질의응답 프로세스를 조율하는 메인 오케스트레이터

**처리 흐름**:

```python
async def process_question(question: str) -> Dict[str, Any]:
    # 1. 응급 상황 감지 (최우선)
    if EmergencyDetector.detect(question):
        return emergency_response

    # 2. 의료 판단 요청 감지
    if MedicalJudgmentDetector.detect(question):
        return medical_judgment_response

    # 3. 의도 분류 (LLM + 캐싱)
    intent_result = await self.intent_service.classify(question)

    # 4. 특수 의도 처리 (NON_MEDICAL, NON_ETHICAL, CHIT_CHAT)
    if intent in SPECIAL_INTENTS:
        return special_intent_response

    # 5. RAG 검색
    search_results = await self.rag_service.search(...)

    # 6. 문서 요약
    summaries = await self.summarizer.summarize(...)

    # 7. 응답 구성 및 검증
    return final_response
```

**주요 특징**:
- 비동기 처리 (`async/await`)
- 타임아웃 설정 (20초)
- 각 단계별 에러 핸들링
- 성능 메트릭 자동 기록

### 2. IntentClassifier (의도 분류)

**위치**: `backend/services/intent.py`

**역할**: LLM을 사용하여 사용자 질문의 의도를 9가지로 분류

**Few-shot 프롬프트**:

```python
SYSTEM_PROMPT = """
당신은 CKD(만성 콩팥병) 환자 지원 챗봇의 의도 분류 시스템입니다.
사용자 질문을 다음 9개 의도 중 하나로 분류하세요:

1. MEDICAL_INFO: 의학 정보 (질병, 검사, 약물)
2. POLICY: 의료 정책 및 가이드라인
3. RESEARCH: 최신 연구 및 논문
...
"""

FEW_SHOT_EXAMPLES = [
    {
        "question": "크레아티닌 수치가 높으면 어떻게 해야 하나요?",
        "intent": "MEDICAL_INFO",
        "confidence": 0.95
    },
    ...
]
```

**캐싱 전략**:
- 동일 질문: 1시간 캐싱
- 캐시 키: `intent:{question_hash}`
- Redis 사용 (없으면 메모리)

### 3. RAGSearchService (검색 증강 생성)

**위치**: `backend/services/rag_search.py`

**역할**: Vector DB와 외부 API를 통한 관련 문서 검색

**검색 로직**:

```python
async def search(question: str, intent: str, top_k: int = 5):
    # 1. 의도별 DB 선택
    collections = self._get_collections_for_intent(intent)

    # 2. 질문 임베딩 생성
    query_embedding = await self._embed_query(question)

    # 3. Vector 유사도 검색
    results = []
    for collection in collections:
        hits = await self.vector_db.search(
            collection=collection,
            query_vector=query_embedding,
            limit=top_k
        )
        results.extend(hits)

    # 4. RESEARCH 의도: PubMed API 추가 검색
    if intent == "RESEARCH":
        pubmed_results = await self._search_pubmed(question)
        results.extend(pubmed_results)

    # 5. 중복 제거 및 정렬
    results = self._deduplicate_and_sort(results)

    return results[:top_k]
```

**의도별 DB 매핑**:

| Intent | Collections |
|--------|-------------|
| MEDICAL_INFO | qna_db |
| POLICY | policy_db |
| RESEARCH | paper_db + PubMed API |

### 4. DocumentSummarizer (문서 요약)

**위치**: `backend/services/summarizer.py`

**역할**: LLM을 사용하여 검색된 문서를 평이한 언어로 요약

**요약 프롬프트**:

```python
SUMMARY_PROMPT = """
다음 의료 문서를 CKD 환자가 이해하기 쉽게 요약해주세요.

요약 형식:
- 제목: [문서 제목]
- 주요 내용: [2-3문장 요약]
- 핵심 포인트: [불릿 포인트 3-5개]
- 출처: [문서 출처]

주의사항:
- 의학 용어는 평이한 언어로 풀어서 설명
- CKD 병기별 맞춤 설명 제공
- 진단이나 처방은 절대 포함하지 않음
"""
```

**배치 처리**:
- 최대 5개 문서 동시 처리
- 각 요약: 100-150 단어 제한
- 비동기 병렬 처리

### 5. PerformanceMonitor (성능 모니터링)

**위치**: `backend/services/performance.py`

**역할**: 시스템 성능 지표를 실시간으로 추적 및 분석

**추적 메트릭**:

1. **응답 시간**:
   - P50, P95, P99 백분위수
   - 평균, 최소, 최대
   - 의도별 분해

2. **의도 분류 정확도**:
   - 전체 정확도
   - 의도별 정확도
   - 라벨링된 데이터만 계산

3. **에러율**:
   - 전체 요청 대비 에러 비율
   - 에러 타입별 집계

**사용 예시**:

```python
# 응답 시간 기록
performance_monitor.record_response_time(
    response_time=3.2,
    intent="MEDICAL_INFO",
    question="질문 내용"
)

# 의도 분류 기록
performance_monitor.record_intent_prediction(
    question="질문 내용",
    predicted_intent="MEDICAL_INFO",
    confidence=0.95,
    actual_intent="MEDICAL_INFO"  # optional
)

# 에러 기록
performance_monitor.record_error(
    error_type="ValueError",
    error_message="에러 메시지"
)

# 메트릭 조회
metrics = performance_monitor.get_metrics_summary()

# 임계값 검증
thresholds = performance_monitor.check_performance_thresholds()
if not thresholds["all_ok"]:
    logger.warning("Performance threshold violated!")
```

---

## API 설계 원칙

### RESTful API 규칙

1. **URL 구조**:
   ```
   /api/v{version}/{resource}/{action}
   ```

   예시:
   - `POST /api/v1/chat` - 채팅 요청
   - `GET /api/v1/performance/metrics` - 메트릭 조회
   - `POST /api/v1/performance/reset` - 메트릭 리셋

2. **HTTP 메서드**:
   - `GET`: 조회 (멱등성)
   - `POST`: 생성/처리
   - `PUT`: 전체 업데이트
   - `PATCH`: 부분 업데이트
   - `DELETE`: 삭제

3. **응답 형식**:
   ```python
   # 성공 응답 (200)
   {
       "data": {...},
       "timestamp": "2025-11-06T15:30:00"
   }

   # 에러 응답 (4xx, 5xx)
   {
       "detail": "에러 메시지",
       "error_code": "VALIDATION_ERROR",
       "timestamp": "2025-11-06T15:30:00"
   }
   ```

### Pydantic 스키마 작성

**Request 스키마**:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="사용자 질문"
    )
    user_id: Optional[str] = Field(
        None,
        description="사용자 ID (선택사항)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="추가 컨텍스트 (선택사항)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "크레아티닌이 높으면 어떻게 해야 하나요?",
                "user_id": "user123"
            }
        }
```

**Response 스키마**:

```python
from datetime import datetime

class ChatResponse(BaseModel):
    question: str
    intent: str
    intent_confidence: float
    answer: str
    summaries: List[SummaryItem]
    selected_databases: List[str]
    total_documents: int
    processing_time: float
    is_emergency: bool
    is_medical_judgment: bool
    is_safe: bool
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "question": "크레아티닌이 높으면...",
                "intent": "MEDICAL_INFO",
                "intent_confidence": 0.95,
                # ...
            }
        }
```

### 에러 핸들링

**커스텀 예외 정의**:

```python
# backend/core/errors.py
class MockinJayException(Exception):
    """기본 예외 클래스"""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class IntentClassificationError(MockinJayException):
    """의도 분류 실패"""
    pass

class RAGSearchError(MockinJayException):
    """RAG 검색 실패"""
    pass
```

**예외 핸들러 등록**:

```python
# backend/core/errors.py
def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(MockinJayException)
    async def mockinjay_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "detail": exc.message,
                "error_code": exc.error_code,
                "timestamp": datetime.now().isoformat()
            }
        )
```

---

## 테스트 가이드

### 테스트 구조

```
tests/
├── conftest.py              # pytest fixtures
├── test_intent.py           # 의도 분류 단위 테스트
├── test_rag_search.py       # RAG 검색 단위 테스트
├── test_summarizer.py       # 요약 단위 테스트
├── test_chat_pipeline.py    # 파이프라인 통합 테스트
├── test_performance.py      # 성능 모니터링 단위 테스트
├── test_chat_api.py         # Chat API 통합 테스트
├── test_performance_api.py  # Performance API 통합 테스트
└── test_vector_db_api.py    # Vector DB API 통합 테스트
```

### Fixture 작성

**conftest.py**:

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)

@pytest.fixture
def mock_llm_response():
    """LLM 응답 Mock"""
    return {
        "intent": "MEDICAL_INFO",
        "confidence": 0.95
    }

@pytest.fixture(autouse=True)
def reset_performance_monitor():
    """각 테스트 전후 성능 모니터 리셋"""
    from backend.services.performance import performance_monitor
    performance_monitor.reset()
    yield
    performance_monitor.reset()
```

### 단위 테스트 예시

```python
import pytest
from backend.services.intent import IntentClassifier

class TestIntentClassifier:
    @pytest.fixture
    def classifier(self):
        return IntentClassifier()

    @pytest.mark.asyncio
    async def test_medical_info_classification(self, classifier):
        """MEDICAL_INFO 의도 분류 테스트"""
        result = await classifier.classify(
            "크레아티닌이 높으면 어떻게 해야 하나요?"
        )

        assert result["intent"] == "MEDICAL_INFO"
        assert result["confidence"] > 0.8

    @pytest.mark.asyncio
    async def test_caching(self, classifier):
        """캐싱 동작 테스트"""
        question = "테스트 질문"

        # 첫 번째 호출
        result1 = await classifier.classify(question)

        # 두 번째 호출 (캐시에서 가져옴)
        result2 = await classifier.classify(question)

        assert result1 == result2
```

### 통합 테스트 예시

```python
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

def test_chat_endpoint_success(client):
    """채팅 엔드포인트 성공 케이스"""
    with patch('backend.services.chat_pipeline.chat_pipeline.process_question',
               new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {
            "question": "테스트 질문",
            "intent": "MEDICAL_INFO",
            "answer": "테스트 답변",
            # ...
        }

        response = client.post(
            "/api/v1/chat",
            json={"question": "테스트 질문"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "MEDICAL_INFO"
```

### Mock 사용 가이드

**LLM API Mock**:

```python
@pytest.fixture
def mock_openai():
    with patch('openai.ChatCompletion.acreate') as mock:
        mock.return_value = AsyncMock(
            choices=[
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': '{"intent": "MEDICAL_INFO", "confidence": 0.95}'
                    })
                })
            ]
        )
        yield mock
```

**Vector DB Mock**:

```python
@pytest.fixture
def mock_chromadb():
    with patch('chromadb.PersistentClient') as mock:
        mock_instance = mock.return_value
        mock_collection = type('obj', (object,), {
            'query': lambda **kwargs: {
                'documents': [['Test Document']],
                'metadatas': [[{'title': 'Test Document'}]],
                'distances': [[0.05]]
            }
        })
        mock_instance.get_or_create_collection.return_value = mock_collection
        yield mock_instance
```

---

## 코딩 스타일

### Python 스타일 가이드 (PEP 8)

**포맷팅 도구**:
- **Black**: 자동 코드 포맷팅
- **isort**: import 문 정렬
- **flake8**: 린팅

**설정 파일 (pyproject.toml)**:

```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### 명명 규칙

```python
# 클래스: PascalCase
class ChatPipeline:
    pass

# 함수/메서드: snake_case
async def process_question(question: str):
    pass

# 상수: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 20.0

# 변수: snake_case
user_question = "..."
intent_result = {}

# Private 메서드/변수: _leading_underscore
def _internal_method(self):
    pass
```

### 타입 힌팅

```python
from typing import Dict, List, Optional, Any, Union

async def search(
    question: str,
    intent: str,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    RAG 검색 수행

    Args:
        question: 사용자 질문
        intent: 분류된 의도
        top_k: 반환할 최대 문서 수
        filters: 추가 필터 (선택사항)

    Returns:
        검색된 문서 리스트

    Raises:
        RAGSearchError: 검색 실패 시
    """
    pass
```

### Docstring 규칙 (Google Style)

```python
def calculate_percentile(values: List[float], percentile: float) -> float:
    """백분위수를 계산합니다.

    Args:
        values: 숫자 리스트
        percentile: 백분위수 (0.0 ~ 1.0)

    Returns:
        계산된 백분위수 값

    Raises:
        ValueError: values가 비어있거나 percentile이 범위를 벗어난 경우

    Example:
        >>> calculate_percentile([1, 2, 3, 4, 5], 0.95)
        5.0
    """
    pass
```

---

## Git 워크플로우

### 브랜치 전략

```
main (production)
  ↑
dev (development)
  ↑
feature/feature-name (기능 개발)
```

**브랜치 명명 규칙**:
- `feature/feature-name`: 새 기능
- `fix/bug-description`: 버그 수정
- `docs/documentation-update`: 문서 업데이트
- `refactor/refactoring-description`: 리팩토링
- `test/test-description`: 테스트 추가

### 커밋 메시지 규칙

**형식**:

```
<type>: <subject>

<body>

<footer>
```

**Type**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 업데이트
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드, 설정 등

**예시**:

```bash
feat: Implement Feature 1.8 - Integration Pipeline

- Add ChatPipeline service for end-to-end processing
- Implement emergency detection and medical judgment blocking
- Add caching for intent classification and RAG search
- Create comprehensive integration tests

Closes #18
```

### Pull Request 프로세스

1. **브랜치 생성**:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature
   ```

2. **개발 및 커밋**:
   ```bash
   # 작업 수행
   git add .
   git commit -m "feat: Add new feature"
   ```

3. **테스트 실행**:
   ```bash
   pytest
   ```

4. **Push 및 PR 생성**:
   ```bash
   git push origin feature/your-feature
   # GitHub에서 PR 생성
   ```

5. **PR 템플릿**:
   ```markdown
   ## 변경 사항
   - Feature 1.8 구현
   - End-to-End 파이프라인 추가

   ## 테스트
   - [x] 단위 테스트 통과
   - [x] 통합 테스트 통과
   - [x] 수동 테스트 완료

   ## 체크리스트
   - [x] 코드 리뷰 요청
   - [x] 문서 업데이트
   - [x] TASK.md 업데이트

   Closes #18
   ```

---

## 성능 최적화

### 1. 비동기 처리

**FastAPI 비동기 엔드포인트**:

```python
@router.post("/chat")
async def process_chat(request: ChatRequest):
    # LLM 호출은 비동기로 처리
    result = await chat_pipeline.process_question(request.question)
    return result
```

**병렬 처리**:

```python
import asyncio

async def process_multiple_documents(documents: List[str]):
    # 5개 문서를 병렬로 요약
    tasks = [summarizer.summarize(doc) for doc in documents]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 캐싱 전략

**Redis 캐싱**:

```python
# 의도 분류 결과 캐싱 (1시간)
cache_key = f"intent:{hash(question)}"
cached = await cache_service.get(cache_key)
if cached:
    return cached

result = await llm_classify(question)
await cache_service.set(cache_key, result, expire=3600)
```

**메모리 캐싱 (Redis 없을 때)**:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_intent_examples(intent: str) -> List[Dict]:
    # Few-shot 예시 캐싱
    return load_examples(intent)
```

### 3. 데이터베이스 최적화

**벡터 검색 최적화**:

```python
# ChromaDB는 기본적으로 HNSW 인덱스 사용
# 검색 파라미터 튜닝
search_params = {
    "n_results": 5,      # 반환할 결과 수
    "include": ["documents", "metadatas", "distances"]  # 포함할 필드
}
```

**배치 처리**:

```python
# 여러 쿼리를 한 번에 처리
results = await vector_db.batch_search(
    queries=query_list,
    collection="qna_db",
    limit=5
)
```

### 4. LLM API 최적화

**토큰 수 제한**:

```python
# 프롬프트 최적화
response = await llm_client.complete(
    prompt=optimized_prompt,
    max_tokens=500,  # 응답 길이 제한
    temperature=0.3  # 일관성 높임
)
```

**스트리밍 응답** (향후 구현):

```python
async def stream_response(question: str):
    async for chunk in llm_client.stream(question):
        yield chunk
```

---

## 트러블슈팅

### 일반적인 문제

#### 1. LLM API 타임아웃

**증상**: `asyncio.TimeoutError` 발생

**해결**:

```python
# 타임아웃 증가
response = await asyncio.wait_for(
    llm_client.complete(prompt),
    timeout=30.0  # 20 → 30초
)

# 또는 재시도 로직 추가
for attempt in range(3):
    try:
        response = await llm_client.complete(prompt)
        break
    except asyncio.TimeoutError:
        if attempt == 2:
            raise
        await asyncio.sleep(1)
```

#### 2. Vector DB 데이터 문제

**증상**: ChromaDB 데이터가 로드되지 않음

**해결**:

```bash
# ChromaDB 데이터 디렉토리 확인
ls -la data/chroma_db/

# 컬렉션 확인 (Python)
python -c "import chromadb; client = chromadb.PersistentClient(path='data/chroma_db'); print(client.list_collections())"

# 데이터 재로드
python scripts/load_qa_data.py
```

#### 3. Redis 연결 실패

**증상**: `redis.ConnectionError`

**해결**: Redis는 선택사항이므로 graceful degradation 구현됨

```python
# backend/services/cache.py에서 자동 처리
if self.redis_client is None:
    logger.warning("Redis not available, using memory cache")
    return None
```

#### 4. 임베딩 차원 불일치

**증상**: `ValueError: dimension mismatch`

**해결**:

```python
# 임베딩 모델 확인
assert embedding_dim == 1536  # text-embedding-3-small

# Vector DB 컬렉션 재생성
await vector_db.recreate_collection(
    collection_name="qna_db",
    vector_size=1536
)
```

### 디버깅 팁

**로깅 레벨 조정**:

```python
# backend/core/logging.py
import logging

logging.basicConfig(
    level=logging.DEBUG,  # INFO → DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**성능 프로파일링**:

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # 프로파일링할 코드
    result = expensive_function()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

---

## 기여하기

1. Issue를 생성하여 작업 내용 논의
2. 브랜치를 생성하여 개발
3. 테스트를 작성하고 통과 확인
4. PR을 생성하고 리뷰 요청
5. 피드백 반영 후 병합

**코드 리뷰 체크리스트**:
- [ ] 테스트 커버리지 80% 이상
- [ ] 타입 힌팅 완료
- [ ] Docstring 작성
- [ ] 에러 핸들링 구현
- [ ] 성능 임팩트 고려
- [ ] 문서 업데이트 (필요 시)

---

## 추가 리소스

- **FastAPI 문서**: https://fastapi.tiangolo.com/
- **Pydantic 문서**: https://docs.pydantic.dev/
- **ChromaDB 문서**: https://docs.trychroma.com/
- **pytest 문서**: https://docs.pytest.org/
- **Python 타입 힌팅**: https://docs.python.org/3/library/typing.html

---

**마지막 업데이트**: 2025-11-06
