# ⚡ Order 세부 기획서

**Repository:** trading-platform-order  
**Version:** 2.0  
**Date:** 2025-12-12  
**Updated:** 성능 최적화, One-leg Failure 복구, Circuit Breaker 추가

> ⚠️ **주의:** 이 시스템은 완전 자동으로 주문을 실행합니다

---

## 1. 개요

### 1.1 목적

research 레포에서 생성된 신호를 받아 **즉시 주문을 실행**하는 완전 자동화 시스템입니다. 수동 확인 없이 신호가 들어오면 바로 거래소 API를 호출합니다.

### 1.2 핵심 책임

- **신호 수신:** research 레포에서 Signal 수신
- **주문 생성:** 신호 → 주문 변환 (거래소별)
- **주문 실행:** 거래소 API 호출 (완전 자동)
- **체결 관리:** 체결 확인, 포지션 업데이트
- **장애 복구:** One-leg Failure 자동 복구
- **청산 조건:** 수익 실현 시에만 청산 (손실 상태 청산 금지)

### 1.3 연관 레포지토리

| 레포 | 관계 | 데이터 흐름 |
|------|------|-------------|
| research | 신호 제공자 | research → Signal → order |
| storage | 데이터 저장소 | order → 주문/체결 → storage |
| portfolio | (간접) 성과 분석 | order → storage → portfolio |

---

## 2. 성능 최적화 (P0)

### 2.1 필수 라이브러리

```txt
# requirements.txt - 성능 최적화 패키지

uvloop==0.19.0         # asyncio 대체 - 2~4x 성능 향상
orjson==3.9.10         # json 대체 - 10~20x JSON 파싱
coincurve==18.0.0      # ECDSA 서명 - 45ms → 0.05ms
aiohttp==3.9.0         # 비동기 HTTP
ccxt==4.2.0            # 거래소 통합 (프로토타이핑)
```

### 2.2 성능 비교

| 영역 | 기본 | 최적화 후 | 개선율 |
|------|------|----------|--------|
| **Event Loop** | asyncio | uvloop | 2~4x |
| **JSON 파싱** | json | orjson | 10~20x |
| **API 서명** | ecdsa | coincurve | 900x |
| **총 주문 지연** | ~150ms | ~30ms | 5x |

### 2.3 적용 코드

```python
# src/main.py

import uvloop

# uvloop 적용 (asyncio 대체)
uvloop.install()

# orjson 적용 (CCXT에서 자동 사용)
import orjson

def fast_json_dumps(obj):
    return orjson.dumps(obj).decode('utf-8')

def fast_json_loads(s):
    return orjson.loads(s)
```

### 2.4 API 서명 최적화 (coincurve)

```python
# src/exchanges/signature.py

from coincurve import PrivateKey
import hashlib
import hmac

class FastSigner:
    """
    coincurve 기반 고속 서명기
    
    ECDSA 서명 속도: ecdsa 45ms → coincurve 0.05ms
    """
    
    def __init__(self, secret_key: str):
        self.secret = secret_key.encode()
    
    def sign_hmac_sha256(self, message: str) -> str:
        """HMAC-SHA256 서명 (업비트/바이낸스 공통)"""
        signature = hmac.new(
            self.secret,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def sign_jwt(self, payload: dict) -> str:
        """JWT 서명 (업비트용)"""
        # 구현
        pass
```

---

## 3. 거래소 API 연동

### 3.1 CCXT vs 직접 API

| 측면 | CCXT | 직접 API |
|------|------|----------|
| **개발 속도** | ✅ 빠름 | 느림 |
| **레이턴시** | 중간 (~50ms 추가) | ✅ 최소 |
| **커스터마이징** | 제한적 | ✅ 완전 제어 |
| **유지보수** | ✅ 자동 업데이트 | 수동 대응 |
| **권장 시기** | MVP, 프로토타이핑 | 최적화 단계 |

### 3.2 어댑터 구조 (점진적 마이그레이션)

