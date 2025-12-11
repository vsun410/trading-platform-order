# 🛡️ 자본 운용 & 청산 전략 가이드

**Version:** 2.0  
**Updated:** 2025-12-11  
**Strategy:** 김프 차익거래 (Cash &amp; Carry Arbitrage)

> ⚠️ **중요:** 이 문서는 김프 차익거래 전략에 특화된 자본 운용 가이드입니다.
> 일반적인 방향성 트레이딩과는 다른 원칙이 적용됩니다.

---

## 1. 전략 특성 이해

### 1.1 김프 차익거래 = 완전 헤지 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                    포지션 구조 (완전 헤지)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [업비트]                          [바이낸스]                   │
│   BTC 현물 매수 (Long)    ←─헤지─→   BTCUSDT 선물 매도 (Short)  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ BTC 가격 상승 시:                                        │   │
│   │   → 업비트: +이익  /  바이낸스: -손실  =  상쇄            │   │
│   │                                                         │   │
│   │ BTC 가격 하락 시:                                        │   │
│   │   → 업비트: -손실  /  바이낸스: +이익  =  상쇄            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ★ 가격 방향성 리스크 = 0 (완전 중립)                          │
│   ★ 순수익 = 김프 축소분 + 펀딩비 수익 - 수수료                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 왜 손절하면 안 되는가?

| 시나리오 | 손절 시 결과 | 홀딩 시 결과 |
|----------|-------------|-------------|
| 역프 발생 (-2%) | ❌ 손실 -2% **확정** | ✅ 프리미엄 복귀 대기 → 수익 전환 |
| 김프 확대 (5% → 7%) | ❌ 기회 손실 | ✅ 더 큰 수익 기회로 전환 |
| 일시적 변동 | ❌ 불필요한 손실 | ✅ 변동 무시, 수렴 대기 |

**결론:** 헤지된 포지션에서 손절 = 손실 확정 = 불필요한 행위

---

## 2. 자본 배분 규칙

### 2.1 배분 비율

| 구분 | 비율 | 금액 (2천만원 기준) | 용도 |
|------|------|---------------------|------|
| **트레이딩 자본** | 95% | 19,000,000 원 | 김프 차익거래 포지션 |
| **예비비** | 5% | 1,000,000 원 | 수수료, 마진콜, 긴급 대비 |

### 2.2 예비비 사용 목적

```python
RESERVE_USAGE = {
    "trading_fees": "거래 수수료 (진입/청산)",
    "funding_fee_buffer": "음수 펀딩비 발생 시 버퍼",
    "margin_call_prevention": "선물 마진 부족 시 추가 입금",
    "slippage_buffer": "슬리피지 대응",
    "emergency": "예상치 못한 긴급 상황",
}
```

### 2.3 자본 배분 설정

```python
# config/capital.py

CAPITAL_CONFIG = {
    # 기본 배분
    "trading_ratio": 0.95,        # 95% 투입
    "reserve_ratio": 0.05,        # 5% 예비비
    
    # 거래소별 배분 (트레이딩 자본 내)
    "upbit_ratio": 0.50,          # 50% → 업비트 현물
    "binance_ratio": 0.50,        # 50% → 바이낸스 선물 마진
    
    # 레버리지 (선물)
    "binance_leverage": 1,        # 1배 (마진과 동일 수량)
}
```

---

## 3. 청산 조건

### 3.1 핵심 원칙

> 🚫 **절대 금지:** 손실 상태에서의 청산
> 
> ✅ **유일한 청산 조건:** `차익 - 수수료 > 0`

### 3.2 청산 판단 공식

