# Implementation Plan: Dashboard Enhancement

**Branch**: `003-dashboard-enhancement` | **Date**: 2025-12-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-dashboard-enhancement/spec.md`

## Summary

기존 Streamlit 대시보드를 **FastAPI + Jinja2** 기반으로 재구축한다. Neon Daybreak 디자인 시스템을 적용하고, 데이터 로딩 오류 수정, 매수 금액 및 수익 분기점 표시 기능을 추가한다. 구현 완료 후 Cloudflare Tunnel을 연동하여 외부 접근을 제공한다.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Framework**: FastAPI 0.104+, Jinja2 3.1+
**Frontend**: HTML5, Tailwind CSS (CDN), Chart.js, Lucide Icons
**Storage**: Supabase (PostgreSQL) - 기존 테이블 활용
**Testing**: pytest, pytest-asyncio, httpx (TestClient)
**Target Platform**: Docker container → Vultr 서버, Cloudflare Tunnel 경유
**Server**: uvicorn ASGI
**Performance Goals**: 초기 로딩 3초 이내, 자동 갱신 10초
**Constraints**: 기존 비상정지/데이터 로직 유지, 반응형 UI 필수

## Constitution Check

*GATE: Must pass before implementation.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Safety First** | PASS | 비상정지 기능 유지, 손익분기점 표시로 안전한 청산 판단 지원 |
| **II. Concurrent Execution** | N/A | 대시보드는 모니터링 전용, 주문 실행 로직 없음 |
| **III. Code Quality** | PASS | Type hints, docstring, async/await, loguru 사용 |
| **IV. Security** | PASS | API 키는 환경변수, Cloudflare Zero Trust 인증 |
| **V. Simplicity** | PASS | FastAPI 단일 앱, 기존 Supabase 재사용, 복잡한 프레임워크 없음 |
| **VI. TDD Cycle** | PASS | API 엔드포인트, 계산 로직 테스트 작성 |
| **VII. GitHub First** | PASS | 작업 완료 즉시 커밋/푸시 |

**Gate Result**: PASS - 모든 원칙 준수

## Project Structure

### Source Code (repository root)

```text
src/
├── dashboard_v2/                   # 새 FastAPI 대시보드
│   ├── __init__.py
│   ├── main.py                     # FastAPI 앱 진입점
│   ├── config.py                   # 설정 (환경변수)
│   │
│   ├── routers/                    # API 라우터
│   │   ├── __init__.py
│   │   ├── pages.py                # HTML 페이지 라우터
│   │   ├── api.py                  # JSON API 엔드포인트
│   │   └── websocket.py            # 실시간 데이터 (선택)
│   │
│   ├── services/                   # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── position_service.py     # 포지션 조회
│   │   ├── kimp_service.py         # 김프 데이터 조회
│   │   ├── pnl_service.py          # 손익 계산 (분기점 포함)
│   │   ├── emergency_service.py    # 비상정지 (기존 로직 이전)
│   │   └── health_service.py       # 시스템 상태 체크
│   │
│   ├── models/                     # Pydantic 모델
│   │   ├── __init__.py
│   │   ├── position.py
│   │   ├── kimp.py
│   │   ├── pnl.py
│   │   └── system.py
│   │
│   ├── templates/                  # Jinja2 HTML 템플릿
│   │   ├── base.html               # 기본 레이아웃
│   │   ├── index.html              # 메인 대시보드
│   │   ├── components/
│   │   │   ├── sidebar.html
│   │   │   ├── ticker.html
│   │   │   ├── kpi_cards.html
│   │   │   ├── chart.html
│   │   │   ├── positions_table.html
│   │   │   ├── control_panel.html
│   │   │   └── system_logs.html
│   │   └── partials/
│   │       ├── loading.html        # 로딩 스켈레톤
│   │       └── error.html          # 에러 표시
│   │
│   └── static/                     # 정적 파일
│       ├── css/
│       │   └── neon-daybreak.css   # 커스텀 CSS
│       └── js/
│           └── dashboard.js        # 클라이언트 JS (fetch, 갱신)
│
├── database/                       # DB 클라이언트 (기존)
│   └── supabase_client.py
│
└── telegram/                       # 알림 (기존)
    └── notifier.py