```python
# src/exchanges/factory.py

from enum import Enum
from typing import Protocol

class AdapterType(Enum):
    CCXT = "ccxt"           # 프로토타이핑용
    DIRECT = "direct"       # 최적화용

class ExchangeFactory:
    """거래소 어댑터 팩토리"""
    
    @staticmethod
    def create(
        exchange: str, 
        adapter_type: AdapterType = AdapterType.CCXT
    ) -> 'BaseExchange':
        if adapter_type == AdapterType.CCXT:
            if exchange == "upbit":
                return CCXTUpbitAdapter()
            elif exchange == "binance":
                return CCXTBinanceAdapter()
        else:
            if exchange == "upbit":
                return DirectUpbitAdapter()
            elif exchange == "binance":
                return DirectBinanceAdapter()
```

### 3.3 업비트 API 제한 (⚠️ 주의)

| 엔드포인트 | 제한 | 주의사항 |
|------------|------|----------|
| 시세 조회 | **초당 10회** | Origin 헤더 포함 시 10초당 1회로 제한! |
| 거래 API | 초당 30회 | - |
| 주문 생성 | **초당 8회** | 동시 주문 시 주의 |
| 잔고 조회 | 초당 30회 | - |

```python
# ⚠️ 업비트 특수 제한 사항
UPBIT_SPECIAL_LIMITS = {
    # Origin 헤더 포함 시 제한 강화
    "with_origin_header": "10 req / 10 seconds",
    
    # KRW 입금 후 출금 제한
    "krw_deposit_lock": "24시간 동안 동일 금액 암호화폐 출금 불가",
}
```

### 3.4 바이낸스 선물 Rate Limit

| 엔드포인트 | 제한 | 비고 |
|------------|------|------|
| /fapi/v1/order | 10 req/sec | 초당 10건 |
| 전체 API | 1200 req/min | 분당 1200건 |
| 주문 Weight | 1 weight/order | 주문당 1 weight |

---

## 4. One-leg Failure 복구 (P0)

### 4.1 문제 정의

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

### 4.2 복구 전략

