# ⚡ 김치프리미엄 주문 실행 명세 (Ver 3.0)

## 1. 실행 시스템 개요

### 1.1 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Order Execution System (Ver 3.0)                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│   │  Signal     │ →   │   Filter    │ →   │  Executor   │           │
│   │  Detector   │     │  (FX+Entry) │     │  (CCXT)     │           │
│   └─────────────┘     └─────────────┘     └─────────────┘           │
│         │                    │                    │                  │
│         │                    │                    ▼                  │
│         │                    │            ┌─────────────┐           │
│         │                    │            │   Upbit     │           │
│         │                    │            │ + Binance   │           │
│         │                    │            │  동시 실행   │           │
│         │                    │            └─────────────┘           │
│         │                    │                    │                  │
│         ▼                    ▼                    ▼                  │
│   ┌─────────────────────────────────────────────────────┐          │
│   │                   Exit Monitor                       │          │
│   │  ┌─────────────┐          ┌─────────────┐          │          │
│   │  │  Track A    │    OR    │  Track B    │          │          │
│   │  │  (Target)   │          │ (Breakout)  │          │          │
│   │  │  0.7% 익절  │          │ BB돌파탈출   │          │          │
│   │  └─────────────┘          └─────────────┘          │          │
│   └─────────────────────────────────────────────────────┘          │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Ver 3.0 변경사항

| 항목 | 기존 | Ver 3.0 |
|:---|:---|:---|
| 진입 필터 | Z-Score만 | **환율 필터 + Z-Score** |
| 청산 로직 | 단일 목표가 | **Dual Track (Target + Breakout)** |
| exit_reason | 없음 | **'Target' / 'Breakout'** 기록 |

---

## 2. 진입 실행 (Entry Execution)

### 2.1 진입 흐름도

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Entry Flow (Ver 3.0)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   [1] Z-Score 회귀 감지                                              │
│        │                                                              │
│        ▼                                                              │
│   [2] 환율 필터 체크 (NEW)                                           │
│        ├─ 환율 > MA_12h × 1.001 → ⛔ 진입 차단                       │
│        └─ 환율 ≤ MA_12h × 1.001 → ✅ 진입 진행                       │
│                                     │                                 │
│                                     ▼                                 │
│   [3] 진입 레벨 결정                                                 │
│        ├─ Level 1: 40% (Z > -2.0 회귀)                               │
│        ├─ Level 2: 60% 추가 (Z > -2.5 회귀)                          │
│        └─ Full: 100% (-2.5 직행 후 회귀)                             │
│                     │                                                 │
│                     ▼                                                 │
│   [4] 동시 주문 실행                                                 │
│        ├─ Upbit: 현물 BTC 매수                                       │
│        └─ Binance: BTCUSDT 선물 SHORT                                │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 진입 실행 코드

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import asyncio

class EntryLevel(Enum):
    LEVEL1 = "level1"      # 40%
    LEVEL2 = "level2"      # 60% 추가
    FULL = "combined"      # 100%

@dataclass
class EntrySignal:
    level: EntryLevel
    zscore: float
    kimp: float
    fx_rate: float
    fx_ma_12h: float

@dataclass
class EntryResult:
    success: bool
    position_id: Optional[str]
    upbit_order_id: Optional[str]
    binance_order_id: Optional[str]
    error: Optional[str]

