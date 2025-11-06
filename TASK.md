# CKD 의료 챗봇 개발 체크리스트

## 🎯 프로젝트 개요
- **프로젝트명**: CKD 환자 지원 AI 챗봇 (MockinJay)
- **목표**: 정확성 검증 기능을 갖춘 의료 Q&A 챗봇 시스템
- **주 사용자**: CKD(만성 콩팥병) 환자 및 보호자

---

## 📋 Milestone 1: 핵심 의도 MVP (8주)
**목표**: 3개 핵심 의도로 기본 파이프라인 구축

### Feature 1.1: 프로젝트 설정
- [x] [Backend] Git 저장소 초기화 및 .gitignore 설정
- [ ] [Backend] Python 가상 환경 설정 (venv)
- [ ] [Frontend] Node.js 프로젝트 초기화
- [x] [Backend] requirements.txt 작성 (Python 의존성)
- [x] [Frontend] package.json 작성 (Node.js 의존성)
- [ ] [Backend] 개발 환경 설정 (VS Code, Linter, Formatter)
- [x] [Backend] 프로젝트 폴더 구조 설계
  ```
  MockinJay/
  ├── backend/          # FastAPI 백엔드
  ├── frontend/         # React 프론트엔드
  ├── data/            # 데이터 파일
  ├── models/          # ML 모델
  ├── tests/           # 테스트 코드
  ├── docs/            # 문서
  └── scripts/         # 유틸리티 스크립트
  ```



### Feature 1.2: 백엔드 기본 구조 (FastAPI)
- [x] [Backend] FastAPI 프로젝트 초기화
- [x] [Backend] API 라우터 설정 (`/api/v1/`)
- [x] [Backend] CORS 설정
- [x] [Backend] 환경 변수 관리 (.env 파일)
- [x] [Backend] 로깅 시스템 구축
- [x] [Backend] 에러 핸들링 미들웨어
- [x] [Backend] Health check 엔드포인트 (`/health`)

### Feature 1.3: 질문 의도 예측 시스템
- [x] **의도 데이터 준비**
  - [x] [AI] MEDICAL_INFO 의도 예시 3개 수집 (기본 구현)
  - [x] [AI] RESEARCH 의도 예시 3개 수집 (기본 구현)
  - [x] [AI] POLICY 의도 예시 3개 수집 (기본 구현)
  - [x] [AI] 의도별 JSON 스키마 정의
  - [x] [AI] Few-shot 프롬프트 템플릿 작성

- [x] **LLM 통합**
  - [x] [AI] OpenAI API 또는 Anthropic Claude API 설정
  - [x] [Backend] API 키 환경 변수 설정
  - [x] [Backend] LLM 호출 함수 구현
  - [x] [AI] Few-shot 프롬프팅 로직 구현
  - [x] [Backend] 응답 파싱 및 검증

- [x] **의도 분류 엔드포인트**
  - [x] [Backend] POST `/api/v1/intent/classify` 구현
  - [x] [Backend] 입력 검증 (Pydantic 모델)
  - [x] [Backend] 의도 분류 로직 통합
  - [ ] [Backend] 응답 시간 < 2초 최적화 (LLM 의존성)
  - [x] [Backend] 에러 처리 (API 실패, 타임아웃)

- [x] **응급 상황 감지 (POLICY)**
  - [x] [AI] 응급 키워드 리스트 정의
    - 숨이 안쉬어져, 가슴 아파, 의식 없어, 호흡곤란 등
  - [x] [Backend] 키워드 기반 우선 감지 로직
  - [x] [AI] 응급 응답 템플릿 작성
  - [x] [Backend] 119 연결 안내 메시지
  - [x] [Backend] 응급 로그 기록

- [x] **의학적 판단 차단 (POLICY)**
  - [x] [AI] 의학적 진단 요청 키워드 리스트
    - "이 증상 뭐에요?", "진단해줘", "병명 알려줘" 등
  - [x] [Backend] 판단 차단 감지 로직
  - [x] [AI] 의사 상담 권고 응답 템플릿
  - [x] [Backend] 차단 로그 기록

