# MockinJay 테스트 가이드

이 문서는 MockinJay 프로젝트의 로컬 테스트 환경 설정 및 테스트 실행 방법을 안내합니다.

---

## 📋 목차

1. [테스트 환경 설정](#테스트-환경-설정)
2. [테스트 실행](#테스트-실행)
3. [테스트 커버리지](#테스트-커버리지)
4. [테스트 작성 가이드](#테스트-작성-가이드)
5. [CI/CD 통합](#cicd-통합)

---

## 테스트 환경 설정

### 1. 테스트 의존성 설치

```bash
# 가상 환경 활성화
source venv/bin/activate

# 테스트 의존성 설치
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### 2. 테스트용 환경 변수 설정

**Option 1: .env.test 파일 생성 (권장)**

```bash
# .env.test 파일 생성
cp .env.example .env.test

# 테스트용 값으로 수정
vim .env.test
```

**.env.test 예시**:

```bash
# 테스트 환경
ENVIRONMENT=testing

# Mock LLM (실제 API 호출 없음)
OPENAI_API_KEY=test-key
LLM_PROVIDER=openai

# 테스트용 Vector DB (메모리)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis 비활성화 (메모리 캐시 사용)
REDIS_HOST=
REDIS_PORT=

# 로깅 레벨
LOG_LEVEL=DEBUG
```

**Option 2: pytest 설정에서 환경 변수 자동 설정**

`pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
env =
    ENVIRONMENT=testing
    LOG_LEVEL=DEBUG
```

### 3. 테스트용 서비스 시작

**Qdrant (메모리 모드)**:

```bash
# Docker로 메모리 모드 실행
docker run -p 6333:6333 \
    --name qdrant-test \
    --rm \
    qdrant/qdrant

# 또는 영구 스토리지 없이 실행
docker run -p 6333:6333 \
    --name qdrant-test \
    --rm \
    -e QDRANT__SERVICE__GRPC_PORT=6334 \
    qdrant/qdrant
```

**Redis (선택사항)**:

```bash
# Redis는 테스트에서 선택사항입니다
# 없으면 메모리 캐시로 대체됩니다
docker run -p 6379:6379 --name redis-test --rm redis:7-alpine
```

---

## 테스트 실행

### 전체 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 상세 출력
pytest -v

# 실패 시 즉시 중단
pytest -x

# 마지막 실패한 테스트만 재실행
pytest --lf
```

### 특정 테스트 실행

```bash
# 특정 파일
pytest tests/test_intent.py

# 특정 클래스
pytest tests/test_intent.py::TestIntentClassifier

# 특정 함수
pytest tests/test_intent.py::TestIntentClassifier::test_medical_info_intent

# 패턴 매칭
pytest -k "test_intent"
```

### 병렬 테스트 실행

```bash
# pytest-xdist 설치
pip install pytest-xdist

# 자동 CPU 코어 수 감지
pytest -n auto

# 특정 워커 수 지정
pytest -n 4
```

### 마커를 사용한 선택적 실행

**테스트 마커 정의** (`pytest.ini`):

```ini
[pytest]
markers =
    slow: 느린 테스트 (LLM API 호출)
    integration: 통합 테스트
    unit: 단위 테스트
    api: API 엔드포인트 테스트
```

**마커 사용 예시**:

```python
# tests/test_intent.py
import pytest

@pytest.mark.unit
def test_intent_classification():
    pass

@pytest.mark.slow
@pytest.mark.integration
async def test_llm_api_call():
    pass
```

**마커로 필터링**:

```bash
# 단위 테스트만 실행
pytest -m unit

# slow 테스트 제외
pytest -m "not slow"

# integration OR api 테스트만
pytest -m "integration or api"
```

---

## 테스트 커버리지

### 커버리지 측정

```bash
# 커버리지와 함께 테스트 실행
pytest --cov=backend --cov-report=html --cov-report=term

# 특정 모듈만
pytest --cov=backend.services --cov-report=html

# 누락된 라인 표시
pytest --cov=backend --cov-report=term-missing
```

### 커버리지 리포트 확인

```bash
# HTML 리포트 열기
open htmlcov/index.html

# 터미널에서 요약 보기
pytest --cov=backend --cov-report=term
```

### 커버리지 목표

| 모듈 | 목표 | 현재 |
|------|------|------|
| **backend/services** | 90% | ✅ |
| **backend/api** | 85% | ✅ |
| **backend/core** | 80% | ✅ |
| **전체** | 85% | ✅ |

---

## 테스트 작성 가이드

### 디렉토리 구조

```
tests/
├── conftest.py                # 공통 fixture
├── test_intent.py             # 의도 분류 테스트
├── test_rag_search.py         # RAG 검색 테스트
├── test_summarizer.py         # 요약 테스트
├── test_chat_pipeline.py      # 통합 파이프라인 테스트
├── test_performance.py        # 성능 모니터링 테스트
├── test_chat_api.py           # Chat API 테스트
├── test_performance_api.py    # Performance API 테스트
└── test_vector_db_api.py      # Vector DB API 테스트
```

### Fixture 작성

**conftest.py**:

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.performance import performance_monitor

@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)

@pytest.fixture
def mock_llm_response():
    """LLM 응답 Mock"""
    return {
        "intent": "MEDICAL_INFO",
        "confidence": 0.95,
        "reasoning": "의학 정보 질문"
    }

@pytest.fixture(autouse=True)
def reset_performance():
    """각 테스트 전후 성능 모니터 리셋"""
    performance_monitor.reset()
    yield
    performance_monitor.reset()

@pytest.fixture
async def mock_vector_db():
    """Vector DB Mock"""
    with patch('backend.services.vector_db.VectorDBService') as mock:
        mock_instance = mock.return_value
        mock_instance.search.return_value = [
            {
                "id": "doc1",
                "payload": {"title": "Test Document"},
                "score": 0.95
            }
        ]
        yield mock_instance
```

### 단위 테스트 예시

**test_intent.py**:

```python
import pytest
from backend.services.intent import IntentClassifier

class TestIntentClassifier:
    @pytest.fixture
    def classifier(self):
        return IntentClassifier()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_medical_info_classification(self, classifier):
        """MEDICAL_INFO 의도 분류 테스트"""
        question = "크레아티닌이 높으면 어떻게 해야 하나요?"

        result = await classifier.classify(question)

        assert result["intent"] == "MEDICAL_INFO"
        assert result["confidence"] > 0.8
        assert "reasoning" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_caching_behavior(self, classifier):
        """캐싱 동작 테스트"""
        question = "테스트 질문"

        # 첫 번째 호출
        result1 = await classifier.classify(question)

        # 두 번째 호출 (캐시에서 가져옴)
        result2 = await classifier.classify(question)

        assert result1 == result2

    @pytest.mark.unit
    def test_invalid_input(self, classifier):
        """잘못된 입력 처리 테스트"""
        with pytest.raises(ValueError):
            classifier.classify("")
```

### 통합 테스트 예시

**test_chat_api.py**:

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

def test_chat_endpoint_success(client):
    """채팅 엔드포인트 성공 케이스"""
    with patch('backend.services.chat_pipeline.chat_pipeline.process_question',
               new_callable=AsyncMock) as mock_process:

        mock_process.return_value = {
            "question": "테스트 질문",
            "intent": "MEDICAL_INFO",
            "intent_confidence": 0.95,
            "answer": "테스트 답변",
            "summaries": [],
            "selected_databases": ["qna_db"],
            "total_documents": 5,
            "processing_time": 2.5,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True,
            "timestamp": "2025-11-06T15:30:00"
        }

        response = client.post(
            "/api/v1/chat",
            json={"question": "크레아티닌이 뭔가요?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "MEDICAL_INFO"
        assert data["intent_confidence"] == 0.95

def test_chat_endpoint_timeout(client):
    """타임아웃 테스트"""
    with patch('backend.services.chat_pipeline.chat_pipeline.process_question',
               new_callable=AsyncMock) as mock_process:

        import asyncio
        mock_process.side_effect = asyncio.TimeoutError()

        response = client.post(
            "/api/v1/chat",
            json={"question": "테스트"}
        )

        assert response.status_code == 504
        assert "초과" in response.json()["detail"]
```

### Mock 사용 패턴

**LLM API Mock**:

```python
@pytest.fixture
def mock_openai_client():
    with patch('openai.AsyncOpenAI') as mock:
        mock_instance = mock.return_value
        mock_instance.chat.completions.create = AsyncMock(
            return_value=type('obj', (object,), {
                'choices': [
                    type('obj', (object,), {
                        'message': type('obj', (object,), {
                            'content': '{"intent": "MEDICAL_INFO", "confidence": 0.95}'
                        })
                    })
                ]
            })
        )
        yield mock_instance
```

**Vector DB Mock**:

```python
@pytest.fixture
def mock_qdrant_client():
    with patch('qdrant_client.QdrantClient') as mock:
        mock_instance = mock.return_value
        mock_instance.search = AsyncMock(
            return_value=[
                type('obj', (object,), {
                    'id': 'doc1',
                    'payload': {'title': 'Test', 'content': 'Content'},
                    'score': 0.95
                })
            ]
        )
        yield mock_instance
```

---

## CI/CD 통합

### GitHub Actions 예시

**.github/workflows/test.yml**:

```yaml
name: Tests

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      qdrant:
        image: qdrant/qdrant:latest
        ports:
          - 6333:6333

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run tests
      env:
        ENVIRONMENT: testing
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        QDRANT_HOST: localhost
        QDRANT_PORT: 6333
        REDIS_HOST: localhost
        REDIS_PORT: 6379
      run: |
        pytest --cov=backend --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

### Pre-commit Hook

**.pre-commit-config.yaml**:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--extend-ignore=E203']

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: ['-m', 'not slow']
```

**설치 및 사용**:

```bash
# Pre-commit 설치
pip install pre-commit

# Hook 설치
pre-commit install

# 수동 실행
pre-commit run --all-files
```

---

## 트러블슈팅

### 일반적인 문제

#### 1. Qdrant 연결 실패

```bash
# Qdrant 상태 확인
curl http://localhost:6333/collections

# Docker 재시작
docker restart qdrant-test

# 테스트에서 Vector DB Mock 사용
pytest -m "not integration"
```

#### 2. 비동기 테스트 실패

**증상**: `RuntimeWarning: coroutine was never awaited`

**해결**:

```python
# pytest-asyncio 설치 확인
pip install pytest-asyncio

# pytest.ini에 설정 추가
[pytest]
asyncio_mode = auto

# 또는 데코레이터 사용
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

#### 3. Mock 관련 문제

**증상**: `AttributeError: Mock object has no attribute 'return_value'`

**해결**:

```python
# AsyncMock 사용
from unittest.mock import AsyncMock

# 비동기 함수 Mock
mock_func = AsyncMock(return_value={"result": "test"})

# 사용
result = await mock_func()
```

#### 4. 환경 변수 누락

**증상**: `KeyError: 'OPENAI_API_KEY'`

**해결**:

```python
# monkeypatch 사용
def test_with_env(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    # 테스트 코드

# 또는 .env.test 파일 생성
cp .env.example .env.test
```

---

## 테스트 모범 사례

### 1. AAA 패턴 (Arrange-Act-Assert)

```python
def test_intent_classification():
    # Arrange (준비)
    classifier = IntentClassifier()
    question = "크레아티닌이 뭔가요?"

    # Act (실행)
    result = classifier.classify(question)

    # Assert (검증)
    assert result["intent"] == "MEDICAL_INFO"
    assert result["confidence"] > 0.8
```

### 2. 테스트 격리

```python
# 각 테스트는 독립적이어야 함
@pytest.fixture(autouse=True)
def reset_state():
    # 테스트 전 초기화
    global_state.reset()
    yield
    # 테스트 후 정리
    global_state.cleanup()
```

### 3. 명확한 테스트 이름

```python
# ❌ 나쁜 예
def test_1():
    pass

# ✅ 좋은 예
def test_medical_info_intent_classification_with_high_confidence():
    pass
```

### 4. 하나의 테스트, 하나의 assert

```python
# ✅ 좋은 예 (필요하다면 여러 assert도 OK)
def test_response_structure():
    response = get_response()
    assert "intent" in response
    assert "confidence" in response
    assert response["confidence"] > 0.0
```

---

## 추가 리소스

- **pytest 문서**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **FastAPI 테스팅**: https://fastapi.tiangolo.com/tutorial/testing/

---

**마지막 업데이트**: 2025-11-06