class EntryExecutor:
    """진입 실행기 (Ver 3.0)"""
    
    def __init__(self, upbit_client, binance_client, config):
        self.upbit = upbit_client
        self.binance = binance_client
        self.config = config
        
        # 환율 필터 설정
        self.fx_surge_threshold = 1.001  # +0.1%
    
    async def execute_entry(self, signal: EntrySignal) -> EntryResult:
        """진입 실행"""
        
        # Step 1: 환율 필터 체크 (Ver 3.0)
        if self._is_fx_blocked(signal.fx_rate, signal.fx_ma_12h):
            return EntryResult(
                success=False,
                position_id=None,
                upbit_order_id=None,
                binance_order_id=None,
                error=f"FX filter blocked: {signal.fx_rate:.2f} > {signal.fx_ma_12h * self.fx_surge_threshold:.2f}"
            )
        
        # Step 2: 진입 금액 계산
        capital = self._calculate_entry_capital(signal.level)
        
        # Step 3: 동시 주문 실행
        try:
            upbit_order, binance_order = await asyncio.gather(
                self._execute_upbit_buy(capital['upbit']),
                self._execute_binance_short(capital['binance']),
                return_exceptions=True
            )
            
            # 롤백 체크
            if isinstance(upbit_order, Exception) or isinstance(binance_order, Exception):
                await self._rollback(upbit_order, binance_order)
                return EntryResult(
                    success=False,
                    position_id=None,
                    upbit_order_id=None,
                    binance_order_id=None,
                    error=f"Order failed: {upbit_order}, {binance_order}"
                )
            
            # 포지션 생성
            position_id = await self._create_position(
                signal, upbit_order, binance_order
            )
            
            return EntryResult(
                success=True,
                position_id=position_id,
                upbit_order_id=upbit_order['id'],
                binance_order_id=binance_order['id'],
                error=None
            )
            
        except Exception as e:
            return EntryResult(
                success=False,
                position_id=None,
                upbit_order_id=None,
                binance_order_id=None,
                error=str(e)
            )
    
    def _is_fx_blocked(self, current_rate: float, ma_12h: float) -> bool:
        """환율 필터 체크"""
        threshold = ma_12h * self.fx_surge_threshold
        return current_rate > threshold
    
    def _calculate_entry_capital(self, level: EntryLevel) -> dict:
        """진입 자본 계산"""
        trading_capital = self.config.trading_capital  # 38,000,000
        
        ratios = {
            EntryLevel.LEVEL1: 0.40,
            EntryLevel.LEVEL2: 0.60,
            EntryLevel.FULL: 1.00
        }
        
        total = trading_capital * ratios[level]
        
        return {
            'total': total,
            'upbit': total * 0.5,      # 현물 50%
            'binance': total * 0.5     # 선물 50%
        }
    
    async def _execute_upbit_buy(self, amount_krw: float):
        """업비트 현물 매수"""
        return await self.upbit.create_market_buy_order(
            symbol='BTC/KRW',
            amount=None,  # KRW 금액 기준
            params={'cost': amount_krw}
        )
    
    async def _execute_binance_short(self, amount_krw: float):
        """바이낸스 선물 숏"""
        # KRW → USDT 변환
        usdt_amount = amount_krw / self.config.current_fx_rate
        btc_amount = usdt_amount / self.config.current_btc_price
        
        return await self.binance.create_market_sell_order(
            symbol='BTC/USDT:USDT',
            amount=btc_amount
        )
    
    async def _rollback(self, upbit_order, binance_order):
        """실패 시 롤백"""
        if not isinstance(upbit_order, Exception):
            await self.upbit.create_market_sell_order(
                symbol='BTC/KRW',
                amount=upbit_order['filled']
            )
        
        if not isinstance(binance_order, Exception):
            await self.binance.create_market_buy_order(
                symbol='BTC/USDT:USDT',
                amount=binance_order['filled']
            )
