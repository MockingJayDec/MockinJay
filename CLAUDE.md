**워크플로우 규칙**:

## 작업 단위 정의
- **Milestone**: 주요 릴리즈 단계 (## 헤더, 예: `## Milestone 1: 핵심 의도 MVP`)
- **Feature**: PR 생성 단위 (### 헤더, 예: `### Feature 1.3: 질문 의도 예측 시스템`)
- **Task**: Issue 생성 단위 (체크박스, 예: `- [ ] Task: [Backend] LLM 호출 함수 구현`)

## Feature 시작 시:
1. TASK.md에서 Feature 확인
2. Feature 브랜치 생성
   - 브랜치 명명: `feature/{feature-slug}`
   - 예: `feature/intent-prediction` (Feature 1.3)
   - 예: `feature/vector-db-system` (Feature 1.4)

## 각 Task 작업 시:
1. GitHub Issue 생성
   - 제목: Task 내용 (예: `[Backend] LLM 호출 함수 구현`)
   - Feature 브랜치에서 작업
2. 작업 진행
   - Feature 브랜치에서 직접 커밋
   - 커밋 메시지에 Issue 참조 (예: `feat: Implement LLM client (#11)`)
3. Task 완료
   - TASK.md 체크표시 (Edit 도구 사용)
   - Issue에 완료 내역 기록

## Feature 완료 시:
1. 해당 Feature의 **모든 Task가 완료**되었는지 확인
2. **Pull Request 생성**
   - 제목: Feature 이름 사용
   - 본문: 완료된 모든 Task(Issue) 나열
   - 관련된 모든 Issue 자동 닫기
   - 예시:
     ```
     Title: Feature 1.3: 질문 의도 예측 시스템

     ## 완료된 작업
     - Closes #10: Few-shot 프롬프트 작성
     - Closes #11: LLM 호출 함수 구현
     - Closes #12: 의도 분류 엔드포인트
     - Closes #13: 응급 상황 감지
     - Closes #14: 의학적 판단 차단
     - Closes #15: 테스트 작성
     ```
3. Base branch: `dev` (또는 지정된 브랜치)

## 예시 워크플로우
```
### Feature 1.3: 질문 의도 예측 시스템  ← Feature (PR 단위)
│
├─ Branch: feature/intent-prediction    ← Feature 브랜치
│
├─ Issue #10: [AI] Few-shot 프롬프트 작성      ← Task
├─ Issue #11: [Backend] LLM 호출 함수 구현      ← Task
├─ Issue #12: [Backend] 의도 분류 엔드포인트    ← Task
│
└─ (모든 Task 완료) → PR: Feature 1.3: 질문 의도 예측 시스템
                        - Closes #10, #11, #12
```

## 주의사항
- Feature당 하나의 브랜치만 생성 (Task별 브랜치 X)
- Task는 Issue로 추적, Feature 브랜치에서 작업
- Feature 완료 시 PR 생성 (모든 관련 Issue 자동 종료)
- Milestone은 여러 Feature PR이 병합되면 완료 