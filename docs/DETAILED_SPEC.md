# ⚡ Order 세부 기획서 Ver 3.0

**Repository:** trading-platform-order  
**Version:** 3.0  
**Date:** 2025-12-14  
**Updated:** Dual Track 청산, 환율 필터, Breakout Rescue 추가

> ⚠️ **핵심 철학:** "절대 손절하지 않는다 (No Stop Loss)"

---

## Ver 3.0 주요 변경사항

| 항목 | Ver 2.x | Ver 3.0 |
|:---|:---|:---|
| **청산 방식** | 단일 목표가 | **Dual Track** (정상익절 + Breakout Rescue) |
| **진입 전 검증** | 없음 | **환율 필터** (12시간 MA 대비 0.1% 초과 시 차단) |
| **exit_reason** | 없음 | **필수 저장** ('Target' / 'Breakout') |
| **손절** | 타임컷 고려 | **완전 비활성화** |

---

## 1. 개요

### 1.1 목적

research 레포에서 생성된 신호를 받아 **즉시 주문을 실행**하는 완전 자동화 시스템입니다.

### 1.2 핵심 책임

- **신호 수신:** research 레포에서 Signal 수신
- **환율 필터 확인:** ⭐ Ver 3.0 - 진입 전 환율 상태 검증
- **주문 생성:** 신호 → 주문 변환 (거래소별)
- **주문 실행:** 거래소 API 호출 (완전 자동)
- **Dual Track 청산:** ⭐ Ver 3.0 - 정상익절 OR Breakout Rescue
- **장애 복구:** One-leg Failure 자동 복구

---

## 2. 환율 필터 (Ver 3.0 신규)

### 2.1 개요

환율이 급등하는 구간에서는 김프가 구조적으로 하락/횡보하므로 진입을 차단합니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    환율 필터 로직                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   현재 환율 > 환율_12시간_MA × 1.001 → ⛔ 진입 차단              │
│   현재 환율 ≤ 환율_12시간_MA × 1.001 → ✅ 진입 허용              │
│                                                                 │
│   예시:                                                          │
│   - 12시간 MA: 1,378원                                          │
│   - 임계값: 1,378 × 1.001 = 1,379.38원                          │
│   - 현재 환율: 1,382원 → ⛔ 차단 (0.29% 초과)                    │
│   - 현재 환율: 1,377원 → ✅ 허용                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 구현

```python
# src/filters/exchange_rate_filter.py

from dataclasses import dataclass
from typing import Optional
import aiohttp

@dataclass
class ExchangeRateFilterResult:
    is_entry_allowed: bool
    current_rate: float
    ma_12h: float
    rate_ratio: float
    reason: Optional[str] = None

class ExchangeRateFilter:
    """
    환율 필터 (Ver 3.0)
    
    진입 전 환율 상태를 확인하여 불리한 시장에서의 진입을 방지
    """
    
    THRESHOLD_RATIO = 1.001  # 0.1% 초과 시 차단
    
    def __init__(self, storage_api_url: str):
        self.storage_api_url = storage_api_url
    
    async def check(self) -> ExchangeRateFilterResult:
        """
        환율 필터 상태 확인
        
        Returns:
            ExchangeRateFilterResult: 진입 허용 여부 및 상세 정보
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.storage_api_url}/fx/filter-status"
            ) as resp:
                data = await resp.json()
        
        is_allowed = not data['is_entry_blocked']
        
        return ExchangeRateFilterResult(
            is_entry_allowed=is_allowed,
            current_rate=data['current_rate'],
            ma_12h=data['ma_12h'],
            rate_ratio=data['rate_ratio'],
            reason=f"환율 급등 ({data['rate_ratio']:.4f} > 1.001)" if not is_allowed else None
        )
```

### 2.3 진입 플로우 적용

```python
async def execute_entry(self, signal: 'Signal') -> bool:
    """진입 실행 (환율 필터 적용)"""
    
    # Step 1: 환율 필터 확인
    filter_result = await self.exchange_rate_filter.check()
    
    if not filter_result.is_entry_allowed:
        await self.notifier.send(
            "⚠️ 진입 차단 (환율 필터)",
            f"현재 환율: {filter_result.current_rate:.2f}\n"
            f"12시간 MA: {filter_result.ma_12h:.2f}\n"
            f"Ratio: {filter_result.rate_ratio:.6f} > 1.001"
        )
        return False
    
    # Step 2: 기존 진입 로직 진행...
    return await self._execute_hedge_entry(signal)
```