```

---

## 3. 청산 실행 (Exit Execution) - Dual Track

### 3.1 Dual Track 청산 흐름

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Dual Track Exit System (Ver 3.0)                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   [매 1초 체크]                                                      │
│        │                                                              │
│        ├── Track A: 정상 익절 ──────────────────────────────────────│
│        │    조건: (현재김프 - 진입김프) ≥ 0.7%                       │
│        │    행동: 전량 청산                                          │
│        │    기록: exit_reason = 'Target'                            │
│        │                                                              │
│        └── Track B: Breakout 탈출 ──────────────────────────────────│
│             조건 1: (현재김프 - 진입김프) ≥ 0.48%                    │
│             조건 2: 현재김프 > BB_Upper(20, 2.0)                     │
│             행동: 전량 청산                                          │
│             기록: exit_reason = 'Breakout'                          │
│                                                                       │
│   ※ Track A가 먼저 체크되며, A 조건 충족 시 B는 체크하지 않음        │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 청산 모니터 코드

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import asyncio

class ExitReason(Enum):
    TARGET = "Target"      # Track A: 정상 익절
    BREAKOUT = "Breakout"  # Track B: BB 돌파 탈출

@dataclass
class ExitSignal:
    reason: ExitReason
    current_kimp: float
    entry_kimp: float
    profit_pct: float
    bb_upper: Optional[float]

@dataclass
class ExitResult:
    success: bool
    exit_reason: ExitReason
    realized_pnl: float
    realized_pnl_pct: float
    error: Optional[str]

class ExitMonitor:
    """청산 모니터 (Ver 3.0 Dual Track)"""
    
    # 청산 파라미터
    TARGET_PROFIT_PCT = 0.70     # Track A: 0.7%
    BREAKOUT_MIN_PCT = 0.48      # Track B: 최소 0.48%
    BB_PERIOD = 20
    BB_STD_MULT = 2.0
    
    def __init__(self, data_feed, executor):
        self.data_feed = data_feed
        self.executor = executor
        self.monitoring = False
    
    async def start_monitoring(self, position):
        """청산 모니터링 시작"""
        self.monitoring = True
        
        while self.monitoring:
            # 1초마다 체크
            exit_signal = await self._check_exit_conditions(position)
            
            if exit_signal:
                result = await self.executor.execute_exit(position, exit_signal)
                self.monitoring = False
                return result
            
            await asyncio.sleep(1)
    
    async def _check_exit_conditions(self, position) -> Optional[ExitSignal]:
        """청산 조건 체크 (Dual Track)"""
        
        current_kimp = await self.data_feed.get_current_kimp()
        entry_kimp = position.entry_kimp
        profit_pct = current_kimp - entry_kimp
        
        # Track A: 정상 익절 (우선 체크)
        if profit_pct >= self.TARGET_PROFIT_PCT:
            return ExitSignal(
                reason=ExitReason.TARGET,
                current_kimp=current_kimp,
                entry_kimp=entry_kimp,
                profit_pct=profit_pct,
                bb_upper=None
            )
        
        # Track B: Breakout 탈출
        if profit_pct >= self.BREAKOUT_MIN_PCT:
            bb_upper = await self._get_bb_upper()
            
            if current_kimp > bb_upper:
                return ExitSignal(
                    reason=ExitReason.BREAKOUT,
                    current_kimp=current_kimp,
                    entry_kimp=entry_kimp,
                    profit_pct=profit_pct,
                    bb_upper=bb_upper
                )
        
        return None
    
    async def _get_bb_upper(self) -> float:
        """볼린저 밴드 상단 계산"""
        kimp_series = await self.data_feed.get_kimp_series(self.BB_PERIOD)
        
        mean = sum(kimp_series) / len(kimp_series)
        variance = sum((x - mean) ** 2 for x in kimp_series) / len(kimp_series)
        std = variance ** 0.5
        
        return mean + self.BB_STD_MULT * std
```

### 3.3 청산 실행 코드

