# 거래소 API 가이드

## 업비트 API

### 인증
```python
import pyupbit

upbit = pyupbit.Upbit(access_key, secret_key)
```

### 주문
```python
# 시장가 매수
upbit.buy_market_order("KRW-BTC", 100000)  # 10만원어치

# 시장가 매도
upbit.sell_market_order("KRW-BTC", 0.001)  # 0.001 BTC

# 지정가 매수
upbit.buy_limit_order("KRW-BTC", 95000000, 0.001)
```

### API 제한
- 주문: 초당 8회
- 조회: 초당 10회

## 바이낸스 선물 API

### 인증
```python
from binance.client import Client
from binance.um_futures import UMFutures

client = UMFutures(key=api_key, secret=secret_key)
```

### 주문
```python
# 시장가 롱
client.new_order(
    symbol="BTCUSDT",
    side="BUY",
    type="MARKET",
    quantity=0.001
)

# 지정가 숏
client.new_order(
    symbol="BTCUSDT",
    side="SELL",
    type="LIMIT",
    quantity=0.001,
    price=100000,
    timeInForce="GTC"
)

# Stop-Loss
client.new_order(
    symbol="BTCUSDT",
    side="SELL",
    type="STOP_MARKET",
    stopPrice=95000,
    closePosition=True
)
```

### API 제한
- 주문: 분당 1200회
- 웹소켓: 초당 5회 연결

## 환경 변수

```env
# 업비트
UPBIT_ACCESS_KEY=your_access_key
UPBIT_SECRET_KEY=your_secret_key

# 바이낸스
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
```