tests/
├── unit/
│   ├── test_pnl_service.py         # 손익/분기점 계산 테스트
│   ├── test_position_service.py
│   └── test_kimp_service.py
└── integration/
    └── test_dashboard_api.py       # API 엔드포인트 테스트

# 인프라 설정
Dockerfile.dashboard-v2             # 새 대시보드 Docker 이미지
docker-compose.dashboard-v2.yml     # Docker Compose 설정
```

## Architecture

### 요청 흐름

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Dashboard V2 Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Browser (PC/Mobile)                                                        │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Cloudflare Tunnel + Zero Trust (구현 완료 후)                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  FastAPI (uvicorn :8502)                                             │   │
│   │                                                                      │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │   │
│   │  │ GET /       │  │ GET /api/*  │  │ POST /api/* │                  │   │
│   │  │ (HTML)      │  │ (JSON)      │  │ (Actions)   │                  │   │
│   │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │   │
│   │         │                │                │                          │   │
│   │         ▼                ▼                ▼                          │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │                    Services Layer                            │    │   │
│   │  │  position_service │ kimp_service │ pnl_service │ emergency  │    │   │
│   │  └─────────────────────────────────────────────────────────────┘    │   │
│   │                              │                                       │   │
│   └──────────────────────────────┼───────────────────────────────────────┘   │
│                                  ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         Supabase                                     │   │
│   │    positions │ kimp_1m │ trades │ system_status │ fx_rates          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### API 엔드포인트

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/` | 메인 대시보드 HTML | HTML |
| GET | `/api/position` | 현재 포지션 | JSON |
| GET | `/api/kimp` | 김프 데이터 (1시간) | JSON |
| GET | `/api/kimp/current` | 현재 김프율 | JSON |
| GET | `/api/pnl` | 손익 현황 + 분기점 | JSON |
| GET | `/api/ticker` | 티커 데이터 | JSON |
| GET | `/api/health` | 시스템 상태 | JSON |
| GET | `/api/trades` | 거래 이력 (최근 10건) | JSON |
| POST | `/api/emergency/activate` | 비상정지 활성화 | JSON |
| POST | `/api/emergency/deactivate` | 비상정지 해제 | JSON |
| GET | `/api/emergency/status` | 비상정지 상태 | JSON |

### 핵심 데이터 모델

```python
# models/pnl.py
from pydantic import BaseModel
from typing import Optional

class PnLData(BaseModel):
    """손익 데이터"""
    entry_kimp: float           # 진입 김프 (%)
    current_kimp: float         # 현재 김프 (%)
    kimp_profit: float          # 김프 차익 (%)
    fee_rate: float             # 수수료율 (0.38%)
    net_profit: float           # 순이익 (%)
    breakeven_kimp: float       # 손익분기 김프 (%)
    is_profitable: bool         # 수익 구간 여부

class PositionData(BaseModel):
    """포지션 데이터"""
    quantity: float             # BTC 수량
    entry_price_krw: float      # 업비트 진입가
    entry_price_usd: float      # 바이낸스 진입가
    entry_kimp: float           # 진입 김프
    total_invested_krw: float   # 총 매수 금액 (KRW)
    upbit_invested: float       # 업비트 매수 금액
    binance_invested_krw: float # 바이낸스 진입 금액 (KRW 환산)
    holding_hours: float        # 보유 시간 (시간)
    status: str                 # open/closed
```

### 손익 분기점 계산

```python
# services/pnl_service.py

FEE_RATE = 0.0038  # 0.38% (업비트 0.1% + 바이낸스 0.08% + 슬리피지 0.2%)

def calculate_breakeven(entry_kimp: float) -> float:
    """손익분기 김프 계산"""
    return entry_kimp + (FEE_RATE * 100)  # 진입 김프 + 0.38%

def calculate_pnl(entry_kimp: float, current_kimp: float) -> dict:
    """손익 계산"""
    kimp_profit = current_kimp - entry_kimp  # 롱 포지션 기준
    net_profit = kimp_profit - (FEE_RATE * 100)
    breakeven = calculate_breakeven(entry_kimp)

    return {
        "entry_kimp": entry_kimp,
        "current_kimp": current_kimp,
        "kimp_profit": kimp_profit,
        "fee_rate": FEE_RATE * 100,
        "net_profit": net_profit,
        "breakeven_kimp": breakeven,
        "is_profitable": current_kimp >= breakeven,
    }
```

