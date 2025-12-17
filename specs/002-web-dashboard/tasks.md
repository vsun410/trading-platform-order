# Tasks: Web Dashboard

**Input**: Design documents from `/specs/002-web-dashboard/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: TDD Cycle 필수 (Constitution VI). 각 기능별 테스트 먼저 작성.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization) ✅

**Purpose**: 대시보드 모듈 기본 구조 및 의존성 설정

- [x] T001 Create dashboard directory structure per plan.md (src/dashboard/, src/dashboard/components/, src/dashboard/services/)
- [x] T002 Add Streamlit and Plotly dependencies to requirements.txt
- [x] T003 [P] Create src/dashboard/__init__.py
- [x] T004 [P] Create src/dashboard/components/__init__.py
- [x] T005 [P] Create src/dashboard/services/__init__.py
- [x] T006 [P] Create tests/unit/test_emergency_stop.py (empty file)
- [x] T007 [P] Create tests/unit/test_dashboard_components.py (empty file)

---

## Phase 2: Foundational (Blocking Prerequisites) ✅

**Purpose**: 모든 User Story가 의존하는 핵심 인프라

**CRITICAL**: Phase 2 완료 전까지 User Story 작업 불가

### Database Layer

- [x] T008 Create SQL migration for system_status table in docs/migrations/005_system_status.sql
- [ ] T009 Execute migration on Supabase (manual step - SQL 실행)

### Streamlit App Shell

- [x] T010 [P] Write unit test for app initialization in tests/unit/test_dashboard_app.py (RED)
- [x] T011 Create basic Streamlit app shell in src/dashboard/app.py (title, layout, page config)
- [x] T012 Verify app shell test passes (GREEN)

**Checkpoint**: Foundation ready - User Story implementation can begin

---

## Phase 3: User Story 1 - 비상정지 제어 (Priority: P1) 🎯 MVP ✅

**Goal**: 운영자가 웹 대시보드에서 비상정지를 활성화/비활성화할 수 있다

**Independent Test**: 비상정지 버튼 클릭 시 즉시 상태가 변경되고, Telegram 알림이 발송되는지 확인

### Tests for User Story 1

> **TDD: Write tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US1] Write unit test for EmergencyStopService.activate() in tests/unit/test_emergency_stop.py (RED)
- [x] T014 [P] [US1] Write unit test for EmergencyStopService.deactivate() in tests/unit/test_emergency_stop.py (RED)
- [x] T015 [P] [US1] Write unit test for EmergencyStopService.is_active() in tests/unit/test_emergency_stop.py (RED)
- [x] T016 [P] [US1] Write unit test for EmergencyStopService.get_status() in tests/unit/test_emergency_stop.py (RED)

### Implementation for User Story 1

- [x] T017 [US1] Implement EmergencyStopService in src/dashboard/services/emergency_stop.py
- [x] T018 [US1] Verify EmergencyStopService tests pass (GREEN)
- [x] T019 [P] [US1] Write unit test for EmergencyPanel component in tests/unit/test_dashboard_components.py (RED)
- [x] T020 [US1] Implement render_emergency_panel() in src/dashboard/components/emergency_panel.py
- [x] T021 [US1] Verify EmergencyPanel test passes (GREEN)
- [x] T022 [US1] Integrate EmergencyPanel into src/dashboard/app.py
- [x] T023 [US1] Add Telegram notification for emergency stop state change in src/telegram/notifier.py
- [ ] T023-1 [US1] Write integration test verifying liquidation works during emergency stop (FR-003 검증) in tests/integration/test_emergency_stop_liquidation.py

**Checkpoint**: User Story 1 완료 - 비상정지 제어 기능 독립 동작 확인

---

## Phase 4: User Story 2 - 실시간 포지션 모니터링 (Priority: P2) ✅

**Goal**: 운영자가 현재 포지션, 손익, 김프율을 실시간으로 확인할 수 있다

**Independent Test**: 대시보드 접속 시 포지션, 손익, 김프율이 표시되고 10초 내 갱신되는지 확인

### Tests for User Story 2

- [x] T024 [P] [US2] Write unit test for position data fetching in tests/unit/test_dashboard_components.py (RED)
- [x] T025 [P] [US2] Write unit test for kimp data fetching in tests/unit/test_dashboard_components.py (RED)
- [x] T026 [P] [US2] Write unit test for PnL calculation in tests/unit/test_dashboard_components.py (RED)

### Implementation for User Story 2

- [x] T027 [P] [US2] Implement render_position_card() in src/dashboard/components/position_card.py
- [x] T028 [US2] Verify position_card test passes (GREEN)
- [x] T029 [P] [US2] Implement render_kimp_chart() in src/dashboard/components/kimp_chart.py
- [x] T030 [US2] Verify kimp_chart test passes (GREEN)
- [x] T031 [P] [US2] Implement render_pnl_card() in src/dashboard/components/pnl_card.py
- [x] T032 [US2] Verify pnl_card test passes (GREEN)
- [x] T033 [US2] Integrate PositionCard, KimpChart, PnLCard into src/dashboard/app.py
- [x] T034 [US2] Add auto-refresh logic (10-second interval) in src/dashboard/app.py

**Checkpoint**: User Story 2 완료 - 포지션/김프/손익 모니터링 독립 동작 확인

---

## Phase 5: User Story 3 - 안전한 외부 접근 (Priority: P3) 🔄

**Goal**: Cloudflare Tunnel과 Zero Trust로 인증된 외부 접근 제공

**Independent Test**: 외부 네트워크에서 인증 화면 표시되고, 인증 후 대시보드 접근 가능 확인

### Infrastructure for User Story 3

- [x] T035 [US3] Create Dockerfile.dashboard with Streamlit runtime
- [x] T036 [P] [US3] Create cloudflared/config.yml template
- [x] T037 [US3] Update docker-compose.yml with dashboard service (localhost:8501 only)
- [x] T038 [US3] Create docs/CLOUDFLARE_SETUP.md with Zero Trust configuration guide

### Deployment for User Story 3

- [ ] T039 [US3] Build and test Docker image locally
- [ ] T040 [US3] Deploy to Vultr server (SSH)
- [ ] T041 [US3] Configure Cloudflare Tunnel on server (manual step)
- [ ] T042 [US3] Configure Zero Trust Access policy (manual step)
- [ ] T043 [US3] Verify external access with OTP authentication

**Checkpoint**: User Story 3 완료 - 외부 접근 및 인증 동작 확인

---

## Phase 6: User Story 4 - 시스템 상태 모니터링 (Priority: P4) ✅

**Goal**: 거래소 API 연결 상태 및 에러 현황 표시

**Independent Test**: 각 거래소 연결 상태가 표시되고, 에러 시 빨간색으로 표시 확인

### Tests for User Story 4

- [x] T044 [P] [US4] Write unit test for system health check in tests/unit/test_dashboard_components.py (RED)

### Implementation for User Story 4

- [x] T045 [US4] Implement render_system_status() in src/dashboard/components/system_status.py
- [x] T046 [US4] Verify system_status test passes (GREEN)
- [x] T047 [US4] Add health check logic (ping Upbit, Binance, Supabase) in src/dashboard/services/health_check.py
- [x] T048 [US4] Integrate SystemStatus into src/dashboard/app.py

**Checkpoint**: User Story 4 완료 - 시스템 상태 모니터링 독립 동작 확인

---

## Phase 7: User Story 5 - 거래 이력 조회 (Priority: P5) ✅

**Goal**: 최근 거래 이력 테이블 표시

**Independent Test**: 최근 10건 거래가 시간순으로 표시되는지 확인

### Tests for User Story 5

- [x] T049 [P] [US5] Write unit test for trade history fetching in tests/unit/test_dashboard_components.py (RED)

### Implementation for User Story 5

- [x] T050 [US5] Implement render_trade_history() in src/dashboard/components/trade_history.py
- [x] T051 [US5] Verify trade_history test passes (GREEN)
- [x] T052 [US5] Integrate TradeHistory into src/dashboard/app.py

**Checkpoint**: User Story 5 완료 - 거래 이력 조회 독립 동작 확인

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 최종 마무리 및 반응형 UI 검증

- [ ] T053 [P] Add mobile-responsive CSS styling in src/dashboard/app.py
- [ ] T054 [P] Add error handling for all data fetch operations (Edge Cases 포함):
  - 인터넷 연결 끊김: 마지막 데이터 유지 + "연결 끊김" 배너 표시
  - 비상정지 중복 클릭: 멱등성 보장 (이미 정지 상태면 무시)
  - Supabase 연결 실패: 재시도 로직 + 에러 상태 표시
  - API 타임아웃: 10초 타임아웃 후 에러 표시
- [ ] T055 Run all tests and ensure 100% pass rate
- [ ] T056 Run black and isort on src/dashboard/
- [ ] T057 Test mobile view on actual mobile device
- [ ] T058 Validate quickstart.md steps work end-to-end
- [ ] T059 Update CLAUDE.md with dashboard module documentation

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──► Phase 2 (Foundational) ──► Phase 3+ (User Stories)
                                                     │
                                                     ├─► US1 (P1) - 비상정지 [MVP]
                                                     │      │
                                                     │      ▼ (순차)
                                                     ├─► US2 (P2) - 모니터링
                                                     │      │
                                                     │      ▼ (순차)
                                                     ├─► US3 (P3) - 외부접근 (US1, US2 필요)
                                                     │      │
                                                     │      ▼ (순차)
                                                     ├─► US4 (P4) - 시스템상태
                                                     │      │
                                                     │      ▼ (순차)
                                                     └─► US5 (P5) - 거래이력
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 | Foundational | - |
| US2 | US1 (app shell) | - |
| US3 | US1, US2 (complete dashboard) | - |
| US4 | US1 (app shell) | US2 |
| US5 | US1 (app shell) | US2, US4 |

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# 병렬 실행 가능:
T003 | T004 | T005 | T006 | T007
```

