# Feature Specification: Dashboard Enhancement

**Feature Branch**: `003-dashboard-enhancement`
**Created**: 2025-12-17
**Status**: Draft
**Input**: Neon Daybreak 디자인 시스템 적용 + 데이터 로딩 오류 수정 + 매수금액/수익분기점 표시 추가

## Clarifications

**UI Framework 결정**: FastAPI + Jinja2 템플릿으로 전환 (Option B 선택)

- 기존 Streamlit 대시보드를 FastAPI + Jinja2 기반으로 재구축
- 제공된 HTML/Tailwind CSS 디자인을 그대로 활용 가능
- 구현 완료 후 Cloudflare Tunnel 연동하여 외부 접근 제공
- 기존 Supabase 데이터 연동은 유지

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 실시간 데이터 로딩 수정 (Priority: P1)

운영자가 대시보드 접속 시 모든 데이터(김프율, 포지션, 환율, 시스템 상태)가 정상적으로 로딩되어 표시된다. 데이터 로딩 실패 시 명확한 에러 메시지와 재시도 옵션이 제공된다.

**Why this priority**: 데이터가 표시되지 않으면 대시보드의 모든 기능이 무용지물. 가장 기본적인 기능.

**Independent Test**: 대시보드 접속 시 모든 섹션에 실제 데이터가 표시되고, 10초 이내 자동 갱신되는지 확인.

**Acceptance Scenarios**:

1. **Given** Supabase 연결 정상, **When** 대시보드 접속, **Then** 김프율, 환율, 포지션 데이터가 3초 이내 로딩된다.
2. **Given** 데이터 로딩 중, **When** 로딩 진행, **Then** 스켈레톤 UI 또는 로딩 인디케이터가 표시된다.
3. **Given** Supabase 연결 실패, **When** 대시보드 접속, **Then** "데이터 로딩 실패" 메시지와 재시도 버튼이 표시된다.
4. **Given** 특정 API만 실패, **When** 대시보드 로딩, **Then** 실패한 섹션만 에러 표시, 나머지는 정상 표시된다.

---

### User Story 2 - 매수 금액 표시 (Priority: P2)

운영자가 현재 포지션의 총 매수 금액(투자 원금)을 한눈에 확인할 수 있다. 업비트 현물 매수 금액과 바이낸스 선물 진입 금액이 각각 표시된다.

**Why this priority**: 투자 원금 파악은 손익 계산과 리스크 관리의 기본.

**Independent Test**: 오픈 포지션이 있을 때 매수 금액이 KRW 단위로 표시되는지 확인.

**Acceptance Scenarios**:

1. **Given** 오픈 포지션 존재, **When** 대시보드 접속, **Then** 총 매수 금액이 KRW 포맷으로 표시된다 (예: ₩38,000,000).
2. **Given** 오픈 포지션 존재, **When** 상세 보기, **Then** 업비트 매수금액, 바이낸스 진입금액이 개별 표시된다.
3. **Given** 포지션 없음, **When** 대시보드 접속, **Then** 매수 금액 "₩0" 또는 "-" 표시.

---

### User Story 3 - 수익 분기점 표시 (Priority: P2)

운영자가 현재 포지션의 수익 분기점(Breakeven Point)을 확인할 수 있다. 수수료를 포함한 실제 손익분기 김프율이 표시된다.

**Why this priority**: 수익 분기점을 알아야 청산 타이밍을 판단할 수 있음.

**Independent Test**: 포지션 진입 후 손익분기 김프율이 계산되어 표시되는지 확인.

**Acceptance Scenarios**:

1. **Given** 오픈 포지션 존재, **When** 대시보드 접속, **Then** 손익분기 김프율이 % 단위로 표시된다 (예: 진입 김프 + 0.38% 수수료).
2. **Given** 현재 김프율 < 분기점, **When** 분기점 표시, **Then** 빨간색으로 "손실 구간" 표시.
3. **Given** 현재 김프율 > 분기점, **When** 분기점 표시, **Then** 녹색으로 "수익 구간" 표시.
4. **Given** 포지션 없음, **When** 대시보드 접속, **Then** 분기점 "-" 또는 "N/A" 표시.

---

### User Story 4 - Neon Daybreak 디자인 적용 (Priority: P3)

대시보드에 새로운 디자인 시스템(Neon Daybreak)을 적용한다. Neo-brutalism 스타일의 하드 섀도우, 라임 그린 액센트, 모노스페이스 폰트를 사용한다.

**Why this priority**: 디자인 개선은 기능 수정 후에 적용해도 됨. 기능 우선.

**Independent Test**: 새 디자인이 적용된 대시보드가 PC와 모바일에서 정상 렌더링되는지 확인.

**Acceptance Scenarios**:

1. **Given** 대시보드 접속, **When** UI 로드, **Then** Neo-brutalism 스타일 (하드 섀도우, 샤프 코너)이 적용된다.
2. **Given** PC 브라우저 접속, **When** 사이드바 확인, **Then** 네비게이션 메뉴가 좌측에 고정 표시된다.
3. **Given** 모바일 접속, **When** UI 로드, **Then** 반응형 레이아웃으로 사이드바가 숨겨지거나 햄버거 메뉴로 전환된다.
4. **Given** 김프율 카드, **When** 표시, **Then** 라임 그린 강조색으로 하이라이트된다.

---

### User Story 5 - 실시간 티커 표시 (Priority: P4)

상단에 실시간 데이터 티커(마퀴)가 표시된다. BTC 가격, ETH 가격, 환율, 김프율, API 레이턴시가 스크롤된다.

