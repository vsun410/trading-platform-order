# Git Workflow & Version Control

## 개요

이 문서는 김치프리미엄 트레이딩 플랫폼의 Git 브랜치 전략과 버전 관리 워크플로우를 정의합니다.
Claude Code의 Git Graph 기능을 활용하여 체계적인 버전 관리를 수행합니다.

---

## 🌳 Branch Strategy

```
                                    ┌─────────────────────────────────────┐
                                    │            PRODUCTION               │
                                    │                                     │
    ┌───────────────────────────────┤             main                    │
    │                               │                                     │
    │                               │  ✅ 최종 승인된 코드만              │
    │                               │  ✅ 배포 가능 상태 유지             │
    │                               │  ✅ 직접 커밋 금지                  │
    │                               └─────────────────────────────────────┘
    │                                              ▲
    │                                              │ PR + Approval
    │                                              │
    │                               ┌─────────────────────────────────────┐
    │                               │           DEVELOPMENT               │
    │                               │                                     │
    │   ┌───────────────────────────┤              dev                    │
    │   │                           │                                     │
    │   │                           │  🧪 통합 테스트                     │
    │   │                           │  🔍 코드 리뷰                       │
    │   │                           │  ✅ 기능 통합                       │
    │   │                           └─────────────────────────────────────┘
    │   │                                          ▲
    │   │                                          │ PR + Review
    │   │                                          │
    │   │                           ┌─────────────────────────────────────┐
    │   │                           │            FEATURES                 │
    │   │                           │                                     │
    │   │   ┌───────────────────────┤  feature/*, fix/*, design/*        │
    │   │   │                       │                                     │
    │   │   │                       │  🔨 TDD 사이클                      │
    │   │   │                       │  🎨 디자인 작업                     │
    │   │   │                       │  🐛 버그 수정                       │
    │   │   │                       │  ⚡ 자유로운 실험                   │
    │   │   │                       └─────────────────────────────────────┘
    │   │   │
    │   │   │
    ▼   ▼   ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                           BRANCH FLOW                                   │
│                                                                         │
│   feature/* ──PR──▶ dev ──PR+Approval──▶ main                          │
│                                                                         │
│   1. feature에서 개발/TDD                                               │
│   2. dev로 PR → 코드 리뷰 → 통합 테스트                                 │
│   3. main으로 PR → 최종 승인 → 머지                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📌 Branch 상세 정의

### 1. `main` - Production Branch

```yaml
목적: 프로덕션 배포 가능한 안정적인 코드
보호 규칙:
  - 직접 push 금지
  - PR을 통해서만 머지
  - 최소 1명의 승인 필요 (본인)
  - CI/CD 통과 필수
머지 조건:
  - dev에서 충분한 테스트 완료
  - 모든 기능 정상 동작 확인
  - 문서 업데이트 완료
```

### 2. `dev` - Development Branch

```yaml
목적: 기능 통합 및 테스트
허용 작업:
  - feature 브랜치 머지
  - 통합 테스트
  - 버그 수정
  - 코드 리뷰
머지 조건:
  - feature 브랜치에서 PR
  - 코드 리뷰 통과
  - 테스트 통과
