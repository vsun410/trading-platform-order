# Vultr 서버 배포 가이드

## 서버 정보

| 서버 | 역할 | IP | URL |
|------|------|-----|-----|
| **Dashboard 서버** | FastAPI 대시보드 | 158.247.206.2 | http://158.247.206.2:8502 |
| Collector 서버 | 데이터 수집 (kimptrade) | 64.176.229.30 | - |

> **중요**: Dashboard는 kimptrade가 아닌 **이 레포(order)**에서 관리합니다.

---

## 현재 배포 상태

### Dashboard V2 (FastAPI) - 현재 운영 중
- **URL**: http://158.247.206.2:8502
- **컨테이너**: `kimptrade-dashboard-v2`
- **포트**: 8502
- **디자인**: Neon Daybreak (Lime-500, Hard Shadows)
- **레포 경로**: `/root/order`

### Dashboard V1 (Streamlit) - 레거시
- **URL**: http://158.247.206.2:8501
- **컨테이너**: `kimptrade-dashboard`
- **포트**: 8501
- **레포 경로**: `/root/kimptrade` (더 이상 업데이트 안함)

---

## 배포 방법 (Dashboard V2)

### 1. SSH 접속

```bash
ssh -i ~/.ssh/kimptrade_vultr root@158.247.206.2
```

### 2. 코드 업데이트

```bash
cd /root/order  # Dashboard V2 레포 경로

# 최신 코드 가져오기
git fetch origin
git checkout feat/dashboard-migration  # 또는 main (PR 머지 후)
git pull
```

### 3. Docker 재빌드 및 배포

```bash
# 캐시 없이 빌드
docker compose -f docker-compose.dashboard-v2.yml build --no-cache

# 컨테이너 재시작
docker compose -f docker-compose.dashboard-v2.yml down
docker compose -f docker-compose.dashboard-v2.yml up -d

# 로그 확인
docker logs -f kimptrade-dashboard-v2
```

### 4. 배포 확인

```bash
# 헬스체크
curl http://localhost:8502/api/health

# 컨테이너 상태
docker ps | grep dashboard-v2
```

## 빠른 배포 (로컬에서 한 번에)

```bash
ssh -i ~/.ssh/kimptrade_vultr root@158.247.206.2 "\
  cd /root/order && \
  git pull && \
  docker compose -f docker-compose.dashboard-v2.yml build --no-cache && \
  docker compose -f docker-compose.dashboard-v2.yml up -d"
```

---

## 주의사항

### ⚠️ 캐시 문제
Docker가 코드 변경을 인식하지 못하면:
```bash
docker compose -f docker-compose.dashboard.yml build --no-cache
```

### ⚠️ 환경변수
서버에 `.env` 파일 필요:
```env
SUPABASE_URL=https://shcgnkmlmjohmpeoyjlz.supabase.co
SUPABASE_KEY=eyJhbGc...  # anon key
```

### ⚠️ 포트 바인딩
- `127.0.0.1:8501`만 바인딩 (외부 직접 접근 불가)
- Cloudflare Tunnel 통해서만 외부 접근

### ⚠️ 레포 변경
- **기존**: kimptrade 레포에서 Dashboard 관리
- **현재**: order (trading-platform-order) 레포에서 관리
- 서버의 코드 경로도 업데이트 필요할 수 있음

---

## 파일 구조 (서버)

```
/root/kimptrade/  # 서버 경로 (변경 고려)
├── src/
│   └── dashboard/
│       ├── app.py
│       ├── components/
│       ├── services/
│       └── styles/
├── docker-compose.dashboard.yml
├── Dockerfile.dashboard
├── requirements.txt
└── .env
```

---

## Cloudflare Tunnel (이미 설정됨)

```
[사용자] → [Cloudflare Zero Trust] → [Cloudflare Tunnel] → [Dashboard 서버]
              (이메일 OTP 인증)         (cloudflared)        localhost:8501
```

터널 관리:
```bash
# 터널 상태 확인
systemctl status cloudflared

# 터널 재시작
systemctl restart cloudflared

# 터널 로그
journalctl -u cloudflared -n 50
```

---

## Troubleshooting

### 대시보드 접근 불가

```bash
# 1. 컨테이너 상태 확인
docker ps | grep dashboard

# 2. 컨테이너 로그 확인
docker logs kimptrade-dashboard --tail 50

# 3. 포트 확인
netstat -tlnp | grep 8501

# 4. 터널 상태 확인
systemctl status cloudflared
```

### 코드 변경이 반영 안 됨

```bash
# 1. 코드 확인
cat /root/kimptrade/src/dashboard/styles/neon_daybreak.py | head -20

# 2. 캐시 없이 재빌드
docker compose -f docker-compose.dashboard.yml build --no-cache
docker compose -f docker-compose.dashboard.yml up -d
```

### Supabase 연결 실패

```bash
# 1. .env 확인
cat /root/kimptrade/.env | grep SUPA

# 2. 컨테이너 내부에서 테스트
docker exec -it kimptrade-dashboard python -c "
from supabase import create_client
import os
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
print('Connected!')
"
```

---

## 빠른 배포 스크립트

로컬에서 실행:
```bash
# 1. 로컬 코드를 서버로 전송
scp -i ~/.ssh/kimptrade_vultr -r ./src/dashboard root@158.247.206.2:/root/kimptrade/src/

# 2. 서버에서 재빌드
ssh -i ~/.ssh/kimptrade_vultr root@158.247.206.2 "cd /root/kimptrade && docker compose -f docker-compose.dashboard.yml build --no-cache && docker compose -f docker-compose.dashboard.yml up -d"
```

---

## 참고

- **Dashboard 테스트 URL**: http://na4.pe.kr:8501
- **E2E 테스트**: `npm test` (Playwright)
- **Cloudflare 설정 문서**: `docs/CLOUDFLARE_SETUP.md` (kimptrade 레포)
