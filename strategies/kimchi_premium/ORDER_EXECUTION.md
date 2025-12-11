# 📦 김프 전략 주문 실행 명세 (Order Execution)

## 1. 주문 실행 개요

### 1.1 헤지 포지션 구조

```
┌─────────────────────────────────────────────────────┐
│                   헤지 진입 플로우                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│   신호 발생 (Z-Score 회귀)                            │
│        │                                            │
│        ▼                                            │
│   ┌──────────────┐                                  │
│   │ 투입금액 계산 │                                  │
│   └──────────────┘                                  │
│        │                                            │
│        ▼                                            │
│   ┌──────────────────────────────────────────┐   │
│   │          동시 주문 실행 (asyncio)        │   │
│   │                                          │   │
│   │   업비트              바이낸스            │   │
│   │   ┌─────────┐       ┌─────────┐        │   │
│   │   │ BTC 매수 │       │ BTC 숏  │        │   │
│   │   │ (현물)   │       │ (선물)  │        │   │
│   │   └─────────┘       └─────────┘        │   │
│   │                                          │   │
│   └──────────────────────────────────────────┘   │
│        │                                            │
│        ▼                                            │
│   ┌──────────────┐                                  │
│   │ 체결 확인    │                                  │
│   └──────────────┘                                  │
│        │                                            │
│        ▼                                            │
│   성공: DB 기록 → 모니터링 모드                       │
│   실패: 롤백 실행 → 알림 발송                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 1.2 거래소별 주문 상세

| 거래소 | 심볼 | 주문 유형 | 포지션 |
|:---|:---|:---|:---|
| 업비트 | BTC/KRW | 시장가 매수 | 현물 롱 |
| 바이낸스 | BTC/USDT:USDT | 시장가 매도 | 선물 숏 (1x) |

## 2. CCXT 기반 주문 실행

### 2.1 거래소 초기화

```python
import ccxt
import asyncio

class OrderExecutor:
    def __init__(self, api_keys):
        # 업비트 설정
        self.upbit = ccxt.upbit({
            'apiKey': api_keys['upbit']['access_key'],
            'secret': api_keys['upbit']['secret_key'],
            'enableRateLimit': True
        })
        
        # 바이낸스 선물 설정
        self.binance = ccxt.binance({
            'apiKey': api_keys['binance']['api_key'],
            'secret': api_keys['binance']['secret'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # 선물 모드
            }
        })
