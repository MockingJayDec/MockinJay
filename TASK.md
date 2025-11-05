# CKD 의료 챗봇 개발 체크리스트

## 🎯 프로젝트 개요
- **프로젝트명**: CKD 환자 지원 AI 챗봇 (MockinJay)
- **목표**: 정확성 검증 기능을 갖춘 의료 Q&A 챗봇 시스템
- **주 사용자**: CKD(만성 콩팥병) 환자 및 보호자

---

## 📋 1단계: 핵심 의도 MVP (8주)
**목표**: 3개 핵심 의도로 기본 파이프라인 구축

### 1.1 프로젝트 설정
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



### 1.2 백엔드 기본 구조 (FastAPI)
- [x] [Backend] FastAPI 프로젝트 초기화
- [x] [Backend] API 라우터 설정 (`/api/v1/`)
- [x] [Backend] CORS 설정
- [x] [Backend] 환경 변수 관리 (.env 파일)
- [x] [Backend] 로깅 시스템 구축
- [x] [Backend] 에러 핸들링 미들웨어
- [x] [Backend] Health check 엔드포인트 (`/health`)

### 1.3 기능 1: 질문 의도 예측 시스템
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

### 1.4 기능 2: 벡터 DB 선택 시스템
- [ ] **벡터 DB 선택**
  - [ ] [Backend] Pinecone, Weaviate, Qdrant 중 선택
  - [ ] [Backend] 벡터 DB 계정 생성 및 API 키 설정
  - [ ] [Backend] Python 클라이언트 라이브러리 설치

- [ ] **의도별 DB 라우팅 로직**
  - [ ] [Backend] MEDICAL_INFO → QnA DB 매핑
  - [ ] [Backend] RESEARCH → Paper DB 매핑
  - [ ] [Backend] POLICY → Policy DB 매핑
  - [ ] [Backend] 라우팅 설정 파일 (config.yaml)
  - [ ] [Backend] DB 선택 함수 구현

- [ ] **테스트**
  - [ ] [Backend] DB 연결 테스트
  - [ ] [Backend] 의도별 라우팅 정확성 테스트

### 1.5 데이터 수집 및 임베딩
- [ ] **QnA DB (MEDICAL_INFO)**
  - [ ] [AI] CKD 관련 Q&A 데이터 100개 수집
    - 크레아티닌, GFR, 병기별 관리 등
  - [ ] [AI] 의료 전문가 검증 (가능한 경우)
  - [ ] [AI] 임베딩 모델 선택 (OpenAI, Sentence-Transformers)
  - [ ] [AI] 데이터 임베딩 생성
  - [ ] [Backend] 벡터 DB에 업로드
  - [ ] [AI] 메타데이터 필드 정의 (병기, 카테고리 등)

- [ ] **Paper DB (RESEARCH)**
  - [ ] [Backend] PubMed API 계정 설정
  - [ ] [AI] CKD 관련 논문 초록 100개 수집
  - [ ] [Backend] 논문 메타데이터 추출 (제목, 저자, 연도, DOI)
  - [ ] [AI] 논문 초록 임베딩 생성
  - [ ] [Backend] 벡터 DB에 업로드

- [ ] **Policy DB (POLICY)**
  - [ ] [AI] CKD 진료지침 문서 수집
    - 대한신장학회 가이드라인
    - 국제 가이드라인 (KDIGO 등)
  - [ ] [AI] 가이드라인 문서 청크 분할
  - [ ] [AI] 임베딩 생성 및 업로드

### 1.6 기능 3: RAG 검색 엔진
- [ ] **RAG 검색 로직**
  - [ ] [AI] 쿼리 임베딩 생성 함수
  - [ ] [Backend] 벡터 유사도 검색 함수
  - [ ] [Backend] Top-K 결과 반환 (기본값: 5)
  - [ ] [Backend] 유사도 점수 계산 및 정렬
  - [ ] [Backend] 중복 제거 로직

