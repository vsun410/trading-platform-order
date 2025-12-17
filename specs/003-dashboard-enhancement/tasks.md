# Tasks: Dashboard Enhancement

**Input**: Design documents from `/specs/003-dashboard-enhancement/`
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: TDD Cycle 필수 (Constitution VI). 각 기능별 테스트 먼저 작성.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: FastAPI 대시보드 모듈 기본 구조 및 의존성 설정

- [ ] T001 Create dashboard_v2 directory structure per plan.md (src/dashboard_v2/, routers/, services/, models/, templates/, static/)
- [ ] T002 Add FastAPI, Jinja2, uvicorn dependencies to requirements.txt
- [ ] T003 [P] Create src/dashboard_v2/__init__.py
- [ ] T004 [P] Create src/dashboard_v2/routers/__init__.py
- [ ] T005 [P] Create src/dashboard_v2/services/__init__.py
- [ ] T006 [P] Create src/dashboard_v2/models/__init__.py
- [ ] T007 [P] Create tests/unit/test_pnl_service.py (empty file)
- [ ] T008 [P] Create tests/unit/test_position_service.py (empty file)
- [ ] T009 [P] Create tests/integration/test_dashboard_api.py (empty file)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 모든 User Story가 의존하는 핵심 인프라

**CRITICAL**: Phase 2 완료 전까지 User Story 작업 불가

### Config & App Shell

- [ ] T010 Create config.py with environment variables (SUPABASE_URL, FEE_RATE, etc.) in src/dashboard_v2/config.py
- [ ] T011 [P] Write unit test for app initialization in tests/unit/test_dashboard_app.py (RED)
- [ ] T012 Create FastAPI app shell in src/dashboard_v2/main.py (app instance, Jinja2 setup, CORS)
- [ ] T013 Verify app shell test passes (GREEN)

### Base Templates

- [ ] T014 [P] Create base.html with Neon Daybreak layout in src/dashboard_v2/templates/base.html
- [ ] T015 [P] Create neon-daybreak.css in src/dashboard_v2/static/css/neon-daybreak.css
- [ ] T016 [P] Create loading.html skeleton in src/dashboard_v2/templates/partials/loading.html
- [ ] T017 [P] Create error.html template in src/dashboard_v2/templates/partials/error.html

**Checkpoint**: Foundation ready - User Story implementation can begin

---

## Phase 3: User Story 1 - 실시간 데이터 로딩 수정 (Priority: P1) 🎯 MVP

**Goal**: 대시보드 접속 시 모든 데이터(김프율, 포지션, 환율, 시스템 상태)가 정상적으로 로딩되어 표시된다

**Independent Test**: 대시보드 접속 시 모든 섹션에 실제 데이터가 표시되고, 10초 이내 자동 갱신되는지 확인

### Tests for User Story 1

> **TDD: Write tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Write unit test for kimp_service.get_current_kimp() in tests/unit/test_kimp_service.py (RED)
- [ ] T019 [P] [US1] Write unit test for kimp_service.get_kimp_history() in tests/unit/test_kimp_service.py (RED)
- [ ] T020 [P] [US1] Write unit test for health_service.check_all() in tests/unit/test_health_service.py (RED)

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create kimp.py Pydantic model in src/dashboard_v2/models/kimp.py
- [ ] T022 [P] [US1] Create system.py Pydantic model in src/dashboard_v2/models/system.py
- [ ] T023 [US1] Implement kimp_service.py in src/dashboard_v2/services/kimp_service.py
- [ ] T024 [US1] Verify kimp_service tests pass (GREEN)
- [ ] T025 [US1] Implement health_service.py in src/dashboard_v2/services/health_service.py
- [ ] T026 [US1] Verify health_service tests pass (GREEN)
- [ ] T027 [P] [US1] Create api.py router with /api/kimp, /api/kimp/current, /api/health in src/dashboard_v2/routers/api.py
- [ ] T028 [US1] Create pages.py router with GET / in src/dashboard_v2/routers/pages.py
- [ ] T029 [US1] Create index.html with loading states in src/dashboard_v2/templates/index.html
- [ ] T030 [US1] Create dashboard.js with fetch and 10s auto-refresh in src/dashboard_v2/static/js/dashboard.js
- [ ] T031 [US1] Add error handling with retry button in src/dashboard_v2/static/js/dashboard.js
- [ ] T032 [P] [US1] Write integration test for /api/kimp endpoint in tests/integration/test_dashboard_api.py (RED)
- [ ] T033 [US1] Verify integration test passes (GREEN)