```python
# src/executor/one_leg_handler.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import asyncio

class FailureType(Enum):
    UPBIT_ONLY = "upbit_only"       # 업비트만 체결
    BINANCE_ONLY = "binance_only"   # 바이낸스만 체결
    BOTH_FAILED = "both_failed"     # 둘 다 실패

@dataclass
class OneLegResult:
    success: bool
    action_taken: str
    details: dict

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
    
    def __init__(self, upbit_client, binance_client, notifier):
        self.upbit = upbit_client
        self.binance = binance_client
        self.notifier = notifier
    
    async def handle(
        self, 
        upbit_result: Optional['Fill'],
        binance_result: Optional['Fill'],
        original_order: 'KimpOrder'
    ) -> OneLegResult:
        """
        One-leg Failure 처리
        
        Args:
            upbit_result: 업비트 체결 결과 (None이면 실패)
            binance_result: 바이낸스 체결 결과 (None이면 실패)
            original_order: 원본 김프 주문
        """
        failure_type = self._detect_failure(upbit_result, binance_result)
        
        if failure_type == FailureType.BOTH_FAILED:
            # 둘 다 실패 → 재시도만
            return await self._retry_both(original_order)
        
        elif failure_type == FailureType.UPBIT_ONLY:
            # 업비트만 체결 → 바이낸스 재시도 또는 업비트 청산
            return await self._handle_upbit_only(upbit_result, original_order)
        
        elif failure_type == FailureType.BINANCE_ONLY:
            # 바이낸스만 체결 → 업비트 재시도 또는 바이낸스 청산
            return await self._handle_binance_only(binance_result, original_order)
    
    async def _handle_upbit_only(
        self, 
        upbit_fill: 'Fill', 
        order: 'KimpOrder'
    ) -> OneLegResult:
        """
        업비트만 체결된 경우 처리
        
        상황: BTC 현물 보유, 헤지 없음
        위험: BTC 하락 시 손실
        """
        # 1단계: 바이낸스 재시도
        for i, delay in enumerate(self.RETRY_DELAYS):
            await asyncio.sleep(delay)
            
            try:
                binance_result = await self.binance.create_short(
                    symbol="BTCUSDT",
                    quantity=upbit_fill.quantity
                )
                
                if binance_result:
                    await self.notifier.send(
                        "✅ One-leg 복구 성공",
                        f"바이낸스 숏 재시도 성공 (시도 {i+1}회)"
                    )
                    return OneLegResult(
                        success=True,
                        action_taken="retry_success",
                        details={"retry_count": i+1}
                    )
            except Exception as e:
                continue
        
        # 2단계: 재시도 실패 → 긴급 헤지 (업비트 BTC 매도)
        await self.notifier.send(
            "⚠️ One-leg 긴급 헤지",
            "바이낸스 재시도 실패, 업비트 BTC 청산 시도"
        )
        
        try:
            hedge_result = await self.upbit.market_sell(
                symbol="BTC-KRW",
                quantity=upbit_fill.quantity
            )
            
            return OneLegResult(
                success=True,
                action_taken="emergency_hedge",
                details={"hedge_fill": hedge_result}
            )
        except Exception as e:
            # 3단계: 긴급 알림 (수동 개입 필요)
            await self.notifier.send_critical(
                "🚨 One-leg 복구 실패",
                f"수동 개입 필요! 업비트 BTC 보유 중, 헤지 없음. 에러: {e}"
            )
            
            return OneLegResult(
                success=False,
                action_taken="manual_required",
                details={"error": str(e)}
            )
    
    async def _handle_binance_only(
        self, 
        binance_fill: 'Fill', 
        order: 'KimpOrder'
    ) -> OneLegResult:
        """
        바이낸스만 체결된 경우 처리
        
        상황: 숏 포지션만 보유, 현물 없음
        위험: BTC 상승 시 무한 손실 (청산 위험)
        """
        # 1단계: 업비트 재시도
        for i, delay in enumerate(self.RETRY_DELAYS):
            await asyncio.sleep(delay)
            
            try:
                upbit_result = await self.upbit.market_buy(
                    symbol="BTC-KRW",
                    quantity=binance_fill.quantity
                )
                
                if upbit_result:
                    await self.notifier.send(
                        "✅ One-leg 복구 성공",
                        f"업비트 매수 재시도 성공 (시도 {i+1}회)"
                    )
                    return OneLegResult(
                        success=True,
                        action_taken="retry_success",
                        details={"retry_count": i+1}
                    )
            except Exception as e:
                continue
        
        # 2단계: 재시도 실패 → 긴급 헤지 (바이낸스 숏 청산)
        await self.notifier.send(
            "⚠️ One-leg 긴급 헤지",
            "업비트 재시도 실패, 바이낸스 숏 청산 시도"
        )
        
        try:
            hedge_result = await self.binance.close_position("BTCUSDT")
            
            return OneLegResult(
                success=True,
                action_taken="emergency_hedge",
                details={"hedge_fill": hedge_result}
            )
        except Exception as e:
            await self.notifier.send_critical(
                "🚨 One-leg 복구 실패",
                f"수동 개입 필요! 바이낸스 숏만 보유 중. 에러: {e}"
            )
            
            return OneLegResult(
                success=False,
                action_taken="manual_required",
                details={"error": str(e)}
            )
    
    def _detect_failure(
        self, 
        upbit_result: Optional['Fill'],
        binance_result: Optional['Fill']
    ) -> Optional[FailureType]:
        """실패 유형 감지"""
        if not upbit_result and not binance_result:
            return FailureType.BOTH_FAILED
        elif upbit_result and not binance_result:
            return FailureType.UPBIT_ONLY
        elif not upbit_result and binance_result:
            return FailureType.BINANCE_ONLY
        return None  # 둘 다 성공
```

### 4.3 복구 플로우차트