```

### 2.2 헤지 진입

```python
async def execute_hedge_entry(self, amount, upbit_price, binance_price):
    """
    헤지 포지션 동시 진입
    
    Args:
        amount: 투입 금액 (KRW)
        upbit_price: 업비트 현재가
        binance_price: 바이낸스 현재가
    """
    btc_amount = amount / upbit_price
    
    # 동시 주문 실행
    tasks = [
        self.execute_upbit_buy(btc_amount, upbit_price),
        self.execute_binance_short(btc_amount, binance_price)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 결과 검증
    upbit_order = results[0]
    binance_order = results[1]
    
    # 한쪽만 체결된 경우 롤백
    if isinstance(upbit_order, Exception) or isinstance(binance_order, Exception):
        await self.rollback_orders(upbit_order, binance_order)
        raise Exception("헤지 진입 실패 - 롤백 실행")
    
    return {
        'upbit': upbit_order,
        'binance': binance_order
    }
```

### 2.3 업비트 매수

```python
async def execute_upbit_buy(self, btc_amount, price):
    """업비트 현물 매수"""
    try:
        order = self.upbit.create_market_buy_order(
            symbol='BTC/KRW',
            amount=btc_amount
        )
        
        order_id = order['id']
        filled_order = await self.wait_for_fill(
            'upbit', order_id, timeout=10
        )
        
        return filled_order
    except Exception as e:
        raise Exception(f"업비트 매수 실패: {e}")
```

### 2.4 바이낸스 숏

```python
async def execute_binance_short(self, btc_amount, price):
    """바이낸스 선물 숏"""
    try:
        # 레버리지 설정 (1x - 델타 중립)
        self.binance.fapiPrivate_post_leverage({
            'symbol': 'BTCUSDT',
            'leverage': 1
        })
        
        # 선물 숏 포지션
        order = self.binance.create_market_sell_order(
            symbol='BTC/USDT:USDT',  # Perpetual futures
            amount=btc_amount
        )
        
        order_id = order['id']
        filled_order = await self.wait_for_fill(
            'binance', order_id, timeout=10
        )
        
        return filled_order
    except Exception as e:
        raise Exception(f"바이낸스 숏 실패: {e}")
```

## 3. 체결 대기 및 확인

### 3.1 체결 대기 로직

```python
async def wait_for_fill(self, exchange, order_id, timeout=30):
    """주문 체결 대기"""
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        try:
            if exchange == 'upbit':
                order = self.upbit.fetch_order(order_id, 'BTC/KRW')
            else:
                order = self.binance.fetch_order(order_id, 'BTC/USDT:USDT')
            
            if order['status'] == 'closed':
                return order
            
            await asyncio.sleep(0.5)
        except Exception:
            pass
    
    raise TimeoutError(f"주문 체결 타임아웃: {order_id}")
```

### 3.2 체결 상태 코드

| 상태 | 설명 | 액션 |
|:---|:---|:---|
| `open` | 대기 중 | 계속 대기 |
| `closed` | 체결 완료 | 성공 반환 |
| `canceled` | 취소됨 | 예외 발생 |
| `expired` | 만료됨 | 예외 발생 |

## 4. 롤백 처리

### 4.1 롤백 로직

```python
async def rollback_orders(self, upbit_order, binance_order):
    """실패한 주문 롤백"""
    
    # 업비트만 체결된 경우 - 즉시 매도
    if not isinstance(upbit_order, Exception):
        await self.execute_upbit_sell(
            upbit_order['filled'],
            None  # 시장가
        )
    
    # 바이낸스만 체결된 경우 - 포지션 종료
    if not isinstance(binance_order, Exception):
        await self.execute_binance_close(
            binance_order['filled'],
            None  # 시장가
        )
```

### 4.2 롤백 시나리오

| 시나리오 | 업비트 | 바이낸스 | 액션 |
|:---|:---|:---|:---|
| A | 체결 | 실패 | 업비트 즉시 매도 |
| B | 실패 | 체결 | 바이낸스 포지션 종료 |
| C | 실패 | 실패 | 롤백 불필요 |

## 5. 청산 주문

### 5.1 헤지 청산

```python
async def execute_hedge_exit(self, positions, prices):
    """헤지 포지션 청산"""
    
    total_btc = sum(
        pos['amount'] / pos['entry_price'] 
        for pos in positions
    )
    
    # 동시 청산
    tasks = [
        self.execute_upbit_sell(total_btc, prices['upbit']),
        self.execute_binance_close(total_btc, prices['binance'])
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        'upbit': results[0],
        'binance': results[1]
    }
```

## 6. API 제한 관리

### 6.1 거래소별 레이트 리미트

| 거래소 | 주문 API | 조회 API |
|:---|:---|:---|
| 업비트 | 8회/초 | 10회/초 |
| 바이낸스 | 1200회/분 | 2400회/분 |

### 6.2 쿠터 관리

```python
class RateLimiter:
    def __init__(self):
        self.upbit_quota = 8     # 초당
        self.binance_quota = 20  # 초당 (편의상)
        self.last_reset = time.time()
    
    async def wait_for_quota(self, exchange):
        """API 쿠터 대기"""
        # 구현 상세...
```

## 7. 에러 처리

### 7.1 재시도 로직

```python
async def execute_with_retry(self, func, max_retries=3):
    """재시도 로직"""
    for attempt in range(max_retries):
        try:
            return await func()
        except ccxt.NetworkError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
        except ccxt.ExchangeError as e:
            # 거래소 에러는 재시도 불가
            raise
```

### 7.2 에러 코드 대응

| 에러 | 대응 |
|:---|:---|
| `NetworkError` | 재시도 (3회) |
| `ExchangeNotAvailable` | 긴급 정지 |
| `InsufficientFunds` | 진입 취소 |
| `InvalidOrder` | 로그 기록 |
| `RateLimitExceeded` | 대기 후 재시도 |

---

**작성일**: 2025-12-11  
**버전**: 1.0  
**레포**: trading-platform-order
