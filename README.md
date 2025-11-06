# MockinJay - CKD 환자 지원 AI 챗봇

정확성 검증 기능을 갖춘 의료 Q&A 챗봇 시스템

## 🎯 프로젝트 개요

CKD(만성 콩팥병) 환자와 연구자를 위한 AI 기반 의료 챗봇입니다. LLM 에이전트와 RAG(검색 증강 생성)를 활용하여 과학 문헌 기반의 근거 있는 답변을 제공합니다.

### 주요 기능

- **10개 질문 의도 분류**: MEDICAL_INFO, DIET_INFO, RESEARCH, WELFARE_INFO, HEALTH_RECORD, LEARNING, POLICY, CHIT_CHAT, NON_MEDICAL, NON_ETHICAL
- **다중 벡터 데이터베이스**: QnA, Paper, Diet, Welfare, Policy, Quiz DB
- **RAG 검색 엔진**: 관련성 높은 논문 및 정보 검색
- **LLM 기반 요약**: 병기별 맞춤 설명 및 평이한 언어 변환
- **건강 기록 관리**: 크레아티닌, GFR 등 건강 수치 추적
- **안전 장치**: 의학적 판단 차단, 응급 상황 감지

## 📁 프로젝트 구조

```
MockinJay/
├── backend/              # FastAPI 백엔드
├── frontend/            # React 프론트엔드
├── data/                # 데이터 파일
│   ├── raw/            # 원본 데이터
│   ├── processed/      # 전처리 데이터
│   └── embeddings/     # 임베딩 데이터
├── models/              # ML 모델 파일
├── tests/               # 테스트
├── docs/                # 문서
└── scripts/             # 유틸리티 스크립트
```

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### 설치

1. **저장소 클론**
```bash
git clone https://github.com/MockingJayDec/MockinJay.git
cd MockinJay
```

2. **Python 가상 환경 설정**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **환경 변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 설정
```

## 📊 개발 단계

### 1단계: 핵심 의도 MVP (8주) ✅ 진행 중
- [x] 프로젝트 설정
- [x] 폴더 구조 생성
- [ ] FastAPI 백엔드 구축
- [ ] 3개 의도 분류 시스템

## ⚠️ 의료 안전 주의사항

- **의학적 진단이나 치료 권장 금지**: 이 시스템은 참고 정보만 제공합니다.
- **응급 상황**: 즉시 119 안내
- **의사 상담 권고**: 모든 의료 결정은 반드시 의료 전문가와 상담 필요

## 📚 문서

- [PRD (제품 요구사항 정의서)](./prd_ko.md)
- [기능 명세서](./fuction%20specification.md)
- [개발 체크리스트](./TASK.md)

## 📄 라이선스

MIT License

---

**마지막 업데이트**: 2025-11-05
**버전**: 1.0.0
**상태**: 개발 중 (1단계 MVP)