# Contributing Guide

## 개요

김치프리미엄 트레이딩 플랫폼에 기여해 주셔서 감사합니다.
이 문서는 프로젝트에 기여하는 방법을 안내합니다.

---

## 🚀 Quick Start

### 1. Repository Clone

```bash
git clone https://github.com/vsun410/trading-platform-order.git
cd trading-platform-order
```

### 2. 개발 환경 설정

```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발용 의존성
```

### 3. 브랜치 생성

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

---

## 📌 Git Workflow

### Branch Strategy

```
main     ← 프로덕션 (최종 승인된 코드만)
  ↑
dev      ← 개발/통합 테스트
  ↑
feature/* ← 기능 개발, TDD 사이클
design/*  ← 디자인 작업
fix/*     ← 버그 수정
```

> 📖 상세 내용: [docs/GIT_WORKFLOW.md](./docs/GIT_WORKFLOW.md)

### 브랜치 네이밍

| Prefix | 용도 | 예시 |
|--------|------|------|
| `feature/` | 새 기능 | `feature/realtime-pnl` |
| `design/` | 디자인 작업 | `design/kinetic-buttons` |
| `fix/` | 버그 수정 | `fix/fee-calculation` |
| `refactor/` | 리팩토링 | `refactor/service-layer` |
| `test/` | 테스트 추가 | `test/order-service` |
| `docs/` | 문서 수정 | `docs/api-guide` |

---

## 💻 Development

### TDD Cycle

Feature 브랜치에서는 TDD 방식으로 개발합니다.

```bash
# 1. RED - 실패하는 테스트 작성
git commit -m "test: [RED] Add test for feature X"

# 2. GREEN - 테스트 통과하는 최소 코드
git commit -m "feat: [GREEN] Implement feature X"

# 3. REFACTOR - 코드 개선
git commit -m "refactor: [REFACTOR] Improve feature X implementation"
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 테스트
pytest tests/test_order_service.py

# 커버리지 포함
pytest --cov=src --cov-report=html
```

### 코드 스타일

```bash
# 포맷팅
black src/ tests/

# 린트
flake8 src/ tests/

# 타입 체크
mypy src/
```

---

## 🎨 Design Guidelines

### Kinetic Minimalism

모든 UI 컴포넌트는 **Kinetic Minimalism** 스타일을 따릅니다.

#### 필수 요소

- ✅ 중성 팔레트 (white, black, greys)
- ✅ Electric Blue (#0066FF) 액센트
- ✅ 방향성 요소 (diagonal, gradient, streak)
- ✅ 방향성 그림자 (45° offset)
- ✅ 타이트한 자간

#### 금지 사항

- ❌ Glassmorphism
- ❌ Neumorphism / Soft UI
- ❌ Claymorphism
- ❌ Textures / Patterns
- ❌ Pastel colors
- ❌ Full symmetry

> 📖 상세 내용: [docs/DASHBOARD.md](./docs/DASHBOARD.md)

---

## 📝 Commit Convention

### Format

```
<type>: <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `design` | 디자인 변경 |
| `refactor` | 코드 리팩토링 |
| `test` | 테스트 추가/수정 |
| `docs` | 문서 수정 |
| `style` | 코드 포맷팅 |
| `chore` | 빌드/설정 변경 |

### Examples

```bash
# 기능 추가
feat: Add real-time price monitoring

# 버그 수정
fix: Correct fee calculation for Binance futures

# 디자인 변경
design: [PricePanel] Apply 45deg gradient to kimp card

# TDD 커밋
test: [RED] Add unit test for OrderService.execute_entry
feat: [GREEN] Implement OrderService.execute_entry
refactor: [REFACTOR] Extract fee calculation to utility
```

---

## 🔄 Pull Request

### PR 생성 전 체크리스트

- [ ] dev 브랜치와 동기화 (`git rebase origin/dev`)
- [ ] 모든 테스트 통과 (`pytest`)
- [ ] 코드 스타일 검사 통과 (`black`, `flake8`)
- [ ] 커밋 메시지 컨벤션 준수
- [ ] 관련 문서 업데이트

### PR 프로세스

```
1. feature/* → dev (PR)
   - 코드 리뷰
   - 테스트 통과 확인
   - 머지

2. dev → main (PR)
   - 최종 승인 필요
   - 통합 테스트 완료
   - 머지
```

### PR 템플릿

PR 생성 시 자동으로 템플릿이 적용됩니다.
모든 항목을 성실히 작성해 주세요.

---

## 📋 Issue

### Issue 생성

- **🐛 Bug Report**: 버그 발견 시
- **✨ Feature Request**: 새 기능 제안
- **🎨 Design Update**: 디자인 변경 제안

### Issue 라벨

| Label | Description |
|-------|-------------|
| `bug` | 버그 |
| `enhancement` | 기능 개선 |
| `design` | 디자인 관련 |
| `documentation` | 문서 관련 |
| `good first issue` | 입문자용 |
| `help wanted` | 도움 필요 |
| `priority: high` | 높은 우선순위 |
| `priority: low` | 낮은 우선순위 |

---

## 📚 Documentation

### 문서 구조

```
docs/
├── DASHBOARD.md       # UI/UX 스펙 (Kinetic Minimalism)
├── DATABASE.md        # DB 스키마
├── API_INTEGRATION.md # 거래소 API
├── DEPLOYMENT.md      # 배포 가이드
└── GIT_WORKFLOW.md    # Git 워크플로우
```

### 문서 수정 시

1. 관련 Issue 생성 또는 참조
2. `docs/` 브랜치에서 작업
3. PR 생성

---

## ❓ Questions

질문이 있으시면 Issue를 생성해 주세요.

---

## 📄 License

이 프로젝트는 MIT 라이선스를 따릅니다.