---

## 3. Dual Track 청산 (Ver 3.0 핵심)

### 3.1 개요

Ver 3.0에서는 두 가지 청산 트랙을 동시에 모니터링합니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dual Track 청산 시스템                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Track A: 정상 익절 (Target Hit)                               │
│   ───────────────────────────────────                           │
│   조건: (현재김프 - 평단김프) ≥ 0.7%                             │
│   순익: ~0.32% (수수료 0.38% 차감)                              │
│   exit_reason: 'Target'                                        │
│                                                                 │
│   Track B: 돌파 탈출 (Breakout Rescue)                          │
│   ─────────────────────────────────────                         │
│   조건1: (현재김프 - 평단김프) ≥ 0.48%                           │
│   조건2: 현재김프 > 볼린저밴드 상단 (20, 2.0)                    │
│   순익: ~0.10%+ (최소 수익 확보)                                │
│   exit_reason: 'Breakout'                                      │
│                                                                 │
│   ※ Track A 우선 → Track B 차선                                │
│   ※ 둘 다 미충족 시 무한 보유 (No Stop Loss)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 구현

```python
# src/executor/exit_checker.py

from dataclasses import dataclass
from typing import Optional, Literal
from enum import Enum

class ExitReason(Enum):
    TARGET = "Target"       # Track A: 정상 익절
    BREAKOUT = "Breakout"   # Track B: 돌파 탈출

@dataclass
class ExitCheckResult:
    should_exit: bool
    reason: Optional[ExitReason] = None
    profit_pct: float = 0.0
    bb_upper: Optional[float] = None

class DualTrackExitChecker:
    """
    Dual Track 청산 체커 (Ver 3.0)
    
    두 가지 청산 조건을 동시에 모니터링:
    - Track A: 정상 목표가 도달
    - Track B: 볼린저밴드 돌파 + 최소 수익 확보
    """
    
    # Track A 파라미터
    TARGET_PROFIT_PCT = 0.007  # 0.7%
    
    # Track B 파라미터
    RESCUE_MIN_PROFIT_PCT = 0.0048  # 0.48%
    BB_PERIOD = 20
    BB_STDDEV = 2.0
    
    def __init__(self, indicator_service: 'KimpIndicatorService'):
        self.indicator_service = indicator_service
    
    async def check(
        self, 
        entry_kimp: float, 
        current_kimp: float
    ) -> ExitCheckResult:
        """
        청산 조건 확인
        
        Args:
            entry_kimp: 진입 시점 김프 (%)
            current_kimp: 현재 김프 (%)
        
        Returns:
            ExitCheckResult: 청산 여부 및 사유
        """
        profit_pct = current_kimp - entry_kimp
        
        # Track A: 정상 익절 (우선순위 1)
        if profit_pct >= self.TARGET_PROFIT_PCT:
            return ExitCheckResult(
                should_exit=True,
                reason=ExitReason.TARGET,
                profit_pct=profit_pct
            )
        
        # Track B: Breakout Rescue (우선순위 2)
        if profit_pct >= self.RESCUE_MIN_PROFIT_PCT:
            # 볼린저밴드 상단 조회
            indicators = await self.indicator_service.get_latest()
            bb_upper = indicators.bb_upper
            
            if current_kimp > bb_upper:
                return ExitCheckResult(
                    should_exit=True,
                    reason=ExitReason.BREAKOUT,
                    profit_pct=profit_pct,
                    bb_upper=bb_upper
                )
        
        # 청산 조건 미충족 → 무한 보유
        return ExitCheckResult(
            should_exit=False,
            profit_pct=profit_pct
        )
```

### 3.3 청산 실행 (exit_reason 저장)

```python
# src/executor/kimp_executor.py

async def execute_exit(
    self, 
    position: 'Position',
    exit_result: ExitCheckResult
) -> 'TradeResult':
    """
    청산 실행 (exit_reason 필수 저장)
    
    Args:
        position: 현재 포지션
        exit_result: 청산 체크 결과
    """
    # 동시 청산 실행
    upbit_result, binance_result = await asyncio.gather(
        self._execute_upbit_sell(position.btc_amount),
        self._execute_binance_close(position.btc_amount),
        return_exceptions=True
    )
    
    # 청산 기록 저장 (exit_reason 포함)
    trade_record = {
        'trade_id': position.trade_id,
        'exit_timestamp': datetime.utcnow(),
        'exit_kimp': exit_result.profit_pct + position.entry_kimp,
        'gross_pnl_pct': exit_result.profit_pct,
        'exit_reason': exit_result.reason.value,  # ⭐ 'Target' or 'Breakout'
        'status': 'CLOSED'
    }
    
    await self.storage.update_trade(trade_record)
    
    # 알림 전송
    emoji = "🎯" if exit_result.reason == ExitReason.TARGET else "🚀"
    await self.notifier.send(
        f"{emoji} 청산 완료 ({exit_result.reason.value})",
        f"수익률: {exit_result.profit_pct:.4%}\n"
        f"청산 사유: {exit_result.reason.value}"
    )
    
    return TradeResult(success=True, trade_id=position.trade_id)
```

