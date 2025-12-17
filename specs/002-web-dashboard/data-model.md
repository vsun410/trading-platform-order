# Data Model: Web Dashboard

**Feature**: 002-web-dashboard
**Date**: 2025-12-17

## Entities

### 1. EmergencyStop (system_status 테이블)

비상정지 상태를 저장하는 엔티티.

| Field | Type | Description |
|-------|------|-------------|
| key | VARCHAR(50) | Primary key, 'emergency_stop' 고정 |
| value | JSONB | 상태 정보 |
| value.active | boolean | 비상정지 활성화 여부 |
| value.activated_at | ISO8601 | 활성화 시간 (UTC) |
| value.deactivated_at | ISO8601 | 비활성화 시간 (UTC) |
| value.reason | string | 활성화 사유 |
| updated_at | TIMESTAMP | 마지막 업데이트 시간 |

**States**:
- `active = false`: 정상 거래 상태
- `active = true`: 비상정지 상태 (신규 진입 차단)

**SQL Schema**:
```sql
CREATE TABLE IF NOT EXISTS system_status (
    key VARCHAR(50) PRIMARY KEY,
    value JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 초기 데이터
INSERT INTO system_status (key, value)
VALUES ('emergency_stop', '{"active": false}')
ON CONFLICT (key) DO NOTHING;
```

---

### 2. Position (기존 positions 테이블 활용)

현재 오픈 포지션 정보. 대시보드에서 조회만 수행.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| status | VARCHAR | 'open' / 'closed' |
| entry_kimp | DECIMAL | 진입 시 김프율 |
| entry_timestamp | TIMESTAMP | 진입 시간 |
| upbit_quantity | DECIMAL | 업비트 BTC 수량 |
| upbit_entry_price | DECIMAL | 업비트 진입가 (KRW) |
| binance_quantity | DECIMAL | 바이낸스 BTC 수량 |
| binance_entry_price | DECIMAL | 바이낸스 진입가 (USDT) |
| exit_reason | VARCHAR | 'Target' / 'Breakout' / NULL |
| realized_pnl | DECIMAL | 실현 손익 |

**Query Pattern**:
```sql
-- 현재 오픈 포지션 조회
SELECT * FROM positions WHERE status = 'open' ORDER BY entry_timestamp DESC LIMIT 1;
```

---

### 3. Trade (기존 trades 테이블 활용)

거래 이력. 대시보드에서 최근 10건 조회.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| position_id | UUID | 관련 포지션 |
| exchange | VARCHAR | 'upbit' / 'binance' |
| side | VARCHAR | 'buy' / 'sell' / 'short' / 'cover' |
| quantity | DECIMAL | 거래 수량 |
| price | DECIMAL | 체결 가격 |
| fee | DECIMAL | 수수료 |
| timestamp | TIMESTAMP | 거래 시간 |

**Query Pattern**:
```sql
-- 최근 10건 거래 조회
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;
```

---

### 4. KimpData (기존 kimp_1m 테이블 활용)

김프율 데이터. 차트 표시용.

| Field | Type | Description |
|-------|------|-------------|
| timestamp | TIMESTAMP | 데이터 시간 |
| upbit_price | DECIMAL | 업비트 BTC/KRW 가격 |
| binance_price | DECIMAL | 바이낸스 BTCUSDT 가격 |
| exchange_rate | DECIMAL | USD/KRW 환율 |
| kimp_rate | DECIMAL | 김프율 (%) |

**Query Pattern**:
```sql
-- 최근 1시간 김프 데이터 조회
SELECT timestamp, kimp_rate, upbit_price, binance_price, exchange_rate
FROM kimp_1m
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp ASC;
```

---

### 5. SystemHealth (런타임 데이터, DB 저장 안 함)

시스템 연결 상태. 대시보드에서 실시간 체크.

| Field | Type | Description |
|-------|------|-------------|
| upbit_status | string | 'ok' / 'error' |
| upbit_latency_ms | number | 응답 시간 (ms) |
| binance_status | string | 'ok' / 'error' |
| binance_latency_ms | number | 응답 시간 (ms) |
| fx_status | string | 'ok' / 'error' |
| db_status | string | 'ok' / 'error' |
| last_check | ISO8601 | 마지막 체크 시간 |

**Implementation**: 대시보드 로드 시 각 서비스에 ping 요청하여 상태 확인.

---

## Relationships

```
┌─────────────────┐
│ system_status   │──── EmergencyStop 상태 (독립)
└─────────────────┘

┌─────────────────┐      ┌─────────────────┐
│   positions     │──1:N─│     trades      │
└─────────────────┘      └─────────────────┘
        │
        │ 참조
        ▼
┌─────────────────┐
│    kimp_1m      │──── 김프 데이터 (참조용)
└─────────────────┘
```

## Data Flow

```
1. 대시보드 로드
   │
   ├─► Supabase: system_status 조회 (비상정지 상태)
   ├─► Supabase: positions 조회 (현재 포지션)
   ├─► Supabase: trades 조회 (최근 거래)
   ├─► Supabase: kimp_1m 조회 (차트 데이터)
   └─► API Ping: 시스템 상태 체크

2. 비상정지 활성화
   │
   ├─► Supabase: system_status UPDATE
   └─► Telegram: 알림 발송

3. 데이터 갱신 (10초 주기)
   │
   └─► 1번 반복
```