- [ ] **PubMed API 통합 (RESEARCH)**
  - [ ] [Backend] PubMed API 클라이언트 구현
  - [ ] [Backend] 조건부 API 호출 로직
  - [ ] [Backend] API 응답 파싱
  - [ ] [Backend] 속도 제한 처리 (rate limiting)
  - [ ] [Backend] 캐싱 전략 (Redis)

- [ ] **RAG 엔드포인트**
  - [ ] [Backend] POST `/api/v1/rag/search` 구현
  - [ ] [Backend] 입력: 질문, 의도, 선택된 DB
  - [ ] [Backend] 출력: 상위 5개 관련 문서
  - [ ] [Backend] 검색 시간 < 5초 최적화

- [ ] **테스트**
  - [ ] [Backend] 검색 관련성 테스트
  - [ ] [Backend] 검색 시간 벤치마크
  - [ ] [Backend] 엣지 케이스 테스트 (결과 없음, 단일 결과)

### 1.7 기능 4: 논문/문서 요약
- [ ] **요약 생성 로직**
  - [ ] [AI] LLM 기반 요약 프롬프트 작성
  - [ ] [AI] 일관된 요약 형식 정의
    ```
    제목: [제목]
    저자: [저자]
    연도: [연도]
    요약: [2-3문장]
    주요 발견사항: [불릿 포인트]
    관련성: [질의와의 관련성]
    ```
  - [ ] [AI] 요약 길이 제한 (100-150 단어)
  - [ ] [AI] 병기별 맞춤 설명 로직
  - [ ] [AI] 평이한 언어 변환

- [ ] **요약 엔드포인트**
  - [ ] [Backend] POST `/api/v1/summarize` 구현
  - [ ] [Backend] 입력: 5개 문서
  - [ ] [Backend] 출력: 5개 요약
  - [ ] [Backend] 전체 생성 시간 < 10초

- [ ] **응답 검증 레이어**
  - [ ] [AI] 의학적 정확성 체크 로직
  - [ ] [Backend] 안전성 필터링 (부적절한 내용 차단)
  - [ ] [Backend] 출처 첨부 (논문 링크, DOI)

- [ ] **테스트**
  - [ ] [AI] 요약 품질 평가 (의료 전문가 검토)
  - [ ] [Backend] 생성 시간 벤치마크
  - [ ] [Backend] 일관된 형식 검증

### 1.8 통합 파이프라인
- [ ] **End-to-End 파이프라인**
  - [ ] [Backend] POST `/api/v1/chat` 엔드포인트 구현
  - [ ] [Backend] 입력: 사용자 질문
  - [ ] [Backend] 파이프라인 실행:
    1. 의도 분류
    2. DB 선택
    3. RAG 검색
    4. 요약 생성
    5. 응답 검증
  - [ ] [Backend] 출력: 최종 응답 + 메타데이터

- [ ] **비동기 처리**
  - [ ] [Backend] FastAPI 비동기 함수 구현
  - [ ] [Backend] 장기 실행 LLM 호출 비동기 처리
  - [ ] [Backend] 타임아웃 설정 (20초)

- [ ] **캐싱 전략**
  - [ ] [Backend] Redis 설정
  - [ ] [Backend] 의도 분류 결과 캐싱 (1시간)
  - [ ] [Backend] RAG 검색 결과 캐싱 (24시간)

- [ ] **테스트**
  - [ ] [Backend] End-to-End 통합 테스트
  - [ ] [Backend] 전체 응답 시간 < 25초 검증
  - [ ] [Backend] 에러 시나리오 테스트

### 1.9 성능 벤치마크 및 최적화
- [ ] **성능 측정**
  - [ ] [Backend] 응답 시간 모니터링 (P95 < 25초)
  - [ ] [AI] 의도 분류 정확도 측정 (90% 이상)
  - [ ] [Backend] 시스템 오류율 측정 (< 1%)

- [ ] **최적화**
  - [ ] [Backend] LLM API 호출 최적화
  - [ ] [Backend] 벡터 검색 최적화
  - [ ] [Backend] 캐싱 전략 개선
  - [ ] [Backend] 병렬 처리 (가능한 경우)

