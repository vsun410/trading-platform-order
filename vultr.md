# Vultr 서버 배포 가이드

**최종 업데이트**: 2025-12-17
**상태**: Dashboard V2 운영 중

---

## 1. 서버 정보

### 1.1 서버 목록

| 서버 | 역할 | IP | 도메인 |
|------|------|-----|--------|
| **Dashboard** | FastAPI 대시보드 | 158.247.206.2 | na4.pe.kr:8502 |
| Collector | 데이터 수집 | 64.176.229.30 | - |

### 1.2 Dashboard 서버 스펙

| 항목 | 값 |
|------|-----|
| OS | Ubuntu 22.04.5 LTS |
| CPU | 1 vCPU (Xeon Skylake) |
| RAM | 951MB |
| Disk | 25GB SSD |
| Docker | 29.1.3 |
| Docker Compose | v5.0.0 |

---

## 2. 현재 운영 상태

### 2.1 Dashboard V2

| 항목 | 값 |
|------|-----|
| **URL** | http://na4.pe.kr:8502 |
| **직접 IP** | http://158.247.206.2:8502 |
| **컨테이너** | `kimptrade-dashboard-v2` |
| **이미지** | `order-dashboard-v2:latest` (306MB) |
| **프레임워크** | FastAPI + Jinja2 |
| **디자인** | Neon Daybreak |
| **서버 경로** | `/root/order` |
| **브랜치** | `feat/dashboard-migration` |

### 2.2 API 엔드포인트

| 엔드포인트 | 설명 |
|------------|------|
| `GET /` | 메인 대시보드 |
| `GET /api/health` | 헬스체크 |
| `GET /api/kimp` | 김프율 데이터 |
| `GET /api/position` | 포지션 정보 |
| `GET /api/pnl` | 손익 정보 |

### 2.3 헬스체크 응답 예시

```json
{
  "status": "healthy",
  "services": {
    "supabase": { "healthy": true },
    "upbit": { "healthy": true, "latency_ms": 70 },
    "binance": { "healthy": true, "latency_ms": 80 }
  }
}
```

---

## 3. 레포지토리 구조

### 3.1 레포 분리

| 레포 | 역할 | 서버 |
|------|------|------|
| **trading-platform-order** | Dashboard V2 | 158.247.206.2 |
| kimptrade | Backend, Collector, DB | 64.176.229.30 |

### 3.2 서버 디렉토리

```
/root/order/                    ← Dashboard V2 (현재 운영)
├── src/dashboard_v2/           ← FastAPI 앱
├── docker-compose.dashboard-v2.yml
├── Dockerfile.dashboard-v2
└── .env                        ← 환경변수

/root/kimptrade/                ← 레거시 (사용 안함)
```

---

## 4. 환경변수

### 4.1 필수 환경변수 (.env)

```env
# Supabase
SUPABASE_URL=https://shcgnkmlmjohmpeoyjlz.supabase.co
SUPABASE_KEY=eyJhbGci...  # anon key

# Dashboard 설정
REFRESH_INTERVAL=10       # 자동 새로고침 (초)
API_TIMEOUT=10            # API 타임아웃 (초)
FEE_RATE=0.0038           # 수수료율 (0.38%)
DEBUG=false               # 디버그 모드
```

---

## 5. 배포 방법

### 5.1 SSH 접속

```bash
ssh -i ~/.ssh/kimptrade_vultr root@158.247.206.2
```

### 5.2 코드 업데이트 & 배포

```bash
cd /root/order
git pull origin feat/dashboard-migration
docker compose -f docker-compose.dashboard-v2.yml build --no-cache
docker compose -f docker-compose.dashboard-v2.yml up -d
```

### 5.3 빠른 배포 (로컬에서 한 번에)

```bash
ssh -i ~/.ssh/kimptrade_vultr root@158.247.206.2 "\
  cd /root/order && \
  git pull && \
  docker compose -f docker-compose.dashboard-v2.yml build --no-cache && \
  docker compose -f docker-compose.dashboard-v2.yml up -d"
```

### 5.4 배포 확인

```bash
# 헬스체크
curl http://localhost:8502/api/health

# 컨테이너 상태
docker ps | grep dashboard-v2

# 로그 확인
docker logs -f kimptrade-dashboard-v2
```

---

## 6. Docker 설정

### 6.1 Docker Compose (docker-compose.dashboard-v2.yml)

```yaml
services:
  dashboard-v2:
    build:
      context: .
      dockerfile: Dockerfile.dashboard-v2
    container_name: kimptrade-dashboard-v2
    restart: unless-stopped
    ports:
      - "8502:8502"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - REFRESH_INTERVAL=${REFRESH_INTERVAL:-10}
      - API_TIMEOUT=${API_TIMEOUT:-10}
      - FEE_RATE=${FEE_RATE:-0.0038}
      - DEBUG=${DEBUG:-false}
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8502/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 6.2 주요 명령어

```bash
# 상태 확인
docker ps
docker stats kimptrade-dashboard-v2

# 재시작
docker compose -f docker-compose.dashboard-v2.yml restart

# 로그
docker logs -f kimptrade-dashboard-v2 --tail 100

# 컨테이너 접속
docker exec -it kimptrade-dashboard-v2 /bin/bash
```

---

## 7. 네트워크

### 7.1 열린 포트

| 포트 | 서비스 | 상태 |
|------|--------|------|
| 22 | SSH | 열림 |
| 8502 | Dashboard V2 | 열림 |

### 7.2 방화벽 (UFW)

```bash
# 상태 확인
ufw status

# 현재 설정: SSH만 UFW에 등록
# Docker가 8502 포트를 iptables로 직접 관리
```

---

## 8. Troubleshooting

### 8.1 대시보드 접근 불가

```bash
# 1. 컨테이너 상태
docker ps | grep dashboard-v2

# 2. 로그 확인
docker logs kimptrade-dashboard-v2 --tail 50

# 3. 헬스체크
curl http://localhost:8502/api/health

# 4. 포트 확인
ss -tlnp | grep 8502
```

### 8.2 코드 변경이 반영 안 됨

```bash
# 캐시 없이 재빌드
docker compose -f docker-compose.dashboard-v2.yml build --no-cache
docker compose -f docker-compose.dashboard-v2.yml up -d
```

### 8.3 Supabase 연결 실패

```bash
# .env 확인
cat /root/order/.env | grep SUPA

# 컨테이너 내부에서 테스트
docker exec -it kimptrade-dashboard-v2 python -c "
from supabase import create_client
import os
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
print('Connected!')
"
```

---

## 9. 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2025-12-17 | Dashboard V2 배포 완료, V1 정리 |
| 2025-12-17 | 도메인 na4.pe.kr:8502 연결 확인 |
| 2025-12-17 | 문서 전면 재작성 |

---

## 10. 관련 문서

- [Dashboard 스펙](./docs/DASHBOARD_SPEC.md)
- [디자인 시스템](./docs/DESIGN_SYSTEM.md)
- [Feature Spec](./specs/003-dashboard-enhancement/spec.md)