**Checkpoint**: User Story 1 완료 - 데이터 로딩 및 자동 갱신 독립 동작 확인

---

## Phase 4: User Story 2 - 매수 금액 표시 (Priority: P2)

**Goal**: 현재 포지션의 총 매수 금액(투자 원금)을 한눈에 확인할 수 있다

**Independent Test**: 오픈 포지션이 있을 때 매수 금액이 KRW 단위로 표시되는지 확인

### Tests for User Story 2

- [ ] T034 [P] [US2] Write unit test for position_service.get_position() in tests/unit/test_position_service.py (RED)
- [ ] T035 [P] [US2] Write unit test for position_service.calculate_invested_amount() in tests/unit/test_position_service.py (RED)

### Implementation for User Story 2

- [ ] T036 [P] [US2] Create position.py Pydantic model with total_invested_krw, upbit_invested, binance_invested_krw in src/dashboard_v2/models/position.py
- [ ] T037 [US2] Implement position_service.py with invested amount calculation in src/dashboard_v2/services/position_service.py
- [ ] T038 [US2] Verify position_service tests pass (GREEN)
- [ ] T039 [US2] Add /api/position endpoint in src/dashboard_v2/routers/api.py
- [ ] T040 [US2] Create positions_table.html with invested amount display in src/dashboard_v2/templates/components/positions_table.html
- [ ] T041 [US2] Create kpi_cards.html with total invested KRW card in src/dashboard_v2/templates/components/kpi_cards.html
- [ ] T042 [US2] Update dashboard.js to fetch and display position data in src/dashboard_v2/static/js/dashboard.js
- [ ] T043 [P] [US2] Write integration test for /api/position endpoint in tests/integration/test_dashboard_api.py (RED)
- [ ] T044 [US2] Verify integration test passes (GREEN)

**Checkpoint**: User Story 2 완료 - 매수 금액 표시 독립 동작 확인

---

## Phase 5: User Story 3 - 수익 분기점 표시 (Priority: P2)

**Goal**: 현재 포지션의 수익 분기점(Breakeven Point)을 확인할 수 있다

**Independent Test**: 포지션 진입 후 손익분기 김프율이 계산되어 표시되는지 확인

### Tests for User Story 3

- [ ] T045 [P] [US3] Write unit test for pnl_service.calculate_breakeven() in tests/unit/test_pnl_service.py (RED)
- [ ] T046 [P] [US3] Write unit test for pnl_service.calculate_pnl() in tests/unit/test_pnl_service.py (RED)
- [ ] T047 [P] [US3] Write unit test for pnl_service.is_profitable() in tests/unit/test_pnl_service.py (RED)

### Implementation for User Story 3

- [ ] T048 [P] [US3] Create pnl.py Pydantic model with breakeven_kimp, is_profitable in src/dashboard_v2/models/pnl.py
- [ ] T049 [US3] Implement pnl_service.py with FEE_RATE=0.0038 in src/dashboard_v2/services/pnl_service.py
- [ ] T050 [US3] Verify pnl_service tests pass (GREEN)
- [ ] T051 [US3] Add /api/pnl endpoint in src/dashboard_v2/routers/api.py
- [ ] T052 [US3] Update kpi_cards.html with breakeven display and profit/loss color in src/dashboard_v2/templates/components/kpi_cards.html
- [ ] T053 [US3] Update dashboard.js to fetch and display PnL data with color coding in src/dashboard_v2/static/js/dashboard.js
- [ ] T054 [P] [US3] Write integration test for /api/pnl endpoint in tests/integration/test_dashboard_api.py (RED)
- [ ] T055 [US3] Verify integration test passes (GREEN)

**Checkpoint**: User Story 3 완료 - 수익 분기점 표시 독립 동작 확인

---

## Phase 6: User Story 4 - Neon Daybreak 디자인 적용 (Priority: P3)

