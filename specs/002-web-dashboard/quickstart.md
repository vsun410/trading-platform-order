# Quickstart: Web Dashboard (분리 서버 배포)

**Feature**: 002-web-dashboard
**Date**: 2025-12-17

## 아키텍처 개요

```
Collector 서버 (64.176.229.30)     Dashboard 서버 (신규)
       │                                  │
       └──────────┬───────────────────────┘
                  ▼
           Supabase (클라우드)
```

- **Collector 서버**: 데이터 수집 전용 (기존 유지)
- **Dashboard 서버**: 대시보드 + Cloudflare Tunnel (신규 생성)

## Prerequisites

- Vultr 계정 (새 서버 생성용)
- Cloudflare 계정 + 도메인 (DNS 연결됨)
- 기존 kimptrade .env 파일 (Supabase 접속 정보)

---

## 1. Dashboard 서버 생성 (Vultr)

### 1.1 새 서버 생성

1. [Vultr Console](https://my.vultr.com/) 접속
2. **Deploy New Server** 클릭
3. 설정:
   - **Type**: Cloud Compute - Shared CPU
   - **Location**: Seoul (또는 기존 서버와 동일 리전)
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: 1 vCPU / 1GB RAM / 25GB SSD ($5/월)
   - **SSH Key**: 기존 kimptrade_vultr 키 선택
   - **Hostname**: `kimptrade-dashboard`
4. **Deploy Now** 클릭
5. IP 주소 기록 (예: `xxx.xxx.xxx.xxx`)

### 1.2 SSH 접속 확인

```bash
# 새 서버 접속 (~/.ssh/config에 추가 권장)
ssh -i ~/.ssh/kimptrade_vultr root@<DASHBOARD_SERVER_IP>
```

---

## 2. Dashboard 서버 초기 설정

### 2.1 시스템 업데이트 및 Docker 설치

```bash
# SSH 접속 후
apt update && apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com | sh

# Docker Compose 설치
apt install -y docker-compose-plugin

# 확인
docker --version
docker compose version
```

### 2.2 프로젝트 클론

```bash
cd /root
git clone https://github.com/vsun410/kimptrade.git
cd kimptrade
```

### 2.3 환경변수 설정

```bash
# .env 파일 생성 (Supabase 접속 정보만 필요)
cat > .env << 'EOF'
# Supabase (필수)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Telegram (선택 - 비상정지 알림용)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
EOF

# 실제 값으로 수정
nano .env
```

---

## 3. Supabase 마이그레이션

> **중요**: system_status 테이블이 없으면 비상정지 기능이 동작하지 않습니다.

### Supabase Dashboard에서 실행

1. [Supabase Dashboard](https://supabase.com/dashboard) → 프로젝트 선택
2. **SQL Editor** 클릭
3. 아래 SQL 실행:

```sql
-- 비상정지 상태 저장 테이블
CREATE TABLE IF NOT EXISTS system_status (
    key VARCHAR(50) PRIMARY KEY,
    value JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 초기 데이터 삽입
INSERT INTO system_status (key, value)
VALUES ('emergency_stop', '{"active": false}')
ON CONFLICT (key) DO NOTHING;
```

### 확인

```sql
SELECT * FROM system_status WHERE key = 'emergency_stop';
```

---

## 4. Dashboard 배포

### 4.1 대시보드 전용 docker-compose 생성

```bash
# Dashboard 서버에서
cat > docker-compose.dashboard.yml << 'EOF'
version: '3.8'

services:
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    container_name: kimptrade-dashboard
    restart: unless-stopped
    ports:
      - "127.0.0.1:8501:8501"  # localhost만 바인딩
    env_file:
      - .env
    environment:
      - TZ=Asia/Seoul
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF
```

### 4.2 빌드 및 실행

```bash
# 이미지 빌드
docker compose -f docker-compose.dashboard.yml build

# 컨테이너 시작
docker compose -f docker-compose.dashboard.yml up -d

# 상태 확인
docker ps
docker logs kimptrade-dashboard
```

### 4.3 로컬 접속 테스트

```bash
# Dashboard 서버에서
curl http://localhost:8501/_stcore/health
# 정상이면 "ok" 반환
```

---

## 5. Cloudflare Tunnel 설정

### 5.1 cloudflared 설치

```bash
# Dashboard 서버에서
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
dpkg -i cloudflared.deb
cloudflared version
```

### 5.2 Cloudflare 로그인

```bash
cloudflared tunnel login
# 브라우저에서 인증 (URL 출력됨)
```

### 5.3 터널 생성

```bash
cloudflared tunnel create kimptrade-dashboard
# 출력된 TUNNEL_ID 기록
# 예: Created tunnel kimptrade-dashboard with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 5.4 설정 파일 생성

```bash
mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <TUNNEL_ID>
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: dashboard.yourdomain.com
    service: http://localhost:8501
  - service: http_status:404
EOF

# <TUNNEL_ID>와 도메인을 실제 값으로 수정
nano ~/.cloudflared/config.yml
```

### 5.5 DNS 레코드 추가

```bash
cloudflared tunnel route dns kimptrade-dashboard dashboard.yourdomain.com
```

### 5.6 서비스 등록 및 시작

```bash
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared

# 상태 확인
systemctl status cloudflared
```

---

## 6. Zero Trust Access 설정

> Cloudflare Dashboard에서 설정 (웹 UI)

### 6.1 Application 추가

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → **Zero Trust**
2. **Access** → **Applications** → **Add an application**
3. **Self-hosted** 선택
4. 설정:
   - Application name: `kimptrade-dashboard`
   - Session Duration: `24 hours`
   - Application domain: `dashboard.yourdomain.com`

### 6.2 Policy 추가

1. **Add a policy**
2. 설정:
   - Policy name: `Allow Owner`
   - Action: **Allow**
   - Include: **Emails** → 허용할 이메일 주소 입력

### 6.3 Identity Provider

1. **Settings** → **Authentication** → **Login methods**
2. **Add** → **One-time PIN** 선택
3. Save

---

## 7. 접속 테스트

### 7.1 외부 접속

1. `https://dashboard.yourdomain.com` 접속
2. 이메일 입력 → OTP 코드 수신
3. 코드 입력 → 대시보드 표시 확인

### 7.2 비상정지 테스트

1. 🔴 **비상정지** 버튼 클릭
2. 확인 다이얼로그 → **확인**
3. 상태가 "🔴 비상정지 활성화"로 변경 확인
4. Telegram 알림 수신 확인
5. 🟢 **재개** 버튼으로 복구

---

## Troubleshooting

### Dashboard 컨테이너 문제

```bash
# 로그 확인
docker logs kimptrade-dashboard

# 재시작
docker compose -f docker-compose.dashboard.yml restart

# 재빌드
docker compose -f docker-compose.dashboard.yml down
docker compose -f docker-compose.dashboard.yml build --no-cache
docker compose -f docker-compose.dashboard.yml up -d
```

### Cloudflare Tunnel 문제

```bash
# 터널 상태 확인
cloudflared tunnel info kimptrade-dashboard

# 로그 확인
journalctl -u cloudflared -f

# 설정 확인
cat ~/.cloudflared/config.yml
```

### Supabase 연결 문제

```bash
# .env 확인
cat .env | grep SUPABASE

# 컨테이너 내부에서 테스트
docker exec -it kimptrade-dashboard python -c "
from src.database.supabase_client import SupabaseClient
db = SupabaseClient()
print(db._client.table('system_status').select('*').execute())
"
```

---

## 서버 관리 명령어

```bash
# Dashboard 서버 상태 확인
docker ps
systemctl status cloudflared

# 로그 확인
docker logs -f kimptrade-dashboard
journalctl -u cloudflared -f

# 업데이트 (git pull 후)
cd /root/kimptrade
git pull
docker compose -f docker-compose.dashboard.yml build
docker compose -f docker-compose.dashboard.yml up -d
```