### 1.10 문서화 및 배포
- [ ] **문서 작성**
  - [ ] [Backend] API 문서 (Swagger/OpenAPI)
  - [ ] [Backend] 설치 가이드 (README.md)
  - [ ] [Backend] 개발자 가이드
  - [ ] [AI] 의도 분류 정확도 리포트

- [ ] **배포 준비**
  - [ ] [Backend] Docker 컨테이너화
  - [ ] [Backend] docker-compose.yml 작성
  - [ ] [Backend] 환경 변수 문서화
  - [ ] [Backend] 로컬 테스트 환경 구축

---

## 📋 2단계: 환자 지원 기능 (6주)
**목표**: 환자 중심 의도 추가 (DIET_INFO, WELFARE_INFO, HEALTH_RECORD)

### 2.1 DIET_INFO (식단 정보)
- [ ] **Diet DB 구축**
  - [ ] [AI] 저칼륨 식단 정보 수집 (50개 항목)
  - [ ] [AI] 저나트륨 식단 정보 수집 (50개 항목)
  - [ ] [AI] 저단백 식단 정보 수집 (50개 항목)
  - [ ] [AI] 식품별 영양 성분 데이터 수집
    - 칼륨, 나트륨, 단백질 함량
  - [ ] [AI] CKD 병기별 권장/제한 식품 리스트
  - [ ] [AI] 임베딩 생성 및 벡터 DB 업로드

- [ ] **의도 학습 데이터**
  - [ ] [AI] DIET_INFO 의도 예시 100개 수집
  - [ ] [AI] Few-shot 프롬프트 업데이트

- [ ] **식단 추천 로직**
  - [ ] [Backend] 병기별 식단 필터링
  - [ ] [AI] 식품 대체 추천 알고리즘
  - [ ] [Backend] 영양 성분 계산기

- [ ] **테스트**
  - [ ] [Backend] 식단 추천 정확성 테스트
  - [ ] [Backend] 병기별 필터링 검증

### 2.2 WELFARE_INFO (복지 정보)
- [ ] **Welfare DB 구축**
  - [ ] [AI] 4단계 복지 안내 데이터 수집
    1. 자격요건
    2. 신청방법
    3. 제출서류
    4. 수급절차
  - [ ] [AI] 투석 환자 지원금 정보
  - [ ] [AI] 장애등급 신청 정보
  - [ ] [AI] 의료비 지원 정보
  - [ ] [AI] 지역별 복지 정보 (전국 주요 도시)
  - [ ] [AI] 출처: 보건복지부, 국민건강보험공단
  - [ ] [AI] 임베딩 생성 및 벡터 DB 업로드

- [ ] **의도 학습 데이터**
  - [ ] [AI] WELFARE_INFO 의도 예시 100개 수집

- [ ] **4단계 복지 안내 시스템**
  - [ ] [Backend] 단계별 정보 제공 로직
  - [ ] [Backend] 지역별 정보 필터링
  - [ ] [Backend] 온라인 신청 링크 자동 생성

- [ ] **테스트**
  - [ ] [Backend] 4단계 안내 완전성 검증
  - [ ] [Backend] 지역별 정보 정확성 테스트

### 2.3 HEALTH_RECORD (건강 기록)
- [ ] **데이터베이스 설계**
  - [ ] [Backend] 사용자 테이블 스키마
  - [ ] [Backend] 건강 기록 테이블 스키마
    - 크레아티닌, GFR, 혈압, 체중 등
  - [ ] [Backend] 시계열 데이터 구조
  - [ ] [Backend] PostgreSQL 또는 TimescaleDB 선택

- [ ] **의도 학습 데이터**
  - [ ] [AI] HEALTH_RECORD 의도 예시 100개 수집

- [ ] **건강 기록 저장/조회 API**
  - [ ] [Backend] POST `/api/v1/health/record` - 기록 저장
  - [ ] [Backend] GET `/api/v1/health/record/{user_id}` - 기록 조회
  - [ ] [Backend] GET `/api/v1/health/trend/{user_id}` - 추이 분석