**Goal**: 대시보드에 새로운 디자인 시스템(Neon Daybreak)을 적용한다

**Independent Test**: 새 디자인이 적용된 대시보드가 PC와 모바일에서 정상 렌더링되는지 확인

### Implementation for User Story 4

- [ ] T056 [P] [US4] Create sidebar.html with navigation in src/dashboard_v2/templates/components/sidebar.html
- [ ] T057 [P] [US4] Create chart.html with Chart.js kimp chart in src/dashboard_v2/templates/components/chart.html
- [ ] T058 [P] [US4] Create control_panel.html with emergency stop button in src/dashboard_v2/templates/components/control_panel.html
- [ ] T059 [P] [US4] Create system_logs.html for system status in src/dashboard_v2/templates/components/system_logs.html
- [ ] T060 [US4] Update base.html with full Neon Daybreak styles (neo-box, neo-btn, hard shadow) in src/dashboard_v2/templates/base.html
- [ ] T061 [US4] Update neon-daybreak.css with responsive breakpoints (320px-768px) in src/dashboard_v2/static/css/neon-daybreak.css
- [ ] T062 [US4] Update index.html to include all components in src/dashboard_v2/templates/index.html
- [ ] T063 [US4] Test responsive layout on mobile viewport

**Checkpoint**: User Story 4 완료 - Neon Daybreak 디자인 적용 확인

---

## Phase 7: User Story 5 - 실시간 티커 표시 (Priority: P4)

**Goal**: 상단에 실시간 데이터 티커(마퀴)가 표시된다

**Independent Test**: 상단 티커에 실시간 데이터가 스크롤되며 표시되는지 확인

### Implementation for User Story 5

- [ ] T064 [P] [US5] Create ticker.py Pydantic model in src/dashboard_v2/models/ticker.py
- [ ] T065 [US5] Add ticker data aggregation in src/dashboard_v2/services/kimp_service.py
- [ ] T066 [US5] Add /api/ticker endpoint in src/dashboard_v2/routers/api.py
- [ ] T067 [US5] Create ticker.html with marquee animation in src/dashboard_v2/templates/components/ticker.html
- [ ] T068 [US5] Update dashboard.js to update ticker data every 10s in src/dashboard_v2/static/js/dashboard.js
- [ ] T069 [US5] Include ticker.html in base.html header in src/dashboard_v2/templates/base.html

**Checkpoint**: User Story 5 완료 - 실시간 티커 표시 확인

---

## Phase 8: Emergency Stop & Existing Features Migration

**Purpose**: 기존 비상정지 기능 마이그레이션