- [x] **테스트**
  - [x] [Backend] 단위 테스트 (pytest) 작성
  - [ ] [AI] 의도 분류 정확도 90% 이상 검증 (LLM API 키 필요)
  - [ ] [Backend] 응답 시간 < 2초 벤치마크 (LLM API 키 필요)
  - [x] [Backend] 응급 상황 감지 테스트
  - [x] [Backend] 의학적 판단 차단 테스트

### Feature 1.4: 벡터 DB 선택 시스템
- [x] **벡터 DB 선택**
  - [x] [Backend] ChromaDB 선택 (100% 무료, 로컬 실행)
  - [x] [Backend] ChromaDB 설정 (API 키 불필요)
  - [x] [Backend] Python 클라이언트 라이브러리 설치

- [x] **의도별 DB 라우팅 로직**
  - [x] [Backend] MEDICAL_INFO → QnA DB 매핑
  - [x] [Backend] RESEARCH → Paper DB 매핑
  - [x] [Backend] POLICY → Policy DB 매핑
  - [x] [Backend] 라우팅 설정 (config.py에 통합)
  - [x] [Backend] DB 선택 함수 구현

- [x] **테스트**
  - [x] [Backend] DB 연결 테스트
  - [x] [Backend] 의도별 라우팅 정확성 테스트

### Feature 1.5: 데이터 수집 및 임베딩
- [x] **QnA DB (MEDICAL_INFO)**
  - [x] [AI] CKD 관련 Q&A 데이터 100개 수집
    - 크레아티닌, GFR, 병기별 관리 등
  - [ ] [AI] 의료 전문가 검증 (가능한 경우)
  - [x] [AI] 임베딩 모델 선택 (Sentence-Transformers: paraphrase-multilingual-mpnet-base-v2)
  - [x] [AI] 데이터 임베딩 생성
  - [x] [Backend] 벡터 DB에 업로드 (100개 문서)
  - [x] [AI] 메타데이터 필드 정의 (병기, 카테고리 등)

- [x] **Paper DB (RESEARCH)**
  - [x] [Backend] PubMed API 설정 (HTTP 기반)
  - [x] [AI] CKD 관련 논문 초록 100개 수집
  - [x] [Backend] 논문 메타데이터 추출 (제목, 저자, 연도, DOI)
  - [x] [AI] 논문 초록 임베딩 생성
  - [x] [Backend] 벡터 DB에 업로드 (100개 문서)

- [x] **Policy DB (POLICY)**
  - [x] [AI] CKD 진료지침 문서 수집 (20개 가이드라인)
    - 대한신장학회 가이드라인
    - 국제 가이드라인 (KDIGO 등)
  - [x] [AI] 가이드라인 문서 청크 분할
  - [x] [AI] 임베딩 생성 및 업로드 (20개 문서)

### Feature 1.6: RAG 검색 엔진
- [x] **RAG 검색 로직**
  - [x] [AI] 쿼리 임베딩 생성 함수
  - [x] [Backend] 벡터 유사도 검색 함수
  - [x] [Backend] Top-K 결과 반환 (기본값: 5)
  - [x] [Backend] 유사도 점수 계산 및 정렬
  - [x] [Backend] 중복 제거 로직

- [x] **PubMed API 통합 (RESEARCH)**
  - [x] [Backend] PubMed API 클라이언트 구현
  - [x] [Backend] 조건부 API 호출 로직
  - [x] [Backend] API 응답 파싱
  - [x] [Backend] 속도 제한 처리 (rate limiting)
  - [x] [Backend] 캐싱 전략 (Redis)

- [x] **RAG 엔드포인트**
  - [x] [Backend] POST `/api/v1/rag/search` 구현
  - [x] [Backend] 입력: 질문, 의도, 선택된 DB
  - [x] [Backend] 출력: 상위 5개 관련 문서
  - [ ] [Backend] 검색 시간 < 5초 최적화 (벤치마크 필요)

- [x] **테스트**
  - [x] [Backend] 검색 관련성 테스트
  - [ ] [Backend] 검색 시간 벤치마크 (성능 측정 필요)
  - [x] [Backend] 엣지 케이스 테스트 (결과 없음, 단일 결과)