```
┌─────────────────────────────────────────────────────────────────┐
│                  동시 주문 실행                                  │
│         asyncio.gather(upbit, binance)                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │       둘 다 성공?              │
              └───────────────┬───────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │ YES              │                   │ NO
           ▼                  │                   ▼
    ┌─────────────┐          │          ┌───────────────────┐
    │ ✅ 완료     │          │          │  실패 유형 감지    │
    └─────────────┘          │          └─────────┬─────────┘
                             │                    │
                 ┌───────────┴───────────┐       │
                 │                       │       │
        ┌────────▼────────┐    ┌────────▼────────┐
        │ UPBIT_ONLY      │    │ BINANCE_ONLY   │
        │ (업비트만 체결)  │    │ (바이낸스만)   │
        └────────┬────────┘    └────────┬────────┘
                 │                      │
                 ▼                      ▼
        ┌─────────────────┐    ┌─────────────────┐
        │ 바이낸스 재시도  │    │ 업비트 재시도   │
        │ (최대 3회)       │    │ (최대 3회)      │
        └────────┬────────┘    └────────┬────────┘
                 │                      │
         ┌───────┴───────┐      ┌───────┴───────┐
         │ 성공   │ 실패  │      │ 성공   │ 실패  │
         ▼       ▼       │      ▼       ▼       │
        ✅     긴급헤지   │     ✅     긴급헤지  │
               (업비트   │            (바이낸스 │
                매도)    │             청산)   │
                        │                     │
                        ▼                     ▼
              ┌─────────────────────────────────┐
              │  헤지 실패 → 🚨 긴급 알림       │
              │  수동 개입 필요                  │
              └─────────────────────────────────┘
```

---

## 5. Circuit Breaker 패턴 (P1)

### 5.1 개요

연속 실패 시 시스템 보호를 위한 자동 차단 메커니즘입니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Circuit Breaker 상태                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   CLOSED ──(실패 5회)──▶ OPEN ──(30초 후)──▶ HALF_OPEN         │
│      ▲                      │                      │            │
│      │                      │                      │            │
│      │                      ▼                      │            │
│      │              (모든 요청 차단)               │            │
│      │                                             │            │
│      └─────(성공)─────────────────────────────────┘            │
│                             │                                   │
│                             │(실패)                             │
│                             ▼                                   │
│                           OPEN                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 구현

```python
# src/executor/circuit_breaker.py

from enum import Enum
from datetime import datetime, timedelta
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"       # 정상 - 모든 요청 허용
    OPEN = "open"           # 차단 - 모든 요청 거부
    HALF_OPEN = "half_open" # 테스트 - 일부 요청 허용

class CircuitBreaker:
    """
    Circuit Breaker 패턴 구현
    
    설정:
    - 실패 임계값: 5회 연속 실패
    - 복구 대기: 30초
    - Half-Open 테스트: 1회 성공 시 복구
    """
    
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 30  # 초
    
    def __init__(self, name: str):
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: datetime = None
        self.lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """
        Circuit Breaker를 통한 함수 호출
        
        Raises:
            CircuitOpenError: 회로 차단 상태
        """
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitOpenError(
                        f"{self.name} circuit is OPEN. "
                        f"Retry after {self._time_until_reset()}s"
                    )
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self):
        """성공 시 처리"""
        async with self.lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
    
    async def _on_failure(self):
        """실패 시 처리"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.FAILURE_THRESHOLD:
                self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """복구 시도 가능 여부"""
        if not self.last_failure_time:
            return True
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.RECOVERY_TIMEOUT
    
    def _time_until_reset(self) -> int:
        """복구까지 남은 시간"""
        if not self.last_failure_time:
            return 0
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return max(0, int(self.RECOVERY_TIMEOUT - elapsed))


class CircuitOpenError(Exception):
    """Circuit Breaker 차단 에러"""
    pass


# 사용 예시
upbit_circuit = CircuitBreaker("upbit")
binance_circuit = CircuitBreaker("binance")

async def execute_with_protection():
    try:
        upbit_result = await upbit_circuit.call(
            upbit_client.create_order, order
        )
    except CircuitOpenError as e:
        # 회로 차단됨 → 대기 또는 알림
        await notifier.send("⚠️ 업비트 Circuit Breaker 작동", str(e))
```

