# MockinJay 아키텍처 리팩토링 설계

> **목표**: 모델 교체 가능성, 실험 용이성, Agent 기반 확장성을 위한 구조 개선

**작성일**: 2024-11-07
**버전**: 1.0.0

---

## 📋 목차

1. [개요](#개요)
2. [현재 문제점](#현재-문제점)
3. [새로운 아키텍처](#새로운-아키텍처)
4. [핵심 개념](#핵심-개념)
5. [폴더 구조](#폴더-구조)
6. [주요 컴포넌트](#주요-컴포넌트)
7. [사용 예시](#사용-예시)
8. [실험 워크플로우](#실험-워크플로우)
9. [마이그레이션 가이드](#마이그레이션-가이드)
10. [향후 로드맵](#향후-로드맵)

---

## 개요

### 🎯 목표

1. **모델 교체 가능성**: 임베딩 모델과 LLM을 쉽게 교체하여 성능 비교
2. **실험 용이성**: 체계적인 벤치마크 시스템으로 모델 평가
3. **Agent 기반 확장**: 모듈화된 Agent 시스템으로 기능 확장
4. **설정 기반 관리**: YAML 설정 파일로 모든 모델/Agent 관리

### 🔑 핵심 원칙

- **추상화 (Abstraction)**: 모든 모델과 Agent에 공통 인터페이스 제공
- **등록 패턴 (Registry Pattern)**: 동적 모델 로드 및 교체
- **관심사의 분리 (Separation of Concerns)**: 각 컴포넌트의 독립성 보장
- **의존성 역전 (Dependency Inversion)**: 구현이 아닌 추상화에 의존

---

## 현재 문제점

### 1. **하드코딩된 모델**
```python
# 현재 코드 (vector_db.py)
self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-mpnet-base-v2"  # 하드코딩
)
```

**문제점**:
- 다른 임베딩 모델로 교체하려면 코드 수정 필요
- 여러 모델 동시 비교 불가능
- 실험 결과 추적 어려움

### 2. **모놀리식 구조**
```python
# 현재 chat_pipeline.py
- 의도 분류, 검색, 요약, 안전성 검사 등 모든 로직이 한 파일에 집중
- 개별 컴포넌트 테스트 어려움
- 병렬 처리 불가능
```

### 3. **실험 시스템 부재**
- 모델 성능 비교를 위한 체계적인 방법 없음
- 벤치마크 데이터셋 관리 안됨
- 평가 지표 (MRR, nDCG 등) 측정 불가

---

## 새로운 아키텍처

### 📐 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│                     (FastAPI Endpoints)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Orchestrator                              │
│              (Agent 조율 및 워크플로우 관리)                    │
└──┬────────┬────────┬────────┬────────┬──────────────────────┘
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌──────┐┌──────┐┌────────┐┌────────┐┌─────────┐
│Safety││Intent││Retrieval││Summarize││Medical  │
│Agent ││Agent ││Agent   ││Agent   ││Agent    │
└──────┘└──────┘└────────┘└────────┘└─────────┘
   │        │        │          │         │
   │        │        │          │         │
   │        ▼        ▼          ▼         │
   │   ┌────────┐┌─────────┐┌────────┐  │
   │   │  LLM   ││Embedding││  LLM   │  │
   │   │Registry││Registry ││Registry│  │
   │   └────────┘└─────────┘└────────┘  │
   │        │        │          │         │
   ▼        ▼        ▼          ▼         ▼
┌─────────────────────────────────────────────┐
│           Base Classes & Interfaces          │
│    (BaseLLM, BaseEmbedder, BaseAgent)       │
└─────────────────────────────────────────────┘
```

### 🔄 데이터 흐름

```
사용자 질문
    ↓
Orchestrator (전체 조율)
    ↓
    ├─→ SafetyAgent: 안전성 검사
    │       ↓
    ├─→ IntentAgent: 의도 분류 (LLM Registry 사용)
    │       ↓ (LLM 교체 가능: gpt-4o-mini, claude, gemini)
    │       ↓
    ├─→ RetrievalAgent: 문서 검색 (Embedding Registry 사용)
    │       ↓ (Embedding 교체 가능: mpnet, bge-m3, e5)
    │       ↓
    ├─→ SummarizationAgent: 요약 생성 (LLM Registry 사용)
    │       ↓
    └─→ MedicalAgent: 의료 판단 검증
            ↓
최종 응답
```

---

## 핵심 개념

### 1. **모델 추상화 (Strategy Pattern)**

#### BaseEmbedder 인터페이스
```python
class BaseEmbedder(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass
```

#### 구현 예시
```python
class MPNetEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    @property
    def dimension(self) -> int:
        return 768
```

### 2. **Registry Pattern**

#### EmbeddingRegistry
```python
class EmbeddingRegistry:
    _models = {
        "mpnet-multilingual": MPNetEmbedder,
        "bge-m3": BGEM3Embedder,
        "e5-multilingual": E5Embedder,
    }

    @classmethod
    def get(cls, model_name: str, **kwargs) -> BaseEmbedder:
        return cls._models[model_name](**kwargs)
```

#### 사용법
```python
# 설정 파일에서 모델 이름만 변경하면 됨
embedder = EmbeddingRegistry.get("bge-m3")  # 쉬운 교체!
```

### 3. **Agent 아키텍처**

#### BaseAgent 추상 클래스
```python
class BaseAgent(ABC):
    def __init__(self, agent_name: str, llm_model: Optional[str] = None):
        self.agent_name = agent_name
        self.llm = LLMRegistry.get(llm_model) if llm_model else None
        self.tools = []

    @abstractmethod
    async def execute(self, input_data: Dict) -> Dict:
        """Agent의 핵심 실행 로직"""
        pass
```

#### IntentAgent 구현
```python
class IntentAgent(BaseAgent):
    def __init__(self, llm_model: str = "gpt-4o-mini"):
        super().__init__(agent_name="IntentAgent", llm_model=llm_model)

    async def execute(self, input_data: Dict) -> Dict:
        question = input_data["question"]

        # LLM을 사용한 의도 분류 (교체 가능)
        intent = await self.llm.classify(
            text=question,
            labels=list(IntentType)
        )

        return {
            "intent": intent["label"],
            "confidence": intent["confidence"]
        }
```

---

## 폴더 구조

```
MockinJay/
│
├── backend/
│   ├── models/                       # ✨ NEW: 모델 추상화 계층
│   │   ├── embeddings/
│   │   │   ├── base_embedder.py            # 추상 클래스
│   │   │   ├── mpnet_embedder.py           # 현재 모델
│   │   │   ├── bge_m3_embedder.py          # (추가 예정)
│   │   │   └── registry.py                 # 모델 등록소
│   │   │
│   │   └── llm/
│   │       ├── base_llm.py                 # 추상 클래스
│   │       ├── openai_llm.py               # OpenAI 구현
│   │       ├── anthropic_llm.py            # (추가 예정)
│   │       └── registry.py                 # LLM 등록소
│   │
│   ├── agents/                       # ✨ NEW: Agent 시스템
│   │   ├── base_agent.py                   # Agent 추상 클래스
│   │   ├── orchestrator.py                 # 메인 오케스트레이터
│   │   ├── specialized/
│   │   │   ├── intent_agent.py             # 의도 분류 Agent
│   │   │   ├── retrieval_agent.py          # 검색 Agent
│   │   │   └── summarization_agent.py      # 요약 Agent
│   │   │
│   │   └── tools/
│   │       ├── vector_search.py
│   │       └── pubmed_search.py
│   │
│   ├── experiments/                  # ✨ NEW: 실험/벤치마크
│   │   ├── benchmarks/
│   │   │   ├── embedding_comparison.py     # 임베딩 비교
│   │   │   └── llm_comparison.py           # LLM 비교
│   │   │
│   │   ├── metrics/
│   │   │   ├── retrieval_metrics.py        # MRR, nDCG
│   │   │   └── classification_metrics.py   # Accuracy, F1
│   │   │
│   │   └── results/
│   │       ├── reports/
│   │       └── visualizations/
│   │
│   └── services/                     # 기존 서비스 (리팩토링)
│       ├── vector_db.py              # Registry 사용
│       └── llm.py                    # Registry 사용
│
├── config/                           # ✨ NEW: 설정 관리
│   ├── models/
│   │   ├── embedding.yaml            # 임베딩 모델 설정
│   │   └── llm.yaml                  # LLM 설정
│   │
│   ├── agents/
│   │   └── orchestrator.yaml         # Agent 설정
│   │
│   └── environments/
│       ├── development.yaml
│       ├── production.yaml
│       └── experiment.yaml
│
├── data/
│   └── benchmark_datasets/           # ✨ NEW: 벤치마크 데이터
│       ├── intent_test_set.jsonl
│       └── retrieval_test_set.jsonl
│
└── scripts/
    └── experiments/                  # ✨ NEW: 실험 스크립트
        ├── run_embedding_benchmark.py
        └── run_llm_benchmark.py
```

---

## 주요 컴포넌트

### 1. BaseEmbedder (추상 임베딩 클래스)

**파일**: `backend/models/embeddings/base_embedder.py`

```python
class BaseEmbedder(ABC):
    """모든 임베딩 모델이 구현해야 하는 인터페이스"""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """단일 텍스트를 벡터로 변환"""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 배치로 변환"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """임베딩 벡터 차원"""
        pass
```

**구현된 모델**:
- `MPNetEmbedder`: 현재 사용 중인 모델 (768차원)
- (추가 예정) `BGEM3Embedder`: BAAI의 다국어 모델 (1024차원)
- (추가 예정) `E5Embedder`: Microsoft E5 모델 (768차원)

### 2. BaseLLM (추상 LLM 클래스)

**파일**: `backend/models/llm/base_llm.py`

```python
class BaseLLM(ABC):
    """모든 LLM이 구현해야 하는 인터페이스"""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """텍스트 완성 생성"""
        pass

    @abstractmethod
    async def classify(self, text: str, labels: List[str]) -> Dict:
        """텍스트 분류"""
        pass

    @property
    @abstractmethod
    def context_window(self) -> int:
        """컨텍스트 윈도우 크기"""
        pass
```

**구현된 모델**:
- `OpenAILLM`: GPT-4o, GPT-4o-mini 등
- (추가 예정) `AnthropicLLM`: Claude 3.5 Sonnet
- (추가 예정) `GeminiLLM`: Google Gemini Pro

### 3. EmbeddingRegistry

**파일**: `backend/models/embeddings/registry.py`

```python
class EmbeddingRegistry:
    """임베딩 모델 팩토리"""

    _models = {
        "mpnet-multilingual": MPNetEmbedder,
        "bge-m3": BGEM3Embedder,
    }

    @classmethod
    def get(cls, model_name: str, **kwargs) -> BaseEmbedder:
        """모델 이름으로 인스턴스 생성"""
        return cls._models[model_name](**kwargs)
```

### 4. BaseAgent & Orchestrator

**파일**: `backend/agents/base_agent.py`, `backend/agents/orchestrator.py`

```python
class BaseAgent(ABC):
    """모든 Agent의 기본 클래스"""

    def __init__(self, agent_name: str, llm_model: Optional[str] = None):
        self.agent_name = agent_name
        self.llm = LLMRegistry.get(llm_model) if llm_model else None

    @abstractmethod
    async def execute(self, input_data: Dict) -> Dict:
        pass

class Orchestrator:
    """Agent들을 조율하는 메인 컨트롤러"""

    def __init__(self, strategy: str = "sequential"):
        self.strategy = strategy
        self.agents = []

    def register_agent(self, agent: BaseAgent, priority: int):
        """Agent 등록"""
        self.agents.append({"agent": agent, "priority": priority})

    async def execute(self, input_data: Dict) -> Dict:
        """전체 파이프라인 실행"""
        if self.strategy == "sequential":
            return await self._execute_sequential(input_data)
        elif self.strategy == "parallel":
            return await self._execute_parallel(input_data)
```

---

## 사용 예시

### 예시 1: 임베딩 모델 교체

#### 기존 방식 (코드 수정 필요)
```python
# vector_db.py를 직접 수정해야 함
self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-mpnet-base-v2"  # 하드코딩
)
```

#### 새로운 방식 (설정 파일만 수정)
```yaml
# config/models/embedding.yaml
default: "bge-m3"  # 이 줄만 변경!

models:
  bge-m3:
    class: "BGEM3Embedder"
    dimension: 1024
    model_path: "BAAI/bge-m3"
```

```python
# vector_db.py (코드 변경 불필요)
from backend.models import EmbeddingRegistry

embedder = EmbeddingRegistry.get(config.embedding_model)
vectors = embedder.embed_batch(texts)
```

### 예시 2: LLM 교체로 의도 분류 비교

#### 설정 파일
```yaml
# config/models/llm.yaml
default:
  intent_classification: "gpt-4o-mini"  # 또는 "claude-3-5-sonnet"
```

#### 코드 (변경 불필요)
```python
# agents/specialized/intent_agent.py
class IntentAgent(BaseAgent):
    def __init__(self, llm_model: str):
        super().__init__("IntentAgent", llm_model=llm_model)

    async def execute(self, input_data: Dict) -> Dict:
        # LLM이 자동으로 설정에서 로드됨
        result = await self.llm.classify(
            text=input_data["question"],
            labels=list(IntentType)
        )
        return result
```

### 예시 3: Agent 기반 파이프라인

```python
# main.py 또는 chat_pipeline.py
from backend.agents import Orchestrator
from backend.agents.specialized import IntentAgent, RetrievalAgent

# Orchestrator 생성
orchestrator = Orchestrator(strategy="sequential")

# Agent 등록
orchestrator.register_agent(
    SafetyAgent(),
    priority=1
)
orchestrator.register_agent(
    IntentAgent(llm_model="gpt-4o-mini"),
    priority=2
)
orchestrator.register_agent(
    RetrievalAgent(embedding_model="mpnet-multilingual"),
    priority=3
)

# 실행
result = await orchestrator.execute({
    "question": "크레아티닌 수치가 높으면 어떤 증상이 나타나나요?",
    "user_id": "patient_001"
})
```

---

## 실험 워크플로우

### 시나리오 1: 임베딩 모델 비교

#### 1단계: 벤치마크 데이터 준비
```bash
python scripts/experiments/prepare_benchmark_data.py
```

#### 2단계: 여러 모델로 실험
```bash
python scripts/experiments/run_embedding_benchmark.py \
  --models mpnet-multilingual,bge-m3,e5-multilingual \
  --metrics mrr,ndcg,recall \
  --output backend/experiments/results/embedding_comparison.json
```

#### 3단계: 결과 분석
```json
{
  "mpnet-multilingual": {
    "MRR": 0.85,
    "nDCG@10": 0.78,
    "Recall@5": 0.72,
    "avg_latency_ms": 45,
    "dimension": 768
  },
  "bge-m3": {
    "MRR": 0.88,
    "nDCG@10": 0.82,
    "Recall@5": 0.76,
    "avg_latency_ms": 120,
    "dimension": 1024
  }
}
```

### 시나리오 2: LLM 비교 (의도 분류)

```bash
python scripts/experiments/run_llm_benchmark.py \
  --task intent_classification \
  --models gpt-4o-mini,claude-3-5-sonnet \
  --test-set data/benchmark_datasets/intent_test_set.jsonl \
  --output backend/experiments/results/llm_intent_comparison.json
```

#### 결과 예시
```json
{
  "gpt-4o-mini": {
    "accuracy": 0.92,
    "f1_score": 0.89,
    "avg_latency_ms": 850,
    "cost_per_1k": 0.15
  },
  "claude-3-5-sonnet": {
    "accuracy": 0.95,
    "f1_score": 0.93,
    "avg_latency_ms": 1200,
    "cost_per_1k": 3.00
  }
}
```

### 시나리오 3: 전체 파이프라인 A/B 테스트

```bash
python scripts/experiments/run_full_comparison.py \
  --config-a config/environments/production.yaml \
  --config-b config/environments/experiment.yaml \
  --scenarios data/benchmark_datasets/end_to_end_scenarios.jsonl \
  --metrics accuracy,latency,cost
```

---

## 마이그레이션 가이드

### 단계 1: 의존성 추가

```bash
pip install pyyaml sentence-transformers
```

### 단계 2: 기존 vector_db.py 수정

**Before**:
```python
self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-mpnet-base-v2"
)
```

**After**:
```python
from backend.models import EmbeddingRegistry
from backend.core.config import settings

embedder = EmbeddingRegistry.get(
    settings.EMBEDDING_MODEL,  # config에서 로드
    device="cpu"
)
```

### 단계 3: 기존 llm.py 수정

**Before**:
```python
self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
response = await self.openai_client.chat.completions.create(...)
```

**After**:
```python
from backend.models import LLMRegistry

llm = LLMRegistry.get("gpt-4o-mini")
response = await llm.complete(prompt="...")
```

### 단계 4: Agent 전환 (선택 사항)

기존 `chat_pipeline.py`의 로직을 Agent들로 분리:

1. `IntentAgent`: 의도 분류
2. `RetrievalAgent`: 문서 검색
3. `SummarizationAgent`: 요약 생성

---

## 향후 로드맵

### Phase 1: 기본 인프라 구축 ✅
- [x] 모델 추상화 계층 (BaseEmbedder, BaseLLM)
- [x] Registry 패턴 구현
- [x] Agent 시스템 기본 구조
- [x] YAML 설정 시스템

### Phase 2: 추가 모델 구현 (다음 단계)
- [ ] BGEM3Embedder 구현
- [ ] E5Embedder 구현
- [ ] OpenAIEmbedder 구현
- [ ] AnthropicLLM 구현
- [ ] GeminiLLM 구현

### Phase 3: Agent 전문화
- [ ] IntentAgent 구현
- [ ] RetrievalAgent 구현
- [ ] SummarizationAgent 구현
- [ ] SafetyAgent 구현
- [ ] MedicalAgent 구현

### Phase 4: 실험 시스템
- [ ] 벤치마크 스크립트 작성
- [ ] 평가 메트릭 구현 (MRR, nDCG, F1)
- [ ] 결과 시각화 대시보드
- [ ] 자동화된 A/B 테스트

### Phase 5: 최적화
- [ ] 모델 캐싱
- [ ] 병렬 실행 최적화
- [ ] 비용 추적 및 최적화
- [ ] 성능 프로파일링

---

## 📚 참고 자료

### 디자인 패턴
- **Strategy Pattern**: 임베딩/LLM 모델 교체
- **Registry Pattern**: 동적 모델 로드
- **Factory Pattern**: 모델 인스턴스 생성
- **Template Method**: Agent 실행 흐름

### 평가 메트릭
- **MRR (Mean Reciprocal Rank)**: 검색 품질
- **nDCG (Normalized Discounted Cumulative Gain)**: 순위 품질
- **Recall@K**: 상위 K개 결과에서 재현율
- **F1 Score**: 분류 정확도

### 모델 비교 기준
1. **정확도**: 작업별 성능 (의도 분류, 검색 품질)
2. **속도**: 평균 응답 시간 (ms)
3. **비용**: API 호출 당 비용 (USD)
4. **차원**: 임베딩 벡터 크기
5. **메모리**: 모델 로드 시 메모리 사용량

---

## 🎓 학습 리소스

- [Sentence Transformers 문서](https://www.sbert.net/)
- [ChromaDB 문서](https://docs.trychroma.com/)
- [LangChain 디자인 패턴](https://python.langchain.com/docs/modules/)
- [Information Retrieval 평가](https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval))

---

## 📞 문의

- 설계 관련 질문: Architecture Issues
- 버그 리포트: GitHub Issues
- 기능 제안: Feature Requests