---

## 4. 성능 최적화 (P0)

### 4.1 필수 라이브러리

```txt
# requirements.txt - 성능 최적화 패키지

uvloop==0.19.0         # asyncio 대체 - 2~4x 성능 향상
orjson==3.9.10         # json 대체 - 10~20x JSON 파싱
coincurve==18.0.0      # ECDSA 서명 - 45ms → 0.05ms
aiohttp==3.9.0         # 비동기 HTTP
ccxt==4.2.0            # 거래소 통합 (프로토타이핑)
```

### 4.2 성능 비교

| 영역 | 기본 | 최적화 후 | 개선율 |
|------|------|----------|--------|
| **Event Loop** | asyncio | uvloop | 2~4x |
| **JSON 파싱** | json | orjson | 10~20x |
| **API 서명** | ecdsa | coincurve | 900x |
| **총 주문 지연** | ~150ms | ~30ms | 5x |

---

## 5. One-leg Failure 복구 (P0)

### 5.1 문제 정의

김프 차익거래는 **업비트 + 바이낸스 동시 주문**이 필수입니다.
한쪽만 체결되면 헤지가 풀려 방향성 리스크에 노출됩니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    One-leg Failure 시나리오                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  정상: 업비트 BTC 매수 ✅ + 바이낸스 숏 진입 ✅ = 헤지 완성     │
│                                                                 │
│  장애: 업비트 BTC 매수 ✅ + 바이낸스 숏 실패 ❌ = 헤지 없음!    │
│        → BTC 가격 하락 시 손실 발생                             │
│                                                                 │
│  장애: 업비트 매수 실패 ❌ + 바이낸스 숏 진입 ✅ = 무한 숏!     │
│        → BTC 가격 상승 시 청산 위험                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 복구 전략

```python
# src/executor/one_leg_handler.py

class OneLegFailureHandler:
    """
    One-leg Failure 복구 핸들러
    
    복구 우선순위:
    1. 재시도 (최대 3회, 지수 백오프)
    2. 긴급 헤지 (반대 거래소에서 포지션 취소)
    3. 긴급 청산 (최후 수단)
    """
    
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # 지수 백오프 (초)
    
    async def handle(
        self, 
        upbit_result: Optional['Fill'],
        binance_result: Optional['Fill'],
        original_order: 'KimpOrder'
    ) -> OneLegResult:
        """One-leg Failure 처리"""
        failure_type = self._detect_failure(upbit_result, binance_result)
        
        if failure_type == FailureType.UPBIT_ONLY:
            return await self._handle_upbit_only(upbit_result, original_order)
        elif failure_type == FailureType.BINANCE_ONLY:
            return await self._handle_binance_only(binance_result, original_order)
        
        return await self._retry_both(original_order)
```

---

## 6. Circuit Breaker 패턴 (P1)

### 6.1 개요

연속 실패 시 시스템 보호를 위한 자동 차단 메커니즘입니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Circuit Breaker 상태                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   CLOSED ──(실패 5회)──▶ OPEN ──(30초 후)──▶ HALF_OPEN         │
│      ▲                                             │            │
│      │                                             │            │
│      └─────────────(성공)──────────────────────────┘            │
│                             │(실패)                             │
│                             ▼                                   │
│                           OPEN                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 주문 실행 파이프라인 (Ver 3.0)

### 7.1 진입 플로우

```
Step 1: 신호 수신
  research → Signal(action=ENTER, symbol=BTC, ...)

Step 2: 환율 필터 확인 ⭐ Ver 3.0
  IF exchange_rate_filter.is_blocked: SKIP with notification

Step 3: Circuit Breaker 확인
  IF circuit.is_open: WAIT or ALERT

Step 4: 중복 검사
  IF signal.id in processed_signals: SKIP

Step 5: 자본 배분 확인
  available = total_balance * 0.95  # 예비비 5% 제외

Step 6: 동시 실행
  asyncio.gather(upbit_buy, binance_short)

Step 7: One-leg Failure 확인
  IF one_leg_failure: handle_recovery()

Step 8: 체결 확인 & 저장
  storage.save(position)
```