---

## 6. 주문 실행 파이프라인

### 6.1 실행 흐름 (업데이트)

```
Step 1: 신호 수신
  research → Signal(action=ENTER, symbol=BTC, ...)

Step 2: Circuit Breaker 확인
  IF circuit.is_open: WAIT or ALERT

Step 3: 중복 검사
  IF signal.id in processed_signals: SKIP

Step 4: 자본 배분 확인
  available = total_balance * 0.95  # 예비비 5% 제외

Step 5: 주문 생성
  Order(exchange=upbit, side=BUY, type=MARKET, ...)
  Order(exchange=binance, side=SELL, type=MARKET, ...)

Step 6: 동시 실행 (with Circuit Breaker)
  asyncio.gather(
    upbit_circuit.call(upbit.execute),
    binance_circuit.call(binance.execute)
  )

Step 7: One-leg Failure 확인
  IF one_leg_failure: handle_recovery()

Step 8: 체결 확인 & 저장
  storage.save(fills), discord.notify()
```

### 6.2 김프 차익거래 주문 패턴

| 액션 | 업비트 | 바이낸스 | 주문타입 | 실행 |
|------|--------|----------|----------|------|
| ENTER | BTC 매수 | BTCUSDT 숏 | 시장가 | 동시 |
| EXIT | BTC 매도 | BTCUSDT 청산 | 시장가 | 동시 |

### 6.3 동시 실행 코드 (업데이트)

```python
# src/executor/kimp_executor.py

import asyncio
from typing import Tuple, Optional

class KimpExecutor:
    """김프 차익거래 실행기"""
    
    def __init__(
        self,
        upbit_client: 'UpbitClient',
        binance_client: 'BinanceClient',
        upbit_circuit: CircuitBreaker,
        binance_circuit: CircuitBreaker,
        failure_handler: OneLegFailureHandler
    ):
        self.upbit = upbit_client
        self.binance = binance_client
        self.upbit_circuit = upbit_circuit
        self.binance_circuit = binance_circuit
        self.failure_handler = failure_handler
    
    async def execute_entry(
        self, 
        signal: 'Signal', 
        quantity: float
    ) -> Tuple[Optional['Fill'], Optional['Fill']]:
        """
        김프 진입 실행
        
        업비트: BTC 시장가 매수
        바이낸스: BTCUSDT 숏 진입
        """
        # 동시 실행
        results = await asyncio.gather(
            self._execute_upbit_buy(quantity),
            self._execute_binance_short(quantity),
            return_exceptions=True
        )
        
        upbit_result = results[0] if not isinstance(results[0], Exception) else None
        binance_result = results[1] if not isinstance(results[1], Exception) else None
        
        # One-leg Failure 확인 및 복구
        if not upbit_result or not binance_result:
            recovery = await self.failure_handler.handle(
                upbit_result, binance_result, signal
            )
            
            if not recovery.success:
                raise OneLegFailureError(recovery.details)
        
        return upbit_result, binance_result
    
    async def _execute_upbit_buy(self, quantity: float) -> 'Fill':
        """업비트 매수 (Circuit Breaker 적용)"""
        return await self.upbit_circuit.call(
            self.upbit.market_buy,
            symbol="BTC-KRW",
            quantity=quantity
        )
    
    async def _execute_binance_short(self, quantity: float) -> 'Fill':
        """바이낸스 숏 (Circuit Breaker 적용)"""
        return await self.binance_circuit.call(
            self.binance.create_short,
            symbol="BTCUSDT",
            quantity=quantity
        )
```

---

## 7. 자본 운용 & 청산 전략

> ⚠️ **핵심 원칙:** 김프 차익거래는 현물+선물 헤지 구조로 가격 방향성 리스크가 없습니다.
> 프리미엄 수렴을 기다리면 되므로, **손실 상태에서의 청산은 금지**합니다.

