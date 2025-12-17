# Vultr 서버 작업 분석 보고서

**작성일**: 2025-12-17
**목적**: 이전 세션 작업과 실제 서버 상태 간의 차이 분석

---

## 1. 요약 (Executive Summary)

### 핵심 발견사항

| 구분 | 이전 세션 작업 | 실제 서버 상태 | 상태 |
|------|---------------|---------------|------|
| **Dashboard 버전** | V1 (Streamlit) | V2 (FastAPI) | 🔴 불일치 |
| **포트** | 8501 | 8502 | 🔴 불일치 |
| **프레임워크** | Streamlit | FastAPI + Jinja2 | 🔴 불일치 |
| **이미지 크기** | 1.15GB | 306MB | 🟢 V2 최적화 |
| **테스트** | Playwright E2E | Unit + Integration | 🟡 테스트 체계 변경 |

### 결론
**Dashboard V2 (FastAPI)로 이미 전환 완료**됨. 이전 세션에서 작업한 V1 관련 설정은 **레거시**로 분류됨.

---

## 2. 타임라인 분석

### 2.1 Git 커밋 히스토리

```
이전 세션 작업 (V1 기준)
│
├─ 5b306f6  feat(dashboard): migrate dashboard from kimptrade repo
├─ 7296294  chore: add speckit configuration
├─ a9ffa6d  docs: add Vultr deployment guide (vultr.md - V1 기준)
│
▼ ─────────── 세션 종료 ───────────
│
├─ 13b7ff7  feat(spec): add 003-dashboard-enhancement feature spec
├─ 30290bc  docs(spec): fix speckit analysis issues
├─ 7138a01  feat(dashboard): implement dashboard v2 with FastAPI + Jinja2  ← V2 구현
├─ 0920b30  docs(spec): add clarifications for auth and logging
├─ 28d2aa3  fix(docker): add pydantic-settings dependency
└─ b9f8b11  docs(deploy): update vultr guide for Dashboard V2  ← vultr.md 업데이트
```

### 2.2 작업 분기점

| 시점 | 이벤트 |
|------|--------|
| 이전 세션 | V1 (Streamlit) 기준으로 배포 가이드, E2E 테스트 작성 |
| 세션 종료 후 | 003-dashboard-enhancement 스펙 작성 |
| 새 세션 | V2 (FastAPI + Jinja2) 전면 구현 및 배포 |

---

## 3. 아키텍처 비교

### 3.1 Dashboard V1 (Streamlit) - 레거시

```
┌─────────────────────────────────────────┐
│  Dashboard V1 (Streamlit)               │
│  포트: 8501                              │
├─────────────────────────────────────────┤
│                                         │
│  src/dashboard/                         │
│  ├── app.py              # Streamlit 앱 │
│  ├── components/                        │
│  │   ├── emergency_panel.py            │
│  │   ├── kimp_chart.py                 │
│  │   ├── pnl_card.py                   │
│  │   ├── position_card.py              │
│  │   ├── system_status.py              │
│  │   └── trade_history.py              │
│  ├── services/                          │
│  │   └── emergency_stop.py             │
│  └── styles/                            │
│      └── neon_daybreak.py              │
│                                         │
│  Docker: Dockerfile.dashboard           │
│  Compose: docker-compose.dashboard.yml  │
│  이미지 크기: 1.15GB                    │
│                                         │
└─────────────────────────────────────────┘
```

### 3.2 Dashboard V2 (FastAPI) - 현재 운영

