<!--
Sync Impact Report
==================
Version change: 1.1.0 → 1.2.0
Modified sections:
  - Development Workflow: Added GitHub Collaboration Rules (커밋/Push/PR 필수 규칙)
Added sections:
  - GitHub Collaboration Rules (VII. GitHub First)
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (no changes needed)
  - .specify/templates/spec-template.md ✅ (no changes needed)
  - .specify/templates/tasks-template.md ✅ (no changes needed)
Follow-up TODOs:
  - None
-->

# KimpTrade Constitution

## Core Principles

### I. Safety First (안전 우선)

거래 시스템의 안전성이 모든 기능보다 우선한다.

- 손실 상태에서 청산 금지: 순이익 > 0 조건이 충족될 때만 청산 허용
- One-leg Failure 즉시 복구: 한쪽 거래소만 체결 시 자동 복구 로직 필수
- 일일 손실 한도 5% 초과 시 신규 진입 차단
- 환율 데이터 2분 이내 유효성 검증 필수
- 테스트넷에서 충분히 검증 후 실거래 진행

**Rationale**: 자동화 거래 시스템에서 예기치 않은 손실은 치명적이므로, 안전장치가 모든 기능 구현보다 우선되어야 한다.

### II. Concurrent Execution (동시 실행)

델타 뉴트럴 전략의 핵심은 업비트와 바이낸스 주문의 동시 실행이다.

- `asyncio.gather()`를 사용한 병렬 주문 실행 필수
- 주문 실행 지연 500ms 이내 목표
- 양측 거래소 체결 확인 후에만 포지션 상태 업데이트
- 부분 체결 시나리오에 대한 명확한 처리 로직 구현

**Rationale**: 김프 차익거래는 두 거래소 간 가격 차이를 이용하므로, 시간 지연이 손실로 직결된다.

### III. Code Quality (코드 품질)

유지보수 가능한 프로덕션 코드를 작성한다.

- Type hints: 모든 함수 시그니처에 필수
- Docstring: Google style, 모든 public 함수에 필수
- 비동기: 거래소 API 호출은 반드시 async/await 사용
- 로깅: loguru를 사용한 구조화된 로깅
- 포맷터: black (line-length=100), isort (profile=black)

**Rationale**: 24/7 운영 시스템은 버그 발생 시 즉각적인 금전 손실이 발생하므로, 코드 품질이 시스템 안정성에 직결된다.

### IV. Security (보안)

API 키와 민감 정보는 철저히 보호한다.

- API 키는 환경변수(.env)로만 관리, 절대 커밋 금지
- Webhook Secret 검증: 모든 수신 요청에 대해 필수
- 거래소 API 출금 권한 비활성화 필수
- 가능하면 API IP 화이트리스트 설정

**Rationale**: 거래소 API 키 유출은 자산 탈취로 직결되므로, 보안은 타협할 수 없다.

### V. Simplicity (단순성)

복잡한 인프라 없이 작동하는 시스템을 지향한다.

- "완벽한 시스템보다 작동하는 시스템"
- TradingView가 할 수 있는 건 TradingView에게 위임
- 서버는 주문 실행과 리스크 관리에 집중
- YAGNI 원칙: 현재 필요한 기능만 구현, 미래 요구사항 예측 금지
- 과도한 추상화 지양: 3번 이상 반복되지 않으면 추상화하지 않음

**Rationale**: MVP 단계에서 복잡성은 개발 속도와 안정성을 모두 저하시킨다.

### VI. TDD Cycle (NON-NEGOTIABLE)

모든 기능 구현은 TDD 사이클을 따른다.

```
1. RED:   테스트 먼저 작성 → 실패 확인
2. GREEN: 최소한의 코드로 테스트 통과
3. REFACTOR: 코드 정리 (테스트는 계속 통과)
```

- 테스트 없는 코드는 머지 금지
- 테스트가 먼저, 구현이 나중
- 핵심 비즈니스 로직(진입/청산/포지션 관리)은 반드시 테스트 커버리지 확보
- 테스트 실패 상태에서 다른 작업 진행 금지

**Rationale**: 거래 시스템에서 버그는 곧 금전 손실이다. TDD는 버그를 사전에 방지하는 가장 효과적인 방법이다.

### VII. GitHub First (GitHub 우선)

모든 작업은 GitHub에서 추적 가능해야 한다.

- **커밋**: 작업 완료 즉시, 작은 단위로 자주
- **Push**: 커밋 3-5개마다, 또는 기능 완료 시 즉시
- **PR 생성**: Push 후 기능 단위로 PR 생성하여 리뷰 가능하게
- 로컬에만 코드가 있는 상태 금지: 항상 GitHub에 동기화
- Claude 작업 시 반드시 커밋 → Push → PR 사이클 수행

**Rationale**: GitHub에서 모니터링하고 리뷰할 수 있어야 협업과 품질 관리가 가능하다. 로컬에만 있는 코드는 검토도, 복구도 불가능하다.

## Trading Safety Requirements

거래 시스템 특화 안전 요구사항:

| 항목 | 기준 | 동작 |
|------|------|------|
| 일일 손실 한도 | 5% (100만원) | 초과 시 신규 진입 차단 |
| 최대 드로다운 | 20% | 경고 알림 |
| 환율 유효성 | 2분 이내 | 만료 시 진입 차단 |
| 신호 중복 방지 | 1분 쿨다운 | 무시 |
| 손실 청산 | 금지 | 순이익 > 0만 청산 |

