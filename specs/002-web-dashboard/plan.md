# Implementation Plan: Web Dashboard

**Branch**: `002-web-dashboard` | **Date**: 2025-12-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-web-dashboard/spec.md`

## Summary

Cloudflare Tunnel + Streamlit 기반 웹 대시보드를 구현한다. 비상정지 제어, 실시간 포지션/김프 모니터링, 시스템 상태 표시 기능을 제공하며, Zero Trust 인증으로 외부 접근을 보호한다. 기존 kimptrade 인프라(Supabase, Telegram)를 활용한다.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Streamlit 1.29+, Supabase 2.0+, python-telegram-bot 20.0+, plotly 5.0+, pandas
**Storage**: Supabase (PostgreSQL) - 기존 테이블 활용 + system_status 테이블 추가
**Testing**: pytest, pytest-asyncio
**Target Platform**: Docker container → **별도 Vultr 서버** (Collector 서버와 분리), Cloudflare Tunnel 경유 외부 접근
**Project Type**: Single backend service (기존 kimptrade에 dashboard 모듈 추가, **별도 서버 배포**)
**Performance Goals**: 데이터 갱신 10초 이내, 비상정지 활성화 1초 이내
**Constraints**: Cloudflare Zero Trust 인증 필수, 서버 포트 외부 노출 금지
**Scale/Scope**: 1-2명 운영자, 단일 대시보드 인스턴스

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Safety First** | PASS | 비상정지는 신규 진입만 차단, 청산은 허용 (손실 방지) |
| **II. Concurrent Execution** | N/A | 대시보드는 모니터링/제어 전용, 주문 실행 로직 없음 |
| **III. Code Quality** | PASS | Type hints, docstring, async/await, loguru 사용 예정 |
| **IV. Security** | PASS | Cloudflare Zero Trust 인증, 서버 포트 비노출 |
| **V. Simplicity** | PASS | Streamlit 단일 앱, 기존 Supabase/Telegram 재사용 |
| **VI. TDD Cycle** | PASS | 비상정지 서비스, 데이터 조회 로직 테스트 작성 |
| **VII. GitHub First** | PASS | 작업 완료 즉시 커밋/푸시 |

**Gate Result**: PASS - 모든 원칙 준수

## Project Structure

### Documentation (this feature)

```text
specs/002-web-dashboard/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dashboard/                  # 웹 대시보드 (신규)
│   ├── __init__.py
│   ├── app.py                  # Streamlit 메인 앱
│   ├── components/
│   │   ├── __init__.py
│   │   ├── emergency_panel.py  # 비상정지 제어 패널
│   │   ├── position_card.py    # 포지션 현황 카드
│   │   ├── kimp_chart.py       # 김프율 차트
│   │   ├── pnl_card.py         # 손익 현황 카드
│   │   ├── system_status.py    # 시스템 상태 표시
│   │   └── trade_history.py    # 거래 이력 테이블
│   └── services/
│       ├── __init__.py
│       └── emergency_stop.py   # 비상정지 서비스 (Supabase)
│
├── telegram/                   # 알림 (기존 + 확장)
│   └── notifier.py             # 비상정지 알림 추가
│
├── collectors/                 # 데이터 수집 (기존)
├── calculators/                # 지표 계산 (기존)
├── database/                   # DB 클라이언트 (기존)
└── config.py                   # 환경변수 (확장)

tests/
├── unit/
│   ├── test_emergency_stop.py  # 비상정지 서비스 테스트
│   └── test_dashboard_components.py
└── integration/
    └── test_dashboard_data.py  # 대시보드 데이터 조회 테스트

# 인프라 설정 (신규)
Dockerfile.dashboard            # 대시보드 Docker 이미지
cloudflared/
└── config.yml                  # Cloudflare Tunnel 설정 템플릿
```

**Structure Decision**: 기존 kimptrade 구조에 `src/dashboard/` 모듈 추가. 기존 `src/database/`, `src/telegram/` 재사용.

## Infrastructure Architecture (분리 서버)

### 서버 분리 이유

| 이유 | 설명 |
|------|------|
| **장애 격리** | 대시보드 장애 시에도 데이터 수집 지속 |
| **리소스 독립** | Collector가 1순위, 대시보드와 경합 없음 |
| **보안** | Collector 서버는 외부 노출 최소화 |

### 아키텍처

```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│   Collector 서버 (기존)         │     │   Dashboard 서버 (신규)         │
│   64.176.229.30                 │     │   <새 IP>                       │
│   Vultr 1GB                     │     │   Vultr 1GB                     │
│                                 │     │                                 │
│  ┌───────────────────────────┐  │     │  ┌───────────────────────────┐  │
│  │ collector                 │  │     │  │ dashboard (Streamlit)    │  │
│  │ - Upbit/Binance 데이터    │  │     │  │ - 비상정지 제어          │  │
│  │ - 김프율 계산             │  │     │  │ - 모니터링 UI            │  │
│  │ - DB 저장                 │  │     │  └───────────────────────────┘  │
│  └───────────────────────────┘  │     │  ┌───────────────────────────┐  │
│                                 │     │  │ cloudflared (터널)       │  │
│  ⚠️ 다운되면 = 데이터 손실     │     │  │ - 외부 접근 제공         │  │
│  → 최우선 보호 대상            │     │  └───────────────────────────┘  │
│                                 │     │                                 │
│                                 │     │  ℹ️ 다운되면 = 모니터링 불가    │
│                                 │     │  → 복구하면 됨 (데이터 무손실) │
└────────────────┬────────────────┘     └────────────────┬────────────────┘
                 │                                       │
                 └───────────────┬───────────────────────┘
                                 ▼
                 ┌───────────────────────────────────────┐
                 │         Supabase (클라우드)           │
                 │         - 데이터 저장소               │
                 │         - 둘 다 읽기/쓰기 가능        │
                 └───────────────────────────────────────┘
```

### 비용

| 항목 | 월 비용 |
|------|---------|
| Collector 서버 (기존) | $5 |
| Dashboard 서버 (신규) | $5 |
| **합계** | **$10** |

## Complexity Tracking

> Constitution Check에 위반 사항 없음. 추가 정당화 불필요.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