- [ ] **추이 분석 로직**
  - [ ] [Backend] 이전 기록과 비교
  - [ ] [AI] 악화/호전 판단 알고리즘
  - [ ] [Backend] 알림 트리거 조건 설정

- [ ] **시각화 엔진**
  - [ ] [Backend] 시계열 그래프 생성 (Plotly, Chart.js)
  - [ ] [Backend] 추이 그래프 API 엔드포인트
  - [ ] [Backend] 병기별 정상 범위 표시

- [ ] **개인정보 보호**
  - [ ] [Backend] 데이터 암호화 (저장 시)
  - [ ] [Backend] 사용자 인증 (JWT)
  - [ ] [Backend] 접근 제어 (RBAC)

- [ ] **테스트**
  - [ ] [Backend] 저장/조회 기능 테스트
  - [ ] [Backend] 추이 분석 정확성 검증
  - [ ] [Backend] 보안 테스트

### 2.4 프론트엔드 기본 구조
- [ ] **React 프로젝트 설정**
  - [ ] [Frontend] Create React App 또는 Vite 설정
  - [ ] [Frontend] Tailwind CSS 설치
  - [ ] [Frontend] 라우팅 설정 (React Router)
  - [ ] [Frontend] 상태 관리 (Context API 또는 Redux)

- [ ] **UI 컴포넌트**
  - [ ] [Frontend] 채팅 인터페이스
  - [ ] [Frontend] 건강 기록 입력 폼
  - [ ] [Frontend] 추이 그래프 컴포넌트
  - [ ] [Frontend] 식단 추천 카드
  - [ ] [Frontend] 복지 안내 단계별 UI

- [ ] **API 통합**
  - [ ] [Frontend] Axios 또는 Fetch API 설정
  - [ ] [Frontend] API 클라이언트 함수 작성
  - [ ] [Frontend] 에러 처리

- [ ] **테스트**
  - [ ] [Frontend] 컴포넌트 단위 테스트 (Jest, React Testing Library)
  - [ ] [Frontend] 통합 테스트

---

## 📋 3단계: 피드백 및 학습 시스템 (4주)
**목표**: 품질 개선 및 환자 교육 (LEARNING, CHIT_CHAT, 피드백 시스템)

### 3.1 LEARNING (레벨별 퀴즈)
- [ ] **Quiz DB 구축**
  - [ ] [AI] 초급 퀴즈 50개 작성
    - GFR, 크레아티닌 기본 개념
  - [ ] [AI] 중급 퀴즈 50개 작성
    - 식단 관리, 약물 관리
  - [ ] [AI] 고급 퀴즈 50개 작성
    - 병기별 관리, 합병증 예방
  - [ ] [AI] 퀴즈 스키마 정의
    ```json
    {
      "question": "GFR이란 무엇인가요?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "GFR은...",
      "level": "초급",
      "category": "기본 개념"
    }
    ```
  - [ ] [AI] 임베딩 생성 및 벡터 DB 업로드

- [ ] **의도 학습 데이터**
  - [ ] [AI] LEARNING 의도 예시 100개 수집

- [ ] **퀴즈 엔진**
  - [ ] [Backend] GET `/api/v1/quiz/random` - 랜덤 퀴즈
  - [ ] [Backend] POST `/api/v1/quiz/answer` - 답변 제출
  - [ ] [Backend] GET `/api/v1/quiz/explanation` - 해설 조회
  - [ ] [Backend] 난이도 선택 로직
  - [ ] [Backend] 사용자 레벨 추적 (선택 사항)

- [ ] **테스트**
  - [ ] [Backend] 퀴즈 난이도 분포 검증
  - [ ] [Backend] 답변 평가 정확성 테스트

### 3.2 CHIT_CHAT (일상 대화)
- [ ] **의도 학습 데이터**
  - [ ] [AI] CHIT_CHAT 의도 예시 100개 수집
    - "안녕!", "고마워", "힘들어" 등