```python
class ExitExecutor:
    """청산 실행기"""
    
    def __init__(self, upbit_client, binance_client, db):
        self.upbit = upbit_client
        self.binance = binance_client
        self.db = db
    
    async def execute_exit(self, position, signal: ExitSignal) -> ExitResult:
        """청산 실행"""
        
        try:
            # 동시 청산 실행
            upbit_result, binance_result = await asyncio.gather(
                self._close_upbit_position(position),
                self._close_binance_position(position),
                return_exceptions=True
            )
            
            if isinstance(upbit_result, Exception) or isinstance(binance_result, Exception):
                # 부분 실패 처리
                await self._handle_partial_failure(position, upbit_result, binance_result)
                return ExitResult(
                    success=False,
                    exit_reason=signal.reason,
                    realized_pnl=0,
                    realized_pnl_pct=0,
                    error=f"Partial failure: {upbit_result}, {binance_result}"
                )
            
            # 손익 계산
            realized_pnl = self._calculate_pnl(position, upbit_result, binance_result)
            realized_pnl_pct = (realized_pnl / position.total_invested) * 100
            
            # DB 업데이트
            await self._update_position_closed(
                position=position,
                exit_reason=signal.reason.value,  # 'Target' or 'Breakout'
                exit_kimp=signal.current_kimp,
                exit_bb_upper=signal.bb_upper,
                realized_pnl=realized_pnl,
                realized_pnl_pct=realized_pnl_pct
            )
            
            return ExitResult(
                success=True,
                exit_reason=signal.reason,
                realized_pnl=realized_pnl,
                realized_pnl_pct=realized_pnl_pct,
                error=None
            )
            
        except Exception as e:
            return ExitResult(
                success=False,
                exit_reason=signal.reason,
                realized_pnl=0,
                realized_pnl_pct=0,
                error=str(e)
            )
    
    async def _close_upbit_position(self, position):
        """업비트 현물 매도"""
        return await self.upbit.create_market_sell_order(
            symbol='BTC/KRW',
            amount=position.upbit_amount
        )
    
    async def _close_binance_position(self, position):
        """바이낸스 선물 숏 청산"""
        return await self.binance.create_market_buy_order(
            symbol='BTC/USDT:USDT',
            amount=position.binance_amount,
            params={'reduceOnly': True}
        )
    
    async def _update_position_closed(
        self, 
        position, 
        exit_reason: str,
        exit_kimp: float,
        exit_bb_upper: Optional[float],
        realized_pnl: float,
        realized_pnl_pct: float
    ):
        """포지션 청산 완료 DB 업데이트"""
        await self.db.execute("""
            UPDATE positions SET
                status = 'closed',
                exit_timestamp = NOW(),
                exit_kimp = $1,
                exit_reason = $2,
                exit_bb_upper = $3,
                realized_pnl = $4,
                realized_pnl_pct = $5,
                updated_at = NOW()
            WHERE id = $6
        """, exit_kimp, exit_reason, exit_bb_upper, 
            realized_pnl, realized_pnl_pct, position.id)
```

---

## 4. 통합 실행 루프

### 4.1 메인 트레이딩 루프

```python
class TradingBot:
    """김프 트레이딩 봇 (Ver 3.0)"""
    
    def __init__(self, config):
        self.config = config
        self.entry_executor = EntryExecutor(...)
        self.exit_monitor = ExitMonitor(...)
        self.signal_detector = SignalDetector(...)
        self.fx_filter = FXFilter(...)
        
        self.current_position = None
        self.running = False
    
    async def run(self):
        """메인 루프"""
        self.running = True
        
        while self.running:
            try:
                if self.current_position is None:
                    # 진입 신호 탐지
                    await self._check_entry()
                else:
                    # 청산 신호 탐지 (1초마다)
                    await self._check_exit()
                
                await asyncio.sleep(1)
                
            except Exception as e:
                await self._handle_error(e)
    
    async def _check_entry(self):
        """진입 체크"""
        signal = await self.signal_detector.detect()
        
        if signal:
            # 환율 필터 상태 로깅
            fx_status = self.fx_filter.check(
                signal.fx_rate, 
                signal.fx_ma_12h
            )
            
            if fx_status.is_blocked:
                print(f"⛔ Entry blocked by FX filter: +{fx_status.surge_pct:.2f}%")
                return
            
            # 진입 실행
            result = await self.entry_executor.execute_entry(signal)
            
            if result.success:
                self.current_position = await self._load_position(result.position_id)
                print(f"✅ Entry: {signal.level.value} | Z: {signal.zscore:.2f}")
    
    async def _check_exit(self):
        """청산 체크"""
        exit_signal = await self.exit_monitor._check_exit_conditions(
            self.current_position
        )
        
        if exit_signal:
            result = await self.exit_monitor.executor.execute_exit(
                self.current_position, 
                exit_signal
            )
            
            if result.success:
                reason_emoji = "🎯" if result.exit_reason == ExitReason.TARGET else "🚀"
                print(f"{reason_emoji} Exit ({result.exit_reason.value}): {result.realized_pnl_pct:.2f}%")
                self.current_position = None
```