**Why this priority**: 보조 정보 표시로 필수는 아님.

**Independent Test**: 상단 티커에 실시간 데이터가 스크롤되며 표시되는지 확인.

**Acceptance Scenarios**:

1. **Given** 대시보드 로드, **When** 티커 확인, **Then** BTC/KRW, ETH/KRW, USD/KRW, KIMP 값이 스크롤된다.
2. **Given** 데이터 갱신, **When** 10초 경과, **Then** 티커 데이터가 최신값으로 업데이트된다.

---

### Edge Cases

- Supabase 연결 타임아웃 시 어떻게 처리하는가? (10초 타임아웃 → 에러 표시 + 재시도 버튼)
- 포지션 데이터가 비정상적으로 큰 값일 때? (포맷팅 검증, 오버플로우 방지)
- 수익 분기점 계산 시 수수료율이 변경되면? (설정에서 수수료율 관리)
- 다중 포지션이 있을 때 분기점 계산? (포지션별 개별 분기점 표시)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 대시보드 로딩 시 모든 데이터를 3초 이내에 표시해야 한다
- **FR-002**: 시스템은 데이터 로딩 실패 시 명확한 에러 메시지와 재시도 옵션을 제공해야 한다
- **FR-003**: 시스템은 현재 포지션의 총 매수 금액을 KRW 단위로 표시해야 한다
- **FR-004**: 시스템은 업비트/바이낸스 개별 매수 금액을 표시해야 한다
- **FR-005**: 시스템은 수익 분기점(손익분기 김프율)을 계산하여 표시해야 한다
- **FR-006**: 시스템은 현재 김프율과 분기점 비교 결과를 시각적으로 표시해야 한다 (손실/수익 구간)
- **FR-007**: 시스템은 Neon Daybreak 디자인 시스템을 적용해야 한다
- **FR-008**: 시스템은 상단 티커에 실시간 시세 정보를 스크롤 표시해야 한다
- **FR-009**: 시스템은 PC와 모바일에서 반응형으로 동작해야 한다
- **FR-010**: 시스템은 로딩 중 스켈레톤 UI 또는 로딩 인디케이터를 표시해야 한다

### Non-Functional Requirements

- **NFR-001**: 자동 갱신 주기 10초
- **NFR-002**: API 타임아웃 10초
- **NFR-003**: 모바일 뷰포트(320px~768px) 지원

> Note: 초기 로딩 시간 3초 이내는 FR-001에서 정의됨

### Key Entities

- **Position**: 현재 포지션. entry_price, btc_amount, entry_kimp, total_invested 포함
- **BreakevenPoint**: 손익분기점. entry_kimp + fee_rate로 계산
- **TickerData**: 티커 표시 데이터. BTC, ETH, USD/KRW, KIMP, API latency 포함
- **LoadingState**: 각 섹션별 로딩 상태. loading, success, error, data 포함

### Breakeven Point Calculation

```
수익 분기점 김프율 = 진입 김프율 + 총 수수료율

총 수수료율 = 업비트 수수료(0.05% × 2) + 바이낸스 수수료(0.04% × 2) + 슬리피지(0.2%)
           = 0.1% + 0.08% + 0.2%
           = 0.38%

예시:
- 진입 김프: 3.50%
- 분기점: 3.50% + 0.38% = 3.88%
- 현재 김프: 4.10% → 수익 구간 (녹색)
- 현재 김프: 3.60% → 손실 구간 (빨간색)
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 대시보드 접속 시 모든 데이터가 3초 이내에 로딩된다
- **SC-002**: 데이터 로딩 성공률 99% 이상 (네트워크 정상 시)
- **SC-003**: 매수 금액이 정확한 KRW 포맷으로 표시된다 (천 단위 콤마)
- **SC-004**: 수익 분기점이 소수점 2자리까지 정확히 계산된다
- **SC-005**: 손실/수익 구간 표시가 실제 상태와 100% 일치한다
- **SC-006**: 모바일 뷰포트에서 모든 핵심 정보가 접근 가능하다
- **SC-007**: 에러 발생 시 100% 에러 메시지가 표시된다

## Assumptions

- **FastAPI + Jinja2**로 대시보드 재구축 (Streamlit 대체)
- 기존 Supabase 데이터베이스 연동 유지
- 구현 완료 후 Cloudflare Tunnel 연동 (기존 설정 활용)
- 제공된 HTML/Tailwind CSS 디자인을 템플릿으로 사용
- 수수료율은 현재 고정값(0.38%) 사용, 추후 설정 가능하게 확장
- 단일 포지션만 관리 (다중 포지션은 향후 확장)
- 기존 비상정지, 시스템 상태 기능은 유지
- Python 3.11+, uvicorn ASGI 서버 사용

## Design Reference

### Neon Daybreak Design System

- **Background**: #F3F4F6 (light gray)
- **Surface**: #FFFFFF (white)
- **Border**: #000000 (black, 2px solid)
- **Accent**: #84CC16 (lime green)
- **Danger**: #EF4444 (red)
- **Shadow**: 4px 4px 0px #000000 (hard shadow)
- **Font**: Inter (headings), JetBrains Mono (data)
- **Corner**: 0px (sharp corners)

### Component Styles

- **neo-box**: White background, black border, hard shadow, hover lift effect
- **neo-btn**: Lime background, black border, uppercase text, active press effect
- **section-label**: Black tab header above cards
- **ticker-wrap**: Black background, lime text, marquee animation