- [ ] **공감적 대화 모듈**
  - [ ] [AI] 공감 응답 템플릿 작성
  - [ ] [AI] 감정 분석 로직 (선택 사항)
  - [ ] [AI] 위로 메시지 생성

- [ ] **테스트**
  - [ ] [AI] 대화 자연스러움 평가
  - [ ] [AI] 공감 응답 적절성 검증

### 3.3 기능 5: 휴먼 피드백 데이터 수집
- [ ] **데이터베이스 설계**
  - [ ] [Backend] 피드백 테이블 스키마
    ```sql
    CREATE TABLE feedback (
      id SERIAL PRIMARY KEY,
      question TEXT,
      intent VARCHAR(50),
      selected_dbs TEXT[],
      retrieved_papers JSONB,
      summaries JSONB,
      feedback VARCHAR(20),  -- Good, 판단어려움, Bad
      timestamp TIMESTAMP,
      evaluator_id VARCHAR(50)
    );
    ```

- [ ] **데이터 수집 API**
  - [ ] [Backend] POST `/api/v1/feedback/record` - 피드백 기록
  - [ ] [Backend] GET `/api/v1/feedback/list` - 피드백 목록
  - [ ] [Backend] GET `/api/v1/feedback/stats` - 통계

- [ ] **테스트**
  - [ ] [Backend] 데이터 저장 완전성 검증
  - [ ] [Backend] 쿼리 성능 테스트

### 3.4 기능 6: 휴먼 피드백 인터페이스
- [ ] **피드백 UI 컴포넌트**
  - [ ] [Frontend] 질문 표시 영역
  - [ ] [Frontend] 요약 표시 영역 (5개)
  - [ ] [Frontend] 피드백 버튼 (Good, 판단어려움, Bad)
  - [ ] [Frontend] 메타데이터 표시 (의도, DB, 타임스탬프)
  - [ ] [Frontend] 페이지네이션

- [ ] **피드백 제출 로직**
  - [ ] [Frontend] 원클릭 피드백 제출
  - [ ] [Frontend] 즉시 데이터베이스 저장
  - [ ] [Frontend] 다음 질문/답변 쌍 자동 로드

- [ ] **통계 대시보드**
  - [ ] [Frontend] 전체 피드백 통계 (Good/판단어려움/Bad 비율)
  - [ ] [Frontend] 의도별 정확도 통계
  - [ ] [Frontend] 시간별 피드백 추이 그래프

- [ ] **테스트**
  - [ ] [Frontend] 피드백 제출 기능 테스트
  - [ ] [Frontend] 통계 정확성 검증
  - [ ] [Frontend] 반응형 디자인 테스트

---

## 📋 4단계: 안전장치 및 최적화 (4주)
**목표**: 보안 강화 및 성능 최적화 (NON_MEDICAL, NON_ETHICAL)

### 4.1 NON_MEDICAL (도메인 외 거절)
- [ ] **의도 학습 데이터**
  - [ ] [AI] NON_MEDICAL 의도 예시 100개 수집
    - "코딩해줘", "번역해줘", "날씨 알려줘" 등

- [ ] **도메인 외 감지 로직**
  - [ ] [AI] 도메인 외 키워드 리스트
  - [ ] [Backend] 분류 신뢰도 임계값 설정

- [ ] **정중한 거절 응답**
  - [ ] [AI] 거절 메시지 템플릿
  - [ ] [AI] 지원 가능한 질문 예시 제공

- [ ] **테스트**
  - [ ] [Backend] 도메인 외 감지 정확성 테스트

### 4.2 NON_ETHICAL (비윤리적 차단)
- [ ] **의도 학습 데이터**
  - [ ] [AI] NON_ETHICAL 의도 예시 100개 수집
    - 금전 요구, 욕설, 불법 행위 등

- [ ] **비윤리적 요청 필터**
  - [ ] [AI] 비윤리적 키워드 리스트
  - [ ] [Backend] 패턴 매칭 로직
  - [ ] [Backend] 즉시 차단 로직