```python
def calculate_net_profit(position: Position, current_kimp: Decimal) -> Decimal:
    """순이익 계산"""
    
    # 1. 김프 차익 (진입 김프 - 현재 김프)
    kimp_profit = position.entry_kimp - current_kimp
    
    # 2. 누적 펀딩비 수익
    funding_profit = position.accumulated_funding
    
    # 3. 총 수수료 (진입 + 청산)
    total_fees = calculate_total_fees(position)
    
    # 4. 순이익
    net_profit = kimp_profit + funding_profit - total_fees
    
    return net_profit


def should_exit(position: Position, current_kimp: Decimal) -> ExitDecision:
    """청산 가능 여부 판단"""
    
    net_profit = calculate_net_profit(position, current_kimp)
    
    if net_profit > 0:
        return ExitDecision(
            allowed=True,
            reason=f"순이익 {net_profit:.2%} 실현 가능",
        )
    else:
        return ExitDecision(
            allowed=False,
            reason=f"순이익 미달 ({net_profit:.2%}), 프리미엄 수렴 대기",
        )
```

### 3.3 수수료 구조

```python
# 수수료율 (2025년 기준)
FEES = {
    # 업비트 현물
    "upbit_taker": 0.0005,      # 0.05%
    "upbit_maker": 0.0005,      # 0.05%
    
    # 바이낸스 선물 (USDT-M)
    "binance_taker": 0.0005,    # 0.05% (일반)
    "binance_maker": 0.0002,    # 0.02% (일반)
    # VIP/BNB 할인 적용 시 더 낮음
}

# 왕복 수수료 계산 (시장가 기준)
def total_round_trip_fee():
    entry = FEES["upbit_taker"] + FEES["binance_taker"]   # 진입
    exit = FEES["upbit_taker"] + FEES["binance_taker"]    # 청산
    return entry + exit  # ≈ 0.20%
```

### 3.4 청산 예시

```
예시 1: 청산 허용 ✅
─────────────────────────
진입 김프: 3.5%
현재 김프: 1.0%
펀딩비 수익: +0.1%
수수료: -0.2%

순이익 = (3.5% - 1.0%) + 0.1% - 0.2%
       = 2.5% + 0.1% - 0.2%
       = +2.4% ✅ 청산 가능


예시 2: 청산 금지 ❌
─────────────────────────
진입 김프: 2.0%
현재 김프: 2.5% (역프 발생)
펀딩비 수익: +0.05%
수수료: -0.2%

순이익 = (2.0% - 2.5%) + 0.05% - 0.2%
       = -0.5% + 0.05% - 0.2%
       = -0.65% ❌ 청산 금지, 수렴 대기
```

---

## 4. 시스템 안전장치

### 4.1 유지되는 안전장치

| 항목 | 설정 | 동작 |
|------|------|------|
| 중복 주문 방지 | 신호 ID 멱등성 | 동일 신호 재처리 차단 |
| API 에러 재시도 | 최대 3회 | 1s → 2s → 4s 백오프 |
| Rate Limit | 쓰로틀링 | Semaphore 기반 제어 |
| 네트워크 타임아웃 | 10초 | 자동 재연결 |
| 포지션 불일치 | 알림 발송 | Discord 긴급 알림 |

### 4.2 제거된 항목 (김프 차익거래에 부적합)

```python
# ❌ 제거된 설정 - 사용하지 않음
REMOVED_RISK_CONFIGS = {
    "max_position_size": "제거됨 - 95% 전액 투입",
    "max_daily_loss": "제거됨 - 손실 기반 정지 없음",
    "stop_loss_pct": "제거됨 - 손절 금지",
    "take_profit_pct": "제거됨 - 순이익 기반으로 대체",
    "trailing_stop_pct": "제거됨 - 불필요",
}
```

### 4.3 긴급 정지 조건

```python
# 시스템 레벨 긴급 정지만 유지
EMERGENCY_STOP_CONDITIONS = [
    "api_error_count > 10",           # 연속 API 에러 10회
    "position_severe_mismatch",       # 심각한 포지션 불일치
    "manual_stop_flag",               # 수동 정지 플래그
    "exchange_maintenance",           # 거래소 점검
    "network_failure_prolonged",      # 장시간 네트워크 장애
]

# ❌ 손실 기반 조건 없음
# - daily_loss_limit 없음
# - position_loss_limit 없음  
# - kimp_reversal_stop 없음
```

---

## 5. 알림 설정

### 5.1 알림 이벤트