### 7.1 전략 근거

```
┌─────────────────────────────────────────────────────────────────┐
│                    김프 차익거래 구조                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   업비트 현물 매수 (Long)  ←──헤지──→  바이낸스 선물 매도 (Short) │
│                                                                 │
│   • BTC 가격 상승 → 업비트 이익 + 바이낸스 손실 = 상쇄           │
│   • BTC 가격 하락 → 업비트 손실 + 바이낸스 이익 = 상쇄           │
│   • 순수익 = 김프(프리미엄) 축소분 + 펀딩비 수익                 │
│                                                                 │
│   ∴ 가격 방향성 리스크 = 0 (완전 헤지)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 자본 배분 규칙

```python
CAPITAL_ALLOCATION = {
    "trading_ratio": 0.95,    # 총 자본의 95% 투입
    "reserve_ratio": 0.05,    # 예비비 5% (긴급 상황 대비)
}
```

### 7.3 청산 조건 (EXIT 신호)

> 🚫 **절대 금지:** 손실 상태에서의 청산

```python
def should_exit(position: Position, current_kimp: Decimal, fees: Decimal) -> bool:
    """
    청산 조건 판단
    
    핵심 규칙: 차익 - 수수료 > 0 인 경우에만 청산
    """
    profit = position.entry_kimp - current_kimp
    net_profit = profit - fees.total()
    return net_profit > 0
```

---

## 8. 디렉토리 구조 (업데이트)

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
│   └── DETAILED_SPEC.md       # 이 문서
│
├── src/
│   ├── main.py                # uvloop 적용 진입점
│   │
│   ├── exchanges/             # 거래소 어댑터
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── factory.py         # 🆕 어댑터 팩토리
│   │   ├── signature.py       # 🆕 coincurve 서명
│   │   ├── ccxt_upbit.py      # CCXT 어댑터
│   │   ├── ccxt_binance.py
│   │   ├── direct_upbit.py    # 🆕 직접 API (최적화용)
│   │   └── direct_binance.py
│   │
│   ├── executor/
│   │   ├── __init__.py
│   │   ├── kimp_executor.py   # 🆕 김프 실행기
│   │   ├── one_leg_handler.py # 🆕 One-leg 복구
│   │   ├── circuit_breaker.py # 🆕 Circuit Breaker
│   │   └── exit_validator.py
│   │
│   └── capital/
│       ├── __init__.py
│       ├── allocator.py
│       └── fee_calculator.py
│
└── tests/
    ├── test_one_leg_handler.py
    └── test_circuit_breaker.py
```

---

## 9. 구현 로드맵 (업데이트)

| 우선순위 | 작업 | 산출물 | Phase |
|----------|------|--------|-------|
| **P0** | 성능 최적화 | uvloop, orjson, coincurve 적용 | 3 |
| **P0** | One-leg Failure 복구 | OneLegFailureHandler | 3 |
| **P1** | Circuit Breaker | CircuitBreaker 클래스 | 4 |
| **P1** | 직접 API 옵션 | DirectUpbit/BinanceAdapter | 4 |
| P2 | API 키 보안 강화 | HashiCorp Vault 연동 | 5 |

---

## 10. 핵심 설정 요약

```python
# config/settings.py

PERFORMANCE_CONFIG = {
    "use_uvloop": True,
    "use_orjson": True,
    "use_coincurve": True,
}

CAPITAL_CONFIG = {
    "trading_ratio": 0.95,
    "reserve_ratio": 0.05,
}

EXIT_CONFIG = {
    "min_net_profit": 0,
    "include_funding": True,
    "allow_loss_exit": False,  # ❌ 손실 청산 금지
}

ONE_LEG_CONFIG = {
    "max_retries": 3,
    "retry_delays": [1, 2, 4],  # 초
    "emergency_hedge": True,
}

CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,
    "recovery_timeout": 30,  # 초
}
```

---

*— 문서 끝 —*