- [ ] **경고 응답 및 로그**
  - [ ] [AI] 경고 메시지 템플릿
  - [ ] [Backend] 보안 로그 기록 (IP, 타임스탬프)

- [ ] **테스트**
  - [ ] [Backend] 비윤리적 요청 차단 테스트
  - [ ] [Backend] 로그 기록 검증

### 4.3 시스템 최적화
- [ ] **성능 최적화**
  - [ ] [Backend] 데이터베이스 쿼리 최적화
  - [ ] [Backend] 인덱스 설정
  - [ ] [Backend] 캐싱 전략 개선
  - [ ] [Frontend] CDN 설정 (프론트엔드)

- [ ] **보안 강화**
  - [ ] [Backend] HTTPS 설정
  - [ ] [Backend] API 속도 제한 (rate limiting)
  - [ ] [Backend] CSRF 방지
  - [ ] [Frontend] XSS 방지
  - [ ] [Backend] SQL Injection 방지

- [ ] **모니터링 및 로깅**
  - [ ] [Backend] 애플리케이션 로그 (Winston, Loguru)
  - [ ] [Backend] 에러 추적 (Sentry)
  - [ ] [Backend] 성능 모니터링 (New Relic, Datadog)
  - [ ] [Backend] 알림 설정 (Slack, 이메일)

### 4.4 프로덕션 배포
- [ ] **배포 환경 설정**
  - [ ] [Backend] 클라우드 플랫폼 선택 (AWS, GCP, Azure)
  - [ ] [Backend] 도메인 설정
  - [ ] [Backend] SSL 인증서 설정
  - [ ] [Backend] 데이터베이스 프로덕션 설정

- [ ] **CI/CD 파이프라인**
  - [ ] [Backend] GitHub Actions 또는 GitLab CI 설정
  - [ ] [Backend] 자동 테스트 실행
  - [ ] [Backend] 자동 배포 설정
  - [ ] [Backend] 롤백 전략

- [ ] **문서화**
  - [ ] [Backend] 사용자 가이드
  - [ ] [Backend] 관리자 가이드
  - [ ] [Backend] API 문서
  - [ ] [Backend] 트러블슈팅 가이드

- [ ] **테스트**
  - [ ] [Backend] 프로덕션 환경 smoke 테스트
  - [ ] [Backend] 부하 테스트 (Locust, JMeter)
  - [ ] [Backend] 보안 테스트

---

## 📋 5단계: 지속적 개선 (Ongoing)

### 5.1 피드백 기반 모델 개선
- [ ] [AI] 월간 피드백 데이터 분석
- [ ] [AI] 의도 분류 정확도 개선
- [ ] [AI] 저품질 응답 패턴 분석
- [ ] [AI] Few-shot 예시 업데이트
- [ ] [AI] LLM 프롬프트 최적화

### 5.2 데이터 업데이트
- [ ] [Backend] **Paper DB**: 주간 PubMed 업데이트
- [ ] [AI] **Welfare DB**: 분기별 복지 정보 업데이트
- [ ] [AI] **Diet DB**: 월간 식단 정보 업데이트
- [ ] [AI] **Policy DB**: 가이드라인 개정 시 업데이트

### 5.3 신규 기능 개발
- [ ] [Backend] 사용 패턴 분석
- [ ] [Frontend] 사용자 피드백 수집
- [ ] [AI] 신규 의도 추가 검토
  - MEDICATION_INFO (약물 정보)
  - SYMPTOM_TRACKER (증상 추적)
- [ ] [Backend] A/B 테스트

### 5.4 품질 지표 모니터링
- [ ] **품질 지표**
  - [ ] [AI] 휴먼 피드백 "Good" 비율 > 70%
  - [ ] [AI] 휴먼 피드백 "Bad" 비율 < 15%
  - [ ] [AI] 의도 분류 정확도 > 90%

