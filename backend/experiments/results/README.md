# Experiment Results

이 디렉토리에는 벤치마크 실험 결과가 저장됩니다.

## 구조

```
results/
├── reports/          # 마크다운/HTML 보고서
├── logs/             # 상세 실행 로그
└── visualizations/   # 그래프, 차트
```

## 사용법

실험 스크립트 실행 시 자동으로 결과가 저장됩니다:

```bash
python scripts/experiments/run_embedding_benchmark.py --output results/embedding_comparison.json
```
