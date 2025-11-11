# Benchmark Datasets

이 디렉토리에는 모델 평가를 위한 벤치마크 데이터셋이 저장됩니다.

## 데이터셋 종류

### 1. intent_test_set.jsonl
의도 분류 정확도 평가용 데이터셋

**형식:**
```json
{"question": "질문 텍스트", "expected_intent": "MEDICAL_INFO", "confidence": 0.95}
```

### 2. retrieval_test_set.jsonl
검색 품질 평가용 데이터셋

**형식:**
```json
{"query": "검색 쿼리", "relevant_doc_ids": ["doc1", "doc2"], "relevance_scores": [1.0, 0.8]}
```

### 3. end_to_end_scenarios.jsonl
전체 파이프라인 평가용 시나리오

**형식:**
```json
{"scenario": "크레아티닌 관련 질문", "question": "...", "expected_intent": "...", "expected_docs": 5}
```

## 데이터셋 생성

```bash
python scripts/experiments/prepare_benchmark_data.py
```