One-leg Failure 복구 전략:
- 업비트만 체결: 바이낸스 재시도 3회 → 실패 시 업비트 매도
- 바이낸스만 체결: 업비트 재시도 3회 → 실패 시 바이낸스 청산

## Development Workflow

### 브랜치 전략

```
main ────────────────────► 프로덕션 (완벽하게 검증된 코드만)
  │                         - 직접 커밋 금지
  │                         - dev에서 테스트 완료 후에만 머지
  │
  └─► dev ──────────────► 개발 통합 (자유롭게 테스트)
        │                   - 기능 테스트 및 통합 검증
        │                   - CI 통과 필수
        │
        └─► feature/* ──► 기능 개발 (마음대로 작업)
            L-work          - 자유로운 실험 가능
            H-work          - 실패해도 OK
            P-work          - 작업 완료 후 dev로 머지
```

### GitHub 협업 규칙 (필수 준수)

모든 문서/코드 작업 후 반드시 GitHub에 반영:

```
작업 완료 → 커밋 → Push → PR 생성
```

**빈도 원칙**:
```
커밋: 가장 자주 (작은 단위, 1기능 = 1커밋)
  ↓
Push: 커밋 3-5개마다 또는 기능 완료 시
  ↓
PR: Push 후 기능 단위로 생성 (dev 브랜치로)
```

**Claude 작업 시 필수**:
1. 작업 완료 후 `git add` + `git commit`
2. 즉시 `git push`
3. 기능 완료 시 PR 생성 (`gh pr create`)

**커밋 형식**:
```
<type>(<scope>): <description>

Types: feat, fix, docs, refactor, test, chore
```

**예시**:
```
feat(exchange): implement upbit market_buy
test(exchange): add upbit market_buy tests
fix(webhook): handle empty payload gracefully
docs(spec): add storage integration specification
```

### 작업 기록 (트랙킹)

모든 작업은 추적 가능해야 한다:

- 커밋 메시지에 무엇을 했는지 명확히 기록
- PR 생성 시 변경사항 요약 필수
- 복잡한 로직은 코드 주석 또는 docs에 기록
- 설정 변경, 의존성 추가는 반드시 커밋 메시지에 명시

## Issue Management

문제나 특이사항은 즉시 이슈로 등록한다.

### 즉시 이슈 등록 필요한 경우

1. **버그 발견**: 재현 방법, 예상 동작, 실제 동작 기록
2. **스키마 변경**: DB/API 스키마 변경 전 이슈 생성
3. **Breaking Change**: 기존 기능 호환성 깨지는 변경
4. **의존성 변경**: 라이브러리 추가/삭제/업데이트
5. **환경 설정 변경**: .env, config 수정 사항
6. **아이디어/개선점**: 나중에 할 일도 이슈로 기록

### 이슈 형식

```markdown
## 문제/요청
[무엇이 문제인지 또는 무엇을 원하는지]

## 재현 방법 (버그인 경우)
1. ...
2. ...

## 예상 동작
[어떻게 동작해야 하는지]

## 관련 파일
[영향받는 파일 목록]
```

## Version Control & Recovery

실수는 할 수 있지만, 언제든 돌아갈 수 있어야 한다.

### 버전 관리 원칙

1. **작은 커밋**: 큰 변경을 한 번에 하지 말고, 작게 나눠서 커밋
2. **의미 있는 커밋 메시지**: 나중에 찾을 수 있도록 명확하게
3. **자주 push**: 로컬에만 있으면 복구 불가
4. **태그 활용**: 중요한 마일스톤에는 태그 추가 (`v0.1.0`, `v0.2.0`)

### 복구 시나리오

| 상황 | 해결 방법 |
|------|----------|
| 방금 커밋 취소 | `git reset --soft HEAD~1` |
| 특정 파일 되돌리기 | `git checkout <commit> -- <file>` |
| 브랜치 잘못 작업 | `git stash` → 올바른 브랜치로 이동 → `git stash pop` |
| 완전히 망함 | `git reflog`로 이전 상태 찾기 |

### 위험한 명령어 (주의!)

- `git push --force`: 절대 main/dev에서 사용 금지
- `git reset --hard`: 작업 내용 사라짐, 신중히
- `git clean -fd`: 추적 안 된 파일 전부 삭제

## Governance

이 Constitution은 KimpTrade 프로젝트의 최상위 개발 원칙이다.

**Amendment Procedure**:
1. 원칙 변경은 문서화 필수
2. 기존 코드와의 호환성 검토
3. 변경 시 버전 업데이트 (SemVer)

**Versioning Policy**:
- MAJOR: 원칙 삭제 또는 비호환적 재정의
- MINOR: 새 원칙 추가 또는 주요 확장
- PATCH: 명확화, 오타 수정, 비의미적 개선

**Compliance**:
- 모든 PR은 이 원칙 준수 여부 검증
- 원칙 위반 코드는 머지 금지
- 런타임 가이드: `CLAUDE.md` 참조

**Version**: 1.2.0 | **Ratified**: 2025-12-13 | **Last Amended**: 2025-12-15