**Phase 3 (US1)**:
```bash
# 테스트 병렬:
T013 | T014 | T015 | T016

# 구현은 순차 (서비스 → 컴포넌트 → 통합)
```

**Phase 4 (US2)**:
```bash
# 테스트 병렬:
T024 | T025 | T026

# 컴포넌트 병렬:
T027 | T029 | T031
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup (T001-T007)
2. Phase 2: Foundational (T008-T012)
3. Phase 3: User Story 1 (T013-T023)
4. **STOP**: 비상정지 기능 동작 확인
5. 로컬에서 테스트: `streamlit run src/dashboard/app.py`

### Incremental Delivery

| Milestone | User Stories | 검증 방법 |
|-----------|--------------|----------|
| MVP | US1 | 비상정지 버튼 동작 |
| +모니터링 | US1 + US2 | 포지션/김프/손익 표시 |
| +배포 | US1 + US2 + US3 | 외부 URL 접근 가능 |
| +상태 | US1-4 | 시스템 상태 표시 |
| Full | US1-5 | 거래 이력 포함 |

---

## Task Summary

| Phase | Tasks | Parallel |
|-------|-------|----------|
| Setup | 7 | 5 |
| Foundational | 5 | 1 |
| US1 (P1) | 11 | 5 |
| US2 (P2) | 11 | 6 |
| US3 (P3) | 9 | 1 |
| US4 (P4) | 5 | 1 |
| US5 (P5) | 4 | 1 |
| Polish | 7 | 2 |
| **Total** | **59** | **22** |

---

## Notes

- [P] tasks = 다른 파일, 의존성 없음 → 병렬 실행 가능
- [Story] label = 특정 User Story에 매핑
- TDD 필수: 테스트 실패(RED) → 구현 → 테스트 통과(GREEN)
- 각 User Story는 독립적으로 테스트 가능해야 함
- 커밋: 각 task 또는 논리적 그룹 완료 시
- MVP 권장: US1만으로 비상정지 기능 시작, 이후 점진적 확장
- US3(외부접근)은 US1, US2 완료 후 배포