```

### 3. `feature/*` - Feature Branches

```yaml
목적: 새 기능 개발, 디자인 작업, TDD 사이클
네이밍 규칙:
  - feature/기능명     (새 기능)
  - design/컴포넌트명   (디자인 작업)
  - fix/버그명         (버그 수정)
  - refactor/대상      (리팩토링)
  - test/테스트명      (테스트 추가)
생명주기:
  - dev에서 분기
  - 작업 완료 후 dev로 PR
  - 머지 후 삭제
```

---

## 🎨 Design Version Control

디자인 관련 변경사항은 특별히 관리합니다.

### Design Branch Naming

```bash
# 컴포넌트별 디자인 작업
design/header-kinetic-style
design/price-panel-gradient
design/order-panel-buttons
design/pnl-card-animation

# 전체 테마 작업
design/kinetic-minimalism-v1
design/kinetic-minimalism-v2
design/color-palette-update

# 반응형/레이아웃
design/responsive-mobile
design/layout-grid-system
```

### Design Commit Convention

```bash
# 커밋 메시지 형식
design: [컴포넌트] 변경 내용

# 예시
design: [Header] Add diagonal accent bar with skewX transform
design: [PricePanel] Implement 45deg gradient on kimp card
design: [OrderPanel] Add kinetic button hover animation
design: [Global] Update color palette to Kinetic Minimalism
design: [Typography] Apply Inter font with tight letter-spacing
```

### Design Review Checklist

```markdown
## Design PR Checklist

### Kinetic Minimalism 준수 여부
- [ ] 중성 팔레트 사용 (white, black, greys)
- [ ] Electric Blue (#0066FF) 액센트만 사용
- [ ] 방향성 요소 포함 (diagonal, gradient, streak)
- [ ] 방향성 그림자 적용 (45° offset)
- [ ] 타이트한 자간 적용

### 금지 사항 확인
- [ ] Glassmorphism 미사용
- [ ] Soft/Neumorphism 미사용
- [ ] 파스텔 색상 미사용
- [ ] 완전 대칭 레이아웃 미사용

### 기능 확인
- [ ] 기존 기능 정상 동작
- [ ] 반응형 레이아웃 확인
- [ ] 브라우저 호환성 확인
```

---

## 🔄 TDD Cycle in Feature Branch

Feature 브랜치에서의 TDD 워크플로우:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TDD CYCLE                                       │
│                                                                         │
│    ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐     │
│    │  RED    │ ───▶ │  GREEN  │ ───▶ │REFACTOR │ ───▶ │ COMMIT  │     │
│    │         │      │         │      │         │      │         │     │
│    │ 실패    │      │ 통과    │      │ 개선    │      │ 저장    │     │
│    │ 테스트  │      │ 코드    │      │ 코드    │      │         │     │
│    │ 작성    │      │ 작성    │      │ 작성    │      │         │     │
│    └─────────┘      └─────────┘      └─────────┘      └─────────┘     │
│         │                                                   │          │
│         └───────────────────────────────────────────────────┘          │
│                            반복                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### TDD Commit Convention

```bash
# 커밋 메시지 형식
test: [RED] 테스트 설명
feat: [GREEN] 기능 구현
refactor: [REFACTOR] 개선 내용

# 예시
test: [RED] Add unit test for PriceService.get_current_prices
feat: [GREEN] Implement PriceService.get_current_prices
refactor: [REFACTOR] Extract price formatting to utility function
```

---

## 📝 Commit Convention

### Commit Types

| Type | Description | Example |
|------|-------------|--------|
| `feat` | 새 기능 추가 | `feat: Add real-time price monitoring` |
| `fix` | 버그 수정 | `fix: Correct fee calculation formula` |
| `design` | 디자인 변경 | `design: Update button to kinetic style` |
| `refactor` | 코드 리팩토링 | `refactor: Extract common utilities` |
| `test` | 테스트 추가/수정 | `test: Add integration test for order flow` |
| `docs` | 문서 수정 | `docs: Update API documentation` |
| `style` | 코드 포맷팅 | `style: Apply black formatter` |
| `chore` | 빌드/설정 변경 | `chore: Update dependencies` |

### Commit Message Format

```
<type>: <subject>

[optional body]

[optional footer]
```

### Examples

```bash
# 간단한 커밋
feat: Add position panel component

# 상세 커밋
feat: Add real-time PnL calculation

- Implement gross PnL calculation
- Add fee deduction logic
- Include target progress indicator

Closes #42

# 디자인 커밋
design: [PnLPanel] Apply Kinetic Minimalism style

- Add 45deg gradient to net profit card
- Implement motion streak animation
- Update typography to Inter font
- Apply directional shadow (4px 8px 16px)

Related to #38
```

---

## 🚀 Workflow Commands

### Claude Code에서 사용할 Git 명령어

#### 1. 새 Feature 시작

```bash
# dev에서 최신 코드 가져오기
git checkout dev
git pull origin dev

# 새 feature 브랜치 생성
git checkout -b feature/new-feature-name

# 또는 디자인 작업
git checkout -b design/component-name
```

#### 2. 작업 중 커밋

```bash
# 변경사항 확인
git status
git diff

# 스테이징 및 커밋
git add .
git commit -m "feat: Add feature description"

# 또는 TDD 사이클
git commit -m "test: [RED] Add test for feature"
git commit -m "feat: [GREEN] Implement feature"
git commit -m "refactor: [REFACTOR] Improve implementation"
```

#### 3. Feature 완료 후 PR 준비

```bash
# dev 최신 코드와 동기화
git fetch origin
git rebase origin/dev

# 충돌 해결 후
git push origin feature/new-feature-name
```

#### 4. PR 머지 후 정리

```bash
# dev로 이동
git checkout dev
git pull origin dev

# 머지된 브랜치 삭제
git branch -d feature/new-feature-name
git push origin --delete feature/new-feature-name
```

---

## 📊 Git Graph Visualization

### Claude Code Git Graph 활용

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Git Graph Example                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  main     ●─────────────────────────────────●─────────────▶            │
│           │                                 │                           │
│           │                                 │ merge PR #5               │
│           │                                 │                           │
│  dev      │  ●────●────●────●────●────●────●                           │
│           │  │         │              │                                 │
│           │  │         │ merge        │ merge                          │
│           │  │         │ feature/ui   │ design/kinetic                 │
│           │  │         │              │                                 │
│  feature  │  │    ●────●              │                                │
│  /ui      │  │    │    │              │                                │
│           │  │    │    TDD cycles     │                                │
│           │  │    │                   │                                │
│  design   │  │                   ●────●                                │
│  /kinetic │  │                   │    │                                │
│           │  │                   │    design iterations                │
│           │  │                   │                                     │
│           ●──┘                   └────────────────────────────────────▶│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 브랜치 상태 확인 명령어

```bash
# 그래프 형태로 히스토리 보기
git log --oneline --graph --all

# 브랜치 목록 확인
git branch -a

# 현재 브랜치 상태
git status

# 리모트와 차이 확인
git log origin/dev..HEAD
```

---

## 🔐 Branch Protection Rules

### GitHub 설정 (Repository Settings > Branches)

#### main 브랜치 보호 규칙

```yaml
Branch name pattern: main

Protect matching branches:
  ✅ Require a pull request before merging
    ✅ Require approvals: 1
    ✅ Dismiss stale pull request approvals when new commits are pushed
  
  ✅ Require status checks to pass before merging
    ✅ Require branches to be up to date before merging
  
  ✅ Do not allow bypassing the above settings
  
  ❌ Allow force pushes
  ❌ Allow deletions
```

#### dev 브랜치 보호 규칙

```yaml
Branch name pattern: dev

Protect matching branches:
  ✅ Require a pull request before merging
    ❌ Require approvals (선택적)
  
  ✅ Require status checks to pass before merging
  
  ❌ Allow force pushes
  ❌ Allow deletions
```

---

## 📋 PR Template

### `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## 📝 Description
<!-- 변경 사항에 대한 간단한 설명 -->

## 🔗 Related Issues
<!-- 관련 이슈 번호 -->
Closes #

## 📌 Type of Change
- [ ] 🆕 New feature (기능 추가)
- [ ] 🐛 Bug fix (버그 수정)
- [ ] 🎨 Design update (디자인 변경)
- [ ] ♻️ Refactoring (리팩토링)
- [ ] 📝 Documentation (문서 수정)
- [ ] 🧪 Test (테스트 추가)

## 🧪 Testing
<!-- 테스트 방법 및 결과 -->
- [ ] Unit tests passed
- [ ] Integration tests passed
- [ ] Manual testing completed

## 🎨 Design Changes (if applicable)
<!-- 디자인 변경 시 체크리스트 -->
- [ ] Kinetic Minimalism 가이드라인 준수
- [ ] 방향성 요소 포함
- [ ] 금지 사항 미사용 확인

## 📸 Screenshots (if applicable)
<!-- 변경 전/후 스크린샷 -->

## ✅ Checklist
- [ ] 코드 자체 리뷰 완료
- [ ] 문서 업데이트 완료
- [ ] 테스트 추가/수정 완료
```

---

## 🏷️ Release Tagging

### Semantic Versioning

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR: 호환되지 않는 API 변경
MINOR: 하위 호환 기능 추가
PATCH: 하위 호환 버그 수정
```

### Tag 생성

```bash
# main 브랜치에서 태그 생성
git checkout main
git pull origin main

# 태그 생성
git tag -a v1.0.0 -m "Release v1.0.0: Initial release"

# 태그 푸시
git push origin v1.0.0
```

### Release Notes Example

```markdown
## v1.0.0 - Initial Release

### ✨ Features
- Real-time price monitoring
- Manual order execution
- Position management
- PnL tracking

### 🎨 Design
- Kinetic Minimalism design system
- Responsive layout

### 📝 Documentation
- Complete API documentation
- Git workflow guide
```

---

## 📚 Quick Reference

### 일상 워크플로우

```bash
# 1. 하루 시작
git checkout dev
git pull origin dev

# 2. 작업 브랜치 생성
git checkout -b feature/today-task

# 3. 작업 & 커밋 (TDD)
git add .
git commit -m "test: [RED] Add test"
# ... 코드 작성 ...
git commit -m "feat: [GREEN] Implement feature"
# ... 리팩토링 ...
git commit -m "refactor: [REFACTOR] Improve code"

# 4. 푸시 & PR
git push origin feature/today-task
# GitHub에서 PR 생성

# 5. 머지 후 정리
git checkout dev
git pull origin dev
git branch -d feature/today-task
```

### 긴급 수정 (Hotfix)

```bash
# main에서 직접 분기
git checkout main
git pull origin main
git checkout -b fix/critical-bug

# 수정 후 바로 main으로 PR
git push origin fix/critical-bug
# PR → main (긴급 승인)

# dev에도 반영
git checkout dev
git merge main
git push origin dev
```

---

## 📎 관련 문서

- [DASHBOARD.md](./DASHBOARD.md) - UI/UX 스펙 (Kinetic Minimalism)
- [DATABASE.md](./DATABASE.md) - DB 스키마
- [API_INTEGRATION.md](./API_INTEGRATION.md) - 거래소 API
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 배포 가이드