- [ ] **사용 지표**
  - [ ] [Backend] 일일 활성 사용자 500명 이상
  - [ ] [Backend] 세션당 질문 수 평균 2.5개 이상
  - [ ] [Backend] 재방문 사용자 비율 > 40%

- [ ] **성능 지표**
  - [ ] [Backend] P95 응답 시간 < 25초
  - [ ] [Backend] 시스템 오류율 < 1%
  - [ ] [Backend] PubMed API 성공률 > 98%

- [ ] **비즈니스 지표**
  - [ ] [Backend] 쿼리당 비용 < $0.10
  - [ ] [Backend] 피드백 완료율 > 60%
  - [ ] [AI] 품질 개선 추세 분기별 +5%

---

## 🎓 학습 및 참고 자료

### 기술 문서
- [ ] [Backend] FastAPI 공식 문서 학습
- [ ] [Frontend] React 공식 문서 학습
- [ ] [AI] LangChain 공식 문서 학습
- [ ] [Backend] 벡터 DB 공식 문서 (Pinecone/Weaviate/Qdrant)
- [ ] [Backend] PubMed API 문서

### 의료 자료
- [ ] [AI] 대한신장학회 CKD 가이드라인
- [ ] [AI] KDIGO CKD 가이드라인
- [ ] [AI] 식품영양성분표
- [ ] [AI] 보건복지부 복지 정보

### 프로젝트 문서
- [ ] [AI] PRD (prd_ko.md) 검토
- [ ] [AI] 기능 명세서 (fuction specification.md) 검토
- [ ] [Backend] API 문서 작성 및 유지
- [ ] [Backend] 아키텍처 다이어그램 작성

---

## ✅ 완료 기준

### 1단계 완료 기준
- [ ] [AI] 3개 의도 (MEDICAL_INFO, RESEARCH, POLICY) 90% 이상 정확도
- [ ] [Backend] 질문 → 요약 파이프라인 작동
- [ ] [Backend] 응급 상황 감지 시스템 작동
- [ ] [Backend] 응답 시간 < 25초
- [ ] [Backend] API 문서 작성 완료

### 2단계 완료 기준
- [ ] [AI] 6개 의도 모두 작동
- [ ] [Backend] 건강 기록 저장/조회 기능 작동
- [ ] [Backend] 4단계 복지 안내 시스템 작동
- [ ] [Frontend] 프론트엔드 기본 UI 완성

### 3단계 완료 기준
- [ ] [AI] 8개 의도 모두 작동
- [ ] [Backend] 퀴즈 시스템 작동
- [ ] [Frontend] 휴먼 피드백 인터페이스 완성
- [ ] [Frontend] 피드백 통계 대시보드 작동

### 4단계 완료 기준
- [ ] [AI] 10개 의도 모두 작동
- [ ] [Backend] 비윤리적 요청 차단 시스템 작동
- [ ] [Backend] 프로덕션 배포 완료
- [ ] [Backend] 모니터링 시스템 작동

### 5단계 완료 기준
- [ ] [Backend] 모든 품질 지표 목표 달성
- [ ] [Backend] 월간 데이터 업데이트 프로세스 확립
- [ ] [AI] 피드백 기반 개선 사이클 확립

---

## 📝 주의사항

### 의료 안전
- ⚠️ **절대 의학적 진단이나 치료 권장 금지**
- ⚠️ **응급 상황 시 즉시 119 안내**
- ⚠️ **모든 의료 정보는 참고용이며 의사 상담 권고**

### 데이터 보안
- 🔒 환자 건강 기록 암호화 필수
- 🔒 API 키 및 비밀번호 .env 파일 관리
- 🔒 개인정보 보호법 (PIPA) 준수
- 🔒 HIPAA 고려사항 검토

### 품질 관리
- ✅ 모든 의료 정보는 전문가 검증
- ✅ 정기적인 피드백 데이터 분석
- ✅ 지속적인 정확도 모니터링
- ✅ 사용자 피드백 적극 반영

---

**마지막 업데이트**: 2025-11-05
**문서 버전**: 1.0
**작성자**: Claude Code