| 이벤트 | 채널 | 우선순위 |
|--------|------|----------|
| 포지션 진입 | Discord | 일반 |
| 포지션 청산 (수익) | Discord | 일반 |
| 청산 거부 (손실 상태) | Discord | 정보 |
| 포지션 불일치 감지 | Discord | ⚠️ 경고 |
| API 연속 에러 | Discord | ⚠️ 경고 |
| 시스템 긴급 정지 | Discord + Email | 🚨 긴급 |
| 일일 리포트 | Discord | 일반 |

### 5.2 알림 예시

```python
# 청산 거부 알림
async def notify_exit_rejected(position, reason):
    await discord.send(
        channel="trading-alerts",
        embed={
            "title": "❌ 청산 거부",
            "color": "yellow",
            "fields": [
                {"name": "심볼", "value": position.symbol},
                {"name": "진입 김프", "value": f"{position.entry_kimp:.2%}"},
                {"name": "현재 김프", "value": f"{current_kimp:.2%}"},
                {"name": "사유", "value": reason},
                {"name": "상태", "value": "📍 프리미엄 수렴 대기 중"},
            ]
        }
    )
```

---

## 6. 설정 파일 (최종)

```python
# config/settings.py

# ═══════════════════════════════════════════════════════════════
# 자본 배분 설정
# ═══════════════════════════════════════════════════════════════
CAPITAL_CONFIG = {
    "trading_ratio": 0.95,            # 95% 트레이딩
    "reserve_ratio": 0.05,            # 5% 예비비
    "upbit_ratio": 0.50,              # 업비트 배분
    "binance_ratio": 0.50,            # 바이낸스 배분
    "binance_leverage": 1,            # 선물 레버리지
}

# ═══════════════════════════════════════════════════════════════
# 청산 조건 설정
# ═══════════════════════════════════════════════════════════════
EXIT_CONFIG = {
    "min_net_profit": 0,              # 순이익 > 0 이어야 청산
    "include_funding": True,          # 펀딩비 수익 포함
    "allow_loss_exit": False,         # ❌ 손실 청산 금지
}

# ═══════════════════════════════════════════════════════════════
# 수수료 설정
# ═══════════════════════════════════════════════════════════════
FEE_CONFIG = {
    "upbit_taker": 0.0005,
    "upbit_maker": 0.0005,
    "binance_taker": 0.0005,
    "binance_maker": 0.0002,
}

# ═══════════════════════════════════════════════════════════════
# 시스템 안전장치
# ═══════════════════════════════════════════════════════════════
SAFETY_CONFIG = {
    "max_api_errors": 10,             # 연속 API 에러 한도
    "api_timeout": 10,                # API 타임아웃 (초)
    "retry_attempts": 3,              # 재시도 횟수
    "position_mismatch_alert": True,  # 불일치 알림
}

# ═══════════════════════════════════════════════════════════════
# 비활성화된 설정 (사용하지 않음)
# ═══════════════════════════════════════════════════════════════
DISABLED_CONFIG = {
    # "max_position_size": 0.2,       # 비활성화
    # "max_daily_loss": 0.05,         # 비활성화
    # "stop_loss_pct": 0.03,          # 비활성화
    # "take_profit_pct": 0.10,        # 비활성화
    # "trailing_stop_pct": 0.03,      # 비활성화
}
```

---

## 7. 체크리스트

### 진입 전 확인

- [ ] 총 자본의 95% 투입 준비 완료
- [ ] 예비비 5% 별도 확보
- [ ] 업비트/바이낸스 잔고 50:50 배분
- [ ] 바이낸스 레버리지 1배 설정

### 청산 시 확인

- [ ] 순이익 > 0 인가?
- [ ] 수수료 계산 완료?
- [ ] 펀딩비 수익 포함?
- [ ] **손실 상태라면 → 청산하지 않음**

### 모니터링

- [ ] 포지션 동기화 상태 정상
- [ ] API 연결 상태 정상
- [ ] 알림 시스템 작동 중

---

*— 문서 끝 —*