---

## 5. 에러 처리

### 5.1 주문 실패 시나리오

| 시나리오 | 처리 방법 |
|:---|:---|
| Upbit만 체결 | Upbit 즉시 반대매매 (손실 최소화) |
| Binance만 체결 | Binance 포지션 청산 |
| 양쪽 모두 실패 | 재시도 (최대 3회) |
| 부분 체결 | 체결된 부분만 롤백 |

### 5.2 네트워크 장애 대응

```python
class RetryHandler:
    """재시도 핸들러"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    async def execute_with_retry(self, func, *args, **kwargs):
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
        
        raise last_error
```

---

## 6. 로깅 및 알림

### 6.1 거래 로그

```python
import logging

# 거래 로거 설정
trade_logger = logging.getLogger('trade')
trade_logger.setLevel(logging.INFO)

# 거래 기록 포맷
def log_entry(signal, result):
    trade_logger.info(
        f"ENTRY | Level: {signal.level.value} | "
        f"Z-Score: {signal.zscore:.2f} | "
        f"Kimp: {signal.kimp:.2f}% | "
        f"FX: {signal.fx_rate:.2f} | "
        f"Success: {result.success}"
    )

def log_exit(signal, result):
    trade_logger.info(
        f"EXIT | Reason: {result.exit_reason.value} | "
        f"PnL: {result.realized_pnl:,.0f}원 ({result.realized_pnl_pct:.2f}%) | "
        f"Kimp: {signal.current_kimp:.2f}% → {signal.entry_kimp:.2f}%"
    )
```

### 6.2 Telegram 알림

```python
async def send_telegram_alert(bot, chat_id, message_type, data):
    """Telegram 알림 전송"""
    
    if message_type == 'entry':
        text = (
            f"📈 *진입 완료*\n"
            f"Level: {data['level']}\n"
            f"Z-Score: {data['zscore']:.2f}\n"
            f"김프: {data['kimp']:.2f}%\n"
            f"환율: {data['fx_rate']:.2f}"
        )
    
    elif message_type == 'exit':
        emoji = "🎯" if data['reason'] == 'Target' else "🚀"
        text = (
            f"{emoji} *청산 완료* ({data['reason']})\n"
            f"수익: {data['pnl']:,.0f}원 ({data['pnl_pct']:.2f}%)\n"
            f"김프: {data['entry_kimp']:.2f}% → {data['exit_kimp']:.2f}%"
        )
    
    elif message_type == 'fx_blocked':
        text = (
            f"⛔ *진입 차단 (환율 급등)*\n"
            f"현재 환율: {data['rate']:.2f}\n"
            f"임계값: {data['threshold']:.2f}\n"
            f"급등률: +{data['surge_pct']:.2f}%"
        )
    
    await bot.send_message(chat_id, text, parse_mode='Markdown')
```

---

## 7. 설정

```yaml
# config/order_config.yaml
execution:
  # 진입
  entry:
    fx_surge_threshold: 1.001  # +0.1%
    order_type: "market"
    max_retries: 3
    retry_delay: 1.0
  
  # 청산 - Dual Track
  exit:
    track_a:
      target_profit_pct: 0.70
    track_b:
      breakout_min_pct: 0.48
      bb_period: 20
      bb_std_mult: 2.0
    
    check_interval: 1  # 초
    order_type: "market"
  
  # 롤백
  rollback:
    enabled: true
    max_retries: 3
```

---

**버전**: 3.0  
**작성일**: 2025-12-14  
**레포**: trading-platform-order