### Feature 1.7: 논문/문서 요약
- [x] **요약 생성 로직**
  - [x] [AI] LLM 기반 요약 프롬프트 작성
  - [x] [AI] 일관된 요약 형식 정의
    ```
    제목: [제목]
    저자: [저자]
    연도: [연도]
    요약: [2-3문장]
    주요 발견사항: [불릿 포인트]
    관련성: [질의와의 관련성]
    ```
  - [x] [AI] 요약 길이 제한 (100-150 단어)
  - [x] [AI] 병기별 맞춤 설명 로직
  - [x] [AI] 평이한 언어 변환

- [x] **요약 엔드포인트**
  - [x] [Backend] POST `/api/v1/summarize` 구현
  - [x] [Backend] 입력: 5개 문서
  - [x] [Backend] 출력: 5개 요약

- [x] **응답 검증 레이어**
  - [x] [AI] 의학적 정확성 체크 로직
  - [x] [Backend] 안전성 필터링 (부적절한 내용 차단)
  - [x] [Backend] 출처 첨부 (논문 링크, DOI)

- [x] **테스트**
  - [x] [Backend] 생성 시간 벤치마크
  - [x] [Backend] 일관된 형식 검증

### Feature 1.8: 통합 파이프라인
- [x] **End-to-End 파이프라인**
  - [x] [Backend] POST `/api/v1/chat` 엔드포인트 구현
  - [x] [Backend] 입력: 사용자 질문
  - [x] [Backend] 파이프라인 실행:
    1. 의도 분류
    2. DB 선택
    3. RAG 검색
    4. 요약 생성
    5. 응답 검증
  - [x] [Backend] 출력: 최종 응답 + 메타데이터

- [x] **비동기 처리**
  - [x] [Backend] FastAPI 비동기 함수 구현
  - [x] [Backend] 장기 실행 LLM 호출 비동기 처리
  - [x] [Backend] 타임아웃 설정 (20초)

- [x] **캐싱 전략**
  - [x] [Backend] Redis 설정 (이미 구현됨)
  - [x] [Backend] 의도 분류 결과 캐싱 (1시간)
  - [x] [Backend] RAG 검색 결과 캐싱 (24시간)

- [x] **테스트**
  - [x] [Backend] End-to-End 통합 테스트
  - [ ] [Backend] 전체 응답 시간 < 25초 검증 (LLM API 키 필요)
  - [x] [Backend] 에러 시나리오 테스트

### Feature 1.9: 성능 벤치마크 및 최적화
- [x] **성능 측정**
  - [x] [Backend] 응답 시간 모니터링 (P50, P95, P99 백분위수)
  - [x] [AI] 의도 분류 정확도 측정 (전체 및 의도별)
  - [x] [Backend] 시스템 오류율 측정

- [x] **성능 모니터링 구현**
  - [x] [Backend] PerformanceMonitor 서비스 구현
  - [x] [Backend] ChatPipeline에 성능 추적 통합
  - [x] [Backend] Redis 기반 성능 데이터 캐싱 (선택적)
  - [x] [Backend] 성능 메트릭 API 엔드포인트 (/api/v1/performance/metrics, /thresholds, /reset)
  - [x] [Backend] 성능 임계값 검증 (P95 < 25초, 정확도 >= 90%, 에러율 < 1%)

- [x] **테스트**
  - [x] [Backend] PerformanceMonitor 단위 테스트 (12개)
  - [x] [Backend] 성능 API 통합 테스트 (8개)

- [ ] **최적화** (향후 실제 데이터 기반)
  - [ ] [Backend] LLM API 호출 최적화
  - [ ] [Backend] 벡터 검색 최적화
  - [ ] [Backend] 캐싱 전략 개선
  - [ ] [Backend] 병렬 처리 (가능한 경우)

### Feature 1.10: 문서화 및 배포
- [x] **문서 작성**
  - [x] [Backend] API 문서 (Swagger/OpenAPI)
  - [x] [Backend] 설치 가이드 (README.md)
  - [x] [Backend] 개발자 가이드
  - [ ] [AI] 의도 분류 정확도 리포트

- [x] **배포 준비**
  - [x] [Backend] 환경 변수 문서화
  - [x] [Backend] 로컬 테스트 환경 구축
