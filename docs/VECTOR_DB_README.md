# Vector Database System (ChromaDB)

## 🎯 개요
MockinJay 프로젝트의 벡터 데이터베이스 시스템은 **100% 무료**인 ChromaDB를 사용합니다.

### 왜 ChromaDB인가?
- ✅ **완전 무료** - API 키나 결제 정보 불필요
- ✅ **로컬 실행** - 외부 서버 불필요
- ✅ **간단한 설정** - pip install만으로 설치 완료
- ✅ **영구 저장** - 로컬 디스크에 자동 저장
- ✅ **한국어 지원** - 다국어 임베딩 모델 사용

### 다른 옵션과 비교
| 서비스 | 비용 | 설정 복잡도 | 비고 |
|--------|------|------------|------|
| **ChromaDB** | 무료 | 매우 간단 | 로컬 실행, MVP에 최적 |
| Pinecone | 유료 | 간단 | API 키 필요, 월 $70+ |
| Weaviate | 무료* | 복잡 | Docker 필요, 서버 설정 필요 |
| Qdrant | 무료* | 복잡 | Docker 필요, 메모리 많이 사용 |

## 🚀 빠른 시작

### 1. 설치
```bash
# 자동 설치 스크립트 실행
./scripts/setup_vector_db.sh

# 또는 수동 설치
pip install chromadb==0.4.22
pip install sentence-transformers
```

### 2. 테스트
```bash
# Vector DB 테스트 실행
python tests/test_vector_db.py
```

### 3. 서버 시작
```bash
# FastAPI 서버 시작
uvicorn backend.main:app --reload
```

## 📁 프로젝트 구조
```
backend/
├── services/
│   ├── vector_db.py      # ChromaDB 서비스 (핵심 로직)
│   └── data_loader.py    # 샘플 데이터 로더
├── api/v1/
│   └── vector.py         # REST API 엔드포인트
```

## 🔧 주요 기능

### 1. 의도별 컬렉션 분리
각 의도별로 별도의 컬렉션을 사용하여 검색 정확도를 높입니다:
- `MEDICAL_INFO` - 의학 Q&A
- `RESEARCH` - 연구 논문
- `POLICY` - 정책/가이드라인
- `DIET_INFO` - 식단 정보
- `WELFARE_INFO` - 복지 정보
- `LEARNING` - 학습 퀴즈

### 2. 무료 임베딩 모델
Sentence Transformers의 `paraphrase-multilingual-mpnet-base-v2` 모델 사용:
- 한국어 지원
- 완전 무료
- 로컬 실행
- 빠른 속도

### 3. 메타데이터 필터링
문서에 메타데이터를 추가하여 정밀한 검색 가능:
```python
# 예시: CKD 3기 관련 정보만 검색
results = vector_db.search(
    intent="MEDICAL_INFO",
    query="식단 관리",
    filters={"stage": "3"}
)
```

## 📡 API 엔드포인트

### 문서 추가
```bash
POST /api/v1/vector/add
{
    "intent": "MEDICAL_INFO",
    "documents": ["문서1", "문서2"],
    "metadatas": [{"category": "검사"}, {"category": "치료"}]
}
```

### 유사도 검색
```bash
POST /api/v1/vector/search
{
    "intent": "MEDICAL_INFO",
    "query": "크레아티닌 수치가 높으면?",
    "top_k": 5,
    "filters": {"category": "검사"}
}
```

### 샘플 데이터 로드
```bash
POST /api/v1/vector/load-sample-data?data_type=all
```

### 컬렉션 통계
```bash
GET /api/v1/vector/stats/MEDICAL_INFO
```

## 💡 사용 예시

### Python에서 직접 사용
```python
from backend.services.vector_db import vector_db

# 문서 추가
vector_db.add_documents(
    intent="MEDICAL_INFO",
    documents=["CKD 3기는 GFR 30-59입니다"],
    metadatas=[{"stage": "3", "category": "진단"}]
)

# 검색
results = vector_db.search(
    intent="MEDICAL_INFO",
    query="CKD 3기 진단 기준",
    top_k=5
)
```

### API로 사용
```python
import requests

# 검색 요청
response = requests.post(
    "http://localhost:8000/api/v1/vector/search",
    json={
        "intent": "MEDICAL_INFO",
        "query": "크레아티닌 정상 수치",
        "top_k": 3
    }
)
results = response.json()
```

## 📊 성능 특징

### 장점
- **빠른 응답**: 로컬 실행으로 네트워크 지연 없음
- **무제한 쿼리**: API 제한 없음
- **데이터 소유권**: 모든 데이터가 로컬에 저장
- **개인정보 보호**: 외부 서버로 데이터 전송 없음

### 제약사항
- **단일 서버**: 분산 처리 불가
- **메모리 제한**: 로컬 메모리에 의존
- **확장성**: 대규모 서비스 시 다른 솔루션 고려 필요

### 권장 사용 규모
- ✅ MVP/프로토타입: 완벽
- ✅ 소규모 서비스 (~10만 문서): 적합
- ⚠️ 중규모 서비스 (~100만 문서): 성능 테스트 필요
- ❌ 대규모 서비스 (100만+ 문서): 다른 솔루션 추천

## 🔄 마이그레이션 가이드

향후 규모가 커져서 다른 벡터 DB로 이전해야 할 경우:

### Pinecone으로 마이그레이션
```python
# vector_db.py의 __init__ 메소드만 수정
import pinecone
self.index = pinecone.Index("mockinjay")
# 나머지 인터페이스는 동일하게 유지
```

### Weaviate로 마이그레이션
```python
# vector_db.py의 __init__ 메소드만 수정
import weaviate
self.client = weaviate.Client("http://localhost:8080")
# 나머지 인터페이스는 동일하게 유지
```

## 🐛 트러블슈팅

### 설치 오류
```bash
# sqlite3 오류 시
pip install pysqlite3-binary

# 임베딩 모델 다운로드 오류 시
pip install --upgrade sentence-transformers
```

### 메모리 부족
```python
# config.py에서 컬렉션 수 제한
ACTIVE_COLLECTIONS = ["MEDICAL_INFO", "RESEARCH"]  # 필요한 것만
```

### 검색 성능 저하
```python
# 인덱스 재구축
vector_db.reset_collection("MEDICAL_INFO")
data_loader.load_sample_medical_qa()
```

## 📈 향후 개선 계획

1. **하이브리드 검색**: 키워드 + 벡터 검색 조합
2. **캐싱 레이어**: Redis 통합으로 응답 속도 향상
3. **백업 시스템**: 자동 백업 및 복원 기능
4. **모니터링**: 검색 품질 및 성능 모니터링 대시보드

## 🤝 기여 가이드

1. 새로운 의도 추가 시 `vector_db.py`의 `_init_collections` 수정
2. 샘플 데이터 추가 시 `data_loader.py`에 메소드 추가
3. API 엔드포인트 추가 시 `vector.py` 수정

## 📞 지원

문제가 있으신가요?
- GitHub Issues에 문제 제출
- `tests/test_vector_db.py` 실행하여 디버깅
- `logs/app.log` 확인

---

**작성일**: 2024-11-06
**버전**: 1.0.0
**작성자**: MockinJay Development Team