```
┌─────────────────────────────────────────┐
│  Dashboard V2 (FastAPI + Jinja2)        │
│  포트: 8502                              │
├─────────────────────────────────────────┤
│                                         │
│  src/dashboard_v2/                      │
│  ├── main.py             # FastAPI 앱   │
│  ├── config.py           # Pydantic 설정│
│  ├── models/             # 데이터 모델  │
│  ├── routers/            # API 라우터   │
│  ├── services/           # 비즈니스 로직│
│  ├── static/             # CSS/JS       │
│  └── templates/          # Jinja2 HTML  │
│                                         │
│  Docker: Dockerfile.dashboard-v2        │
│  Compose: docker-compose.dashboard-v2.yml│
│  이미지 크기: 306MB (73% 경량화)        │
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 주요 아키텍처 차이

| 항목 | V1 (Streamlit) | V2 (FastAPI) |
|------|----------------|--------------|
| **프레임워크** | Streamlit (Python) | FastAPI + Jinja2 |
| **렌더링** | Server-side (Streamlit) | Server-side (Jinja2) |
| **API** | 없음 (내장) | RESTful API 분리 |
| **설정 관리** | 환경변수 직접 | Pydantic Settings |
| **헬스체크** | `/_stcore/health` | `/api/health` |
| **보안** | 기본 | non-root user |

---

## 4. 파일 구조 비교

### 4.1 로컬 (C:\order)

```
C:\order/
├── src/
│   ├── dashboard/          # V1 (레거시) - 이전 세션에서 마이그레이션
│   │   ├── app.py
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   │
│   └── dashboard_v2/       # V2 (현재 운영) - 새 세션에서 구현
│       ├── main.py
│       ├── config.py
│       ├── models/
│       ├── routers/
│       ├── services/
│       ├── static/
│       └── templates/
│
├── tests/
│   ├── e2e/               # V1용 Playwright 테스트 (이전 세션)
│   ├── unit/              # V2용 유닛 테스트 (새 세션)
│   └── integration/       # V2용 통합 테스트 (새 세션)
│
├── docker-compose.dashboard.yml      # V1용
├── docker-compose.dashboard-v2.yml   # V2용
├── Dockerfile.dashboard              # V1용
├── Dockerfile.dashboard-v2           # V2용
│
├── vultr.md              # 배포 가이드 (V2 기준으로 업데이트됨)
└── vultr2.md             # 이 문서
```

### 4.2 서버 (/root/order)

```
/root/order/
├── src/
│   ├── dashboard/          # V1 (사용 안함)
│   └── dashboard_v2/       # V2 (실제 운영)
│
├── .env                    # 환경변수 (Supabase 등)
├── docker-compose.dashboard-v2.yml
├── Dockerfile.dashboard-v2
└── ...
```

---

## 5. Docker 설정 비교

### 5.1 컨테이너 현황 (서버)

| 컨테이너 | 이미지 | 상태 | 포트 | 메모리 |
|----------|--------|------|------|--------|
| `kimptrade-dashboard-v2` | order-dashboard-v2 | **Up (healthy)** | 8502 | 103MB |
| `kimptrade-dashboard` | kimptrade-dashboard | Up (healthy) | 8501 | 145MB |

### 5.2 Docker Compose 차이

| 항목 | V1 | V2 |
|------|----|----|
| **파일** | `docker-compose.dashboard.yml` | `docker-compose.dashboard-v2.yml` |
| **컨테이너명** | `kimptrade-dashboard` | `kimptrade-dashboard-v2` |
| **포트** | `127.0.0.1:8501:8501` | `8502:8502` |
| **헬스체크** | `curl /_stcore/health` | `python urllib /api/health` |
| **네트워크** | `kimptrade-dashboard-network` | `kimptrade-network` |
| **볼륨** | 없음 | static, templates 마운트 |

### 5.3 Dockerfile 차이

| 항목 | V1 | V2 |
|------|----|----|
| **베이스** | python:3.11-slim | python:3.11-slim |
| **의존성 설치** | requirements.txt | 직접 pip install |
| **사용자** | root | appuser (non-root) |
| **실행** | `streamlit run` | `uvicorn` |
| **이미지 크기** | 1.15GB | 306MB |

---

## 6. 테스트 체계 비교

### 6.1 이전 세션 (V1용)

```
tests/e2e/                    # Playwright E2E 테스트
├── dashboard.spec.ts         # 대시보드 로드 테스트
├── emergency.spec.ts         # 비상정지 패널 테스트
└── components.spec.ts        # 컴포넌트 테스트

설정 파일:
├── playwright.config.ts      # baseURL: na4.pe.kr:8501
├── package.json              # @playwright/test
└── .github/workflows/playwright.yml
```

**문제점**:
- baseURL이 `na4.pe.kr:8501` (V1 URL)로 설정됨
- V2 API 엔드포인트(`/api/health`)와 호환 안됨

### 6.2 현재 세션 (V2용)

```
tests/
├── unit/                     # 유닛 테스트
│   ├── test_dashboard_app.py
│   ├── test_kimp_service.py
│   ├── test_pnl_service.py
│   ├── test_health_service.py
│   └── test_position_service.py
│
└── integration/              # 통합 테스트
    └── test_dashboard_api.py
```

**개선점**:
- Python pytest 기반
- API 단위 테스트 분리
- 서비스별 테스트 케이스

---

## 7. 환경변수 비교

### 7.1 V1에서 사용

```env
SUPABASE_URL=xxx
SUPABASE_KEY=xxx
```

### 7.2 V2에서 추가

```env
# 기존
SUPABASE_URL=xxx
SUPABASE_KEY=xxx