- [ ] T070 [P] Write unit test for emergency_service.activate() in tests/unit/test_emergency_service.py (RED)
- [ ] T071 [P] Write unit test for emergency_service.deactivate() in tests/unit/test_emergency_service.py (RED)
- [ ] T072 Implement emergency_service.py (migrate from existing) in src/dashboard_v2/services/emergency_service.py
- [ ] T073 Verify emergency_service tests pass (GREEN)
- [ ] T074 Add /api/emergency/* endpoints in src/dashboard_v2/routers/api.py
- [ ] T075 Update control_panel.html with emergency stop UI in src/dashboard_v2/templates/components/control_panel.html
- [ ] T076 Add /api/trades endpoint for trade history in src/dashboard_v2/routers/api.py

**Checkpoint**: 기존 기능 마이그레이션 완료

---

## Phase 9: Infrastructure & Deployment

**Purpose**: Docker 및 배포 설정

- [ ] T077 [P] Create Dockerfile.dashboard-v2 with uvicorn runtime
- [ ] T078 [P] Create docker-compose.dashboard-v2.yml with port 8502
- [ ] T079 Build and test Docker image locally
- [ ] T080 Deploy to Vultr server (SSH)
- [ ] T081 Configure Cloudflare Tunnel (manual step)
- [ ] T082 Verify external access works

**Checkpoint**: 배포 완료 - 외부 접근 확인

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: 최종 마무리 및 품질 검증

- [ ] T083 [P] Add comprehensive error handling for all API endpoints
- [ ] T084 [P] Add loading states for all data sections
- [ ] T085 Run all tests and ensure 100% pass rate
- [ ] T086 Run black (line-length=100) and isort on src/dashboard_v2/
- [ ] T087 Test mobile view on actual mobile device
- [ ] T088 Verify initial load time < 3 seconds
- [ ] T089 Update CLAUDE.md with dashboard_v2 module documentation

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──► Phase 2 (Foundational) ──► Phase 3+ (User Stories)
                                                     │
                                                     ├─► US1 (P1) - 데이터 로딩 [MVP]
                                                     │      │
                                                     │      ▼ (순차)
                                                     ├─► US2 (P2) - 매수 금액
                                                     │      │
                                                     │      ▼ (순차)
                                                     ├─► US3 (P2) - 수익 분기점
                                                     │      │
                                                     │      ▼ (순차)
                                                     ├─► US4 (P3) - 디자인 적용
                                                     │      │
                                                     │      ▼ (순차)
                                                     ├─► US5 (P4) - 티커 표시
                                                     │      │
                                                     │      ▼ (순차)
                                                     └─► Emergency Migration
                                                            │
                                                            ▼
                                                     Deployment ──► Polish
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 | Foundational | - |
| US2 | US1 (app shell, dashboard.js) | - |
| US3 | US2 (position data) | - |
| US4 | US1 (templates structure) | US2, US3 |
| US5 | US4 (base.html) | - |

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# 병렬 실행 가능:
T003 | T004 | T005 | T006 | T007 | T008 | T009
```

**Phase 2 (Foundational)**:
```bash
# 템플릿 병렬:
T014 | T015 | T016 | T017
```

**Phase 3 (US1)**:
```bash
# 테스트 병렬:
T018 | T019 | T020

# 모델 병렬:
T021 | T022
```

**Phase 4 (US2)**:
```bash
# 테스트 병렬:
T034 | T035
```

**Phase 5 (US3)**:
```bash
# 테스트 병렬:
T045 | T046 | T047
```

**Phase 6 (US4)**:
```bash
# 컴포넌트 병렬:
T056 | T057 | T058 | T059
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup (T001-T009)
2. Phase 2: Foundational (T010-T017)
3. Phase 3: User Story 1 (T018-T033)
4. **STOP**: 데이터 로딩 기능 동작 확인
5. 로컬에서 테스트: `uvicorn src.dashboard_v2.main:app --port 8502`

### Incremental Delivery

| Milestone | User Stories | 검증 방법 |
|-----------|--------------|----------|
| MVP | US1 | 데이터 로딩 및 자동 갱신 |
| +매수금액 | US1 + US2 | 포지션 매수 금액 표시 |
| +분기점 | US1-3 | 수익 분기점 및 손익 색상 |
| +디자인 | US1-4 | Neon Daybreak 스타일 |
| +티커 | US1-5 | 상단 마퀴 티커 |
| Full | All + Emergency | 비상정지 포함 전체 기능 |
| Deployed | All + Infra | Cloudflare Tunnel 연동 |

---

## Task Summary

| Phase | Tasks | Parallel |
|-------|-------|----------|
| Setup | 9 | 7 |
| Foundational | 8 | 5 |
| US1 (P1) | 16 | 6 |
| US2 (P2) | 11 | 3 |
| US3 (P2) | 11 | 4 |
| US4 (P3) | 8 | 4 |
| US5 (P4) | 6 | 1 |
| Emergency | 7 | 2 |
| Deployment | 6 | 2 |
| Polish | 7 | 2 |
| **Total** | **89** | **36** |

---

## Notes

- [P] tasks = 다른 파일, 의존성 없음 → 병렬 실행 가능
- [Story] label = 특정 User Story에 매핑
- TDD 필수: 테스트 실패(RED) → 구현 → 테스트 통과(GREEN)
- 각 User Story는 독립적으로 테스트 가능해야 함
- 커밋: 각 task 또는 논리적 그룹 완료 시
- MVP 권장: US1만으로 데이터 로딩 기능 시작, 이후 점진적 확장
- 기존 대시보드(8501)와 병렬 운영 후 검증 완료 시 전환
- 하드코딩 금지: FEE_RATE 등 모든 설정값은 config.py에서 관리