### 7.2 청산 플로우 (Ver 3.0)

```
Loop (1초 간격):

Step 1: 현재 지표 조회
  current_kimp, bb_upper = get_indicators()

Step 2: Dual Track 청산 확인 ⭐ Ver 3.0
  exit_result = dual_track_checker.check(entry_kimp, current_kimp)

Step 3: 청산 실행 (조건 충족 시)
  IF exit_result.should_exit:
    execute_exit(position, exit_result)
    save_trade(exit_reason=exit_result.reason)  # 'Target' or 'Breakout'

Step 4: 무한 보유 (조건 미충족 시)
  ELSE:
    continue  # No Stop Loss
```

---

## 8. 디렉토리 구조 (Ver 3.0)

```
trading-platform-order/
├── README.md
├── pyproject.toml
├── config/
│   └── .env.example
│
├── docs/
│   ├── EXCHANGE_API.md
│   ├── DESIGN_SYSTEM.md
│   ├── RISK_MANAGEMENT.md
│   ├── DASHBOARD_SPEC.md
│   └── DETAILED_SPEC.md       # 이 문서
│
├── src/
│   ├── main.py                # uvloop 적용 진입점
│   │
│   ├── filters/               # ⭐ Ver 3.0 신규
│   │   ├── __init__.py
│   │   └── exchange_rate_filter.py
│   │
│   ├── executor/
│   │   ├── __init__.py
│   │   ├── kimp_executor.py
│   │   ├── exit_checker.py    # ⭐ Ver 3.0 Dual Track
│   │   ├── one_leg_handler.py
│   │   └── circuit_breaker.py
│   │
│   ├── exchanges/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── signature.py
│   │   ├── ccxt_upbit.py
│   │   └── ccxt_binance.py
│   │
│   └── capital/
│       ├── __init__.py
│       ├── allocator.py
│       └── fee_calculator.py
│
└── tests/
    ├── test_exit_checker.py     # ⭐ Ver 3.0
    ├── test_exchange_rate_filter.py  # ⭐ Ver 3.0
    ├── test_one_leg_handler.py
    └── test_circuit_breaker.py
```

---

## 9. 핵심 설정 요약 (Ver 3.0)

```python
# config/settings.py

VERSION = "3.0"

PERFORMANCE_CONFIG = {
    "use_uvloop": True,
    "use_orjson": True,
    "use_coincurve": True,
}

CAPITAL_CONFIG = {
    "trading_ratio": 0.95,
    "reserve_ratio": 0.05,
}

# ⭐ Ver 3.0: 환율 필터
EXCHANGE_RATE_FILTER_CONFIG = {
    "enabled": True,
    "ma_period_minutes": 720,     # 12시간
    "threshold_ratio": 1.001,     # 0.1% 초과 시 차단
}

# ⭐ Ver 3.0: Dual Track 청산
EXIT_CONFIG = {
    "strategy": "dual_track",
    
    # Track A: 정상 익절
    "track_a": {
        "target_profit_pct": 0.007,  # 0.7%
    },
    
    # Track B: Breakout Rescue
    "track_b": {
        "min_profit_pct": 0.0048,    # 0.48%
        "bb_period": 20,
        "bb_stddev": 2.0,
    },
    
    # 손절: 완전 비활성화
    "stop_loss": {
        "enabled": False,
    }
}

ONE_LEG_CONFIG = {
    "max_retries": 3,
    "retry_delays": [1, 2, 4],
    "emergency_hedge": True,
}

CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,
    "recovery_timeout": 30,
}
```

---

## 10. 구현 로드맵 (Ver 3.0)

| 우선순위 | 작업 | 산출물 | Phase |
|----------|------|--------|-------|
| **P0** | 환율 필터 구현 | ExchangeRateFilter | 3 |
| **P0** | Dual Track 청산 | DualTrackExitChecker | 3 |
| **P0** | exit_reason 저장 | DB 필드 추가 | 3 |
| **P0** | One-leg Failure 복구 | OneLegFailureHandler | 3 |
| P1 | Circuit Breaker | CircuitBreaker 클래스 | 4 |
| P2 | 직접 API 최적화 | DirectUpbit/BinanceAdapter | 5 |

---

*— Ver 3.0 문서 끝 —*