## Implementation Phases

### Phase 1: Setup & Foundation (Day 1)

1. `src/dashboard_v2/` 디렉토리 구조 생성
2. FastAPI 앱 기본 설정 (`main.py`, `config.py`)
3. Jinja2 템플릿 엔진 설정
4. 기본 라우터 설정 (`/` → index.html)
5. Docker 설정 (`Dockerfile.dashboard-v2`)

### Phase 2: Services & Models (Day 1-2)

1. Pydantic 모델 정의
2. `position_service.py` - 포지션 조회 + **매수 금액 계산**
3. `kimp_service.py` - 김프 데이터 조회
4. `pnl_service.py` - 손익 계산 + **분기점 계산** (핵심)
5. `emergency_service.py` - 기존 로직 이전
6. `health_service.py` - 시스템 상태
7. 각 서비스 단위 테스트

### Phase 3: API Endpoints (Day 2)

1. `/api/position` - 포지션 + 매수 금액
2. `/api/kimp` - 김프 데이터
3. `/api/pnl` - 손익 + 분기점
4. `/api/emergency/*` - 비상정지
5. `/api/health` - 시스템 상태
6. `/api/ticker` - 티커 데이터
7. API 통합 테스트

### Phase 4: Templates & Design (Day 2-3)

1. `base.html` - Neon Daybreak 레이아웃
2. `index.html` - 메인 대시보드
3. 컴포넌트 템플릿:
   - `ticker.html` - 상단 마퀴
   - `kpi_cards.html` - KPI 카드 (김프, 환율, 매수금액, 분기점)
   - `chart.html` - Chart.js 김프 차트
   - `positions_table.html` - 포지션 테이블
   - `control_panel.html` - 비상정지 제어
   - `system_logs.html` - 시스템 로그
4. `loading.html`, `error.html` - 로딩/에러 UI
5. `neon-daybreak.css` - 커스텀 스타일
6. `dashboard.js` - 클라이언트 JS (fetch, 10초 갱신)

### Phase 5: Integration & Testing (Day 3)

1. 로컬 Docker 빌드 및 테스트
2. 모든 API 엔드포인트 동작 확인
3. 반응형 UI 테스트 (PC/모바일)
4. 에러 핸들링 테스트
5. 데이터 로딩 성능 테스트 (3초 이내)

### Phase 6: Deployment (Day 4)

1. Vultr 서버에 배포 (`docker-compose up -d`)
2. 포트 8502로 실행 (기존 8501과 병렬)
3. 기능 검증 후 기존 대시보드 중지
4. Cloudflare Tunnel 연동

## Key Design Decisions

### 1. FastAPI + Jinja2 선택 이유

| 항목 | Streamlit | FastAPI + Jinja2 |
|------|-----------|------------------|
| 디자인 자유도 | 제한적 | 완전한 커스텀 |
| 성능 | 느림 (매번 rerun) | 빠름 (정적 + API) |
| 프로덕션 적합성 | 프로토타입용 | 프로덕션 레벨 |
| 유지보수 | 어려움 | 용이 |

### 2. 기존 포트(8501) 유지 전략

- 새 대시보드: 포트 8502로 먼저 배포
- 병렬 운영으로 검증
- 검증 완료 후 8501로 전환 또는 기존 중지

### 3. 클라이언트 갱신 방식

- **선택**: JavaScript fetch + setInterval (10초)
- 대안 (향후): WebSocket 실시간 푸시

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| 기존 대시보드 중단 | 모니터링 불가 | 병렬 배포로 검증 후 전환 |
| 데이터 로딩 실패 | 빈 화면 | 에러 핸들링 + 재시도 버튼 |
| 모바일 레이아웃 깨짐 | UX 저하 | Tailwind 반응형 클래스 활용 |

## Success Metrics

- [ ] 초기 로딩 3초 이내
- [ ] 자동 갱신 10초 주기 동작
- [ ] 매수 금액 정확히 표시
- [ ] 분기점 계산 정확도 100%
- [ ] 손익/수익 구간 색상 표시 정확
- [ ] 모바일 뷰포트 정상 렌더링
- [ ] 에러 시 100% 에러 메시지 표시

## Complexity Tracking

> Constitution Check에 위반 사항 없음. 추가 정당화 불필요.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