# 신규
REFRESH_INTERVAL=10      # 자동 새로고침 간격
API_TIMEOUT=10           # API 타임아웃
FEE_RATE=0.0038          # 수수료율
DEBUG=false              # 디버그 모드
```

---

## 8. 접속 정보 비교

### 8.1 URL

| 버전 | URL | 상태 |
|------|-----|------|
| **V2** | http://158.247.206.2:8502 | ✅ 운영 중 |
| V1 | http://158.247.206.2:8501 | 레거시 |
| V1 (도메인) | http://na4.pe.kr:8501 | 레거시 |

### 8.2 API 엔드포인트 (V2)

| 엔드포인트 | 설명 |
|------------|------|
| `GET /` | 메인 대시보드 페이지 |
| `GET /api/health` | 헬스체크 |
| `GET /api/kimp` | 김프율 데이터 |
| `GET /api/position` | 포지션 정보 |
| `GET /api/pnl` | 손익 정보 |

---

## 9. 영향 분석

### 9.1 이전 세션 작업 중 유효한 것

| 작업 | 상태 | 비고 |
|------|------|------|
| kimptrade → order 마이그레이션 | ✅ 유효 | V1 코드 마이그레이션 |
| speckit 전역 설정 | ✅ 유효 | 모든 프로젝트에서 사용 가능 |
| .specify 템플릿 | ✅ 유효 | 스펙 작성에 활용 |
| Git 브랜치 전략 | ✅ 유효 | feat/dashboard-migration |

### 9.2 이전 세션 작업 중 레거시화된 것

| 작업 | 상태 | 비고 |
|------|------|------|
| Playwright E2E 테스트 | 🟡 레거시 | V1용, V2 미지원 |
| playwright.config.ts | 🟡 레거시 | baseURL 8501 |
| package.json (npm) | 🟡 레거시 | E2E용 |
| .github/workflows/playwright.yml | 🟡 레거시 | V1 테스트용 |

### 9.3 새 세션에서 추가된 것

| 작업 | 상태 | 비고 |
|------|------|------|
| Dashboard V2 구현 | ✅ 신규 | FastAPI + Jinja2 |
| src/dashboard_v2/ | ✅ 신규 | V2 소스 코드 |
| Unit/Integration 테스트 | ✅ 신규 | pytest 기반 |
| docker-compose.dashboard-v2.yml | ✅ 신규 | V2 배포 설정 |
| Dockerfile.dashboard-v2 | ✅ 신규 | V2 이미지 |

---

## 10. 권장 조치 사항

### 10.1 즉시 조치 (P0)

1. **E2E 테스트 업데이트 또는 제거**
   ```bash
   # 옵션 1: V2용으로 업데이트
   # playwright.config.ts의 baseURL을 8502로 변경
   # 테스트 케이스를 V2 API에 맞게 수정

   # 옵션 2: E2E 테스트 제거 (Unit/Integration으로 대체)
   rm -rf tests/e2e/
   rm package.json package-lock.json playwright.config.ts
   rm .github/workflows/playwright.yml
   ```

2. **V1 컨테이너 정리 (선택)**
   ```bash
   # 서버에서 실행
   docker stop kimptrade-dashboard
   docker rm kimptrade-dashboard
   docker rmi kimptrade-dashboard
   ```

### 10.2 중기 조치 (P1)

1. **V1 소스 코드 정리**
   - `src/dashboard/` 디렉토리 제거 여부 결정
   - 레거시 유지 또는 완전 삭제

2. **CI/CD 파이프라인 정비**
   - V2용 pytest 워크플로우 추가
   - Playwright 워크플로우 제거 또는 V2 대응

### 10.3 장기 조치 (P2)

1. **문서 일원화**
   - V1 관련 문서 아카이브
   - V2 기준으로 문서 통일

2. **PR 머지 전략**
   - `feat/dashboard-migration` → `main` 머지 시점 결정
   - V1/V2 혼재 상태 정리

---

## 11. 서버 리소스 현황

### 11.1 하드웨어

| 항목 | 값 |
|------|-----|
| CPU | 1 vCPU (Xeon Skylake) |
| RAM | 951MB (50% 사용 중) |
| Disk | 25GB (46% 사용 중) |
| OS | Ubuntu 22.04.5 LTS |

### 11.2 컨테이너 리소스

| 컨테이너 | CPU | 메모리 | 상태 |
|----------|-----|--------|------|
| V2 | 0.20% | 103MB | healthy |
| V1 | 0.00% | 145MB | healthy (미사용) |

**권장**: V1 컨테이너 제거 시 약 145MB 메모리 확보 가능

---

## 12. 결론

### 12.1 현재 상태

- **Dashboard V2가 정상 운영 중**
- 이전 세션의 V1 기반 작업은 레거시화됨
- 로컬(C:\order)과 서버(/root/order) 동기화 필요

### 12.2 핵심 기억 사항

```
운영 중인 대시보드:
├── URL: http://158.247.206.2:8502
├── 컨테이너: kimptrade-dashboard-v2
├── Docker: docker-compose.dashboard-v2.yml
├── 소스: src/dashboard_v2/
└── 헬스체크: /api/health

레거시 (사용 안함):
├── URL: http://158.247.206.2:8501
├── 컨테이너: kimptrade-dashboard
├── Docker: docker-compose.dashboard.yml
├── 소스: src/dashboard/
└── E2E 테스트: tests/e2e/
```

---

**문서 끝**
