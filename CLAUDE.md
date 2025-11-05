**워크플로우 규칙**:

## 🚨 중요: Base Branch 설정
- **모든 Feature 브랜치는 `dev`에서 생성**
- **모든 PR은 `dev`를 base로 설정**
- **절대 `main`으로 직접 PR 생성 금지**

## 작업 단위 정의
- **Milestone**: 주요 릴리즈 단계 (## 헤더)
- **Feature**: PR 생성 단위 (### 헤더)
- **Task**: Issue 생성 단위 (체크박스)

## Feature 시작 시:
1. **반드시 `dev` 브랜치에서 시작**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/{feature-slug}
   ```
2. Feature 브랜치 생성
   - 예: `feature/intent-prediction`
   - 예: `feature/vector-db-system`

## 각 Task 작업 시:
1. GitHub Issue 생성
   - 제목: Task 내용 (예: `[Backend] LLM 호출 함수 구현`)
2. Feature 브랜치에서 작업 및 커밋
3. TASK.md 체크표시 (Edit 도구 사용)

## Feature 완료 시:
1. **PR 생성 전 확인사항**:
   - ✅ Base branch가 `dev`인지 확인
   - ✅ 모든 Task 완료 여부 확인
   - ✅ 테스트 통과 여부 확인

2. **PR 생성**:
   ```bash
   gh pr create --base dev --title "Feature X.X: 기능명"
   ```
   - **반드시 `--base dev` 옵션 사용**
   - Closes #N으로 모든 Issue 참조

## 예시 워크플로우
```
dev 브랜치
│
├─ feature/vector-db-system (Feature 1.4)
│  ├─ Issue #1: 벡터 DB 선택
│  ├─ Issue #2: 라우팅 로직
│  └─ PR → dev (NOT main!)
│
└─ feature/rag-engine (Feature 1.6)
   ├─ Issue #3: RAG 검색 로직
   └─ PR → dev (NOT main!)
```

## ⚠️ 실수 방지 체크리스트
- [ ] `git branch`로 현재 브랜치 확인
- [ ] PR 생성 시 `--base dev` 명시
- [ ] PR 생성 후 base branch 재확인