# ⚡ Order 세부 기획서

**Repository:** trading-platform-order  
**Version:** 1.0  
**Date:** 2025-12-11

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
- **리스크 관리:** 포지션 제한, 손절, 중복 방지

### 1.3 연관 레포지토리

| 레포 | 관계 | 데이터 흐름 |
|------|------|-------------|
| research | 신호 제공자 | research → Signal → order |
| storage | 데이터 저장소 | order → 주문/체결 → storage |
| portfolio | (간접) 성과 분석 | order → storage → portfolio |

---

## 2. 거래소 API 연동

### 2.1 업비트 (Upbit)

#### 2.1.1 지원 주문 타입

| 타입 | API 파라미터 | 설명 |
|------|--------------|------|
| 시장가 매수 | `ord_type: price` | KRW 금액 지정 |
| 시장가 매도 | `ord_type: market` | 수량 지정 |
| 지정가 | `ord_type: limit` | 가격 + 수량 지정 |

#### 2.1.2 Rate Limit

| 엔드포인트 | 제한 | 비고 |
|------------|------|------|
| /v1/orders (주문) | 8 req/sec | 초당 8건 |
| /v1/ticker (시세) | 30 req/sec | 초당 30건 |
| /v1/accounts (잔고) | 30 req/sec | 초당 30건 |

### 2.2 바이낸스 선물 (Binance Futures)

#### 2.2.1 지원 주문 타입

| 타입 | API 파라미터 | 설명 |
|------|--------------|------|
| 시장가 | `type: MARKET` | 즉시 체결 |
| 지정가 | `type: LIMIT` | 가격 지정 대기 |
| Stop Market | `type: STOP_MARKET` | 손절/익절 시장가 |
| Trailing Stop | `type: TRAILING_STOP` | 추적 손절 |

#### 2.2.2 Rate Limit

| 엔드포인트 | 제한 | 비고 |
|------------|------|------|
| /fapi/v1/order (주문) | 10 req/sec | 초당 10건 |
| 전체 API | 1200 req/min | 분당 1200건 |
| 주문 Weight | 1 weight/order | 주문당 1 weight |

---

## 3. 주문 실행 파이프라인

### 3.1 실행 흐름

```
Step 1: 신호 수신
  research → Signal(action=ENTER, symbol=BTC, ...)

Step 2: 중복 검사
  IF signal.id in processed_signals: SKIP

Step 3: 리스크 검증
  CHECK: 포지션 한도, 일일 손실 한도, 마진 비율

Step 4: 주문 생성
  Order(exchange=upbit, side=BUY, type=MARKET, ...)
  Order(exchange=binance, side=SELL, type=MARKET, ...)

Step 5: 동시 실행
  asyncio.gather(upbit.execute(), binance.execute())

Step 6: 체결 확인 & 저장
  storage.save(fills), discord.notify()
```

### 3.2 김프 차익거래 주문 패턴

김프 진입 시 업비트와 바이낸스에 동시 주문을 실행합니다.

| 액션 | 업비트 | 바이낸스 | 주문타입 | 실행 |
|------|--------|----------|----------|------|
| ENTER | BTC 매수 | BTCUSDT 숏 | 시장가 | 동시 |
| EXIT | BTC 매도 | BTCUSDT 청산 | 시장가 | 동시 |

### 3.3 동시 실행 코드 구조

```python
async def execute_kimp_order(signal: Signal):
    # 주문 생성
    upbit_order = create_upbit_order(signal)
    binance_order = create_binance_order(signal)
    
    # 동시 실행
    results = await asyncio.gather(
        upbit_client.execute(upbit_order),
        binance_client.execute(binance_order),
        return_exceptions=True
    )
    
    # 결과 처리
    handle_results(results)
```

---

## 4. 리스크 관리

### 4.1 주문 안전장치

| 리스크 | 대응 방안 | 구현 |
|--------|-----------|------|
| 중복 주문 | 신호 ID 기반 멱등성 키 | Redis/Set 중복 체크 |
| API 에러 | 지수 백오프 재시도 | 최대 3회, 1s→2s→4s |
| Rate Limit | 요청 큐잉 + 쓰로틀링 | asyncio.Semaphore |
| 네트워크 장애 | 타임아웃 + 자동 재연결 | 10초 타임아웃 |
| 한쪽 체결 실패 | 롤백 또는 수동 알림 | Discord 긴급 알림 |

### 4.2 포지션 제한

- **최대 포지션 크기:** 총 자본의 50%
- **레버리지 제한:** 바이낸스 선물 최대 2배
- **손절 기준:** 포지션당 -5%
- **일일 손실 한도:** 총 자본의 -3%

### 4.3 긴급 정지 조건

```python
EMERGENCY_STOP_CONDITIONS = [
    "daily_loss > 3%",           # 일일 손실 한도 초과
    "api_error_count > 10",      # 연속 API 에러
    "position_mismatch",         # 포지션 불일치
    "manual_stop_flag",          # 수동 정지 플래그
]
```

---

## 5. 디렉토리 구조

```
trading-platform-order/
├── README.md
├── pyproject.toml
├── config/
│   └── .env.example          # API 키 템플릿
│
├── docs/
│   ├── EXCHANGE_API.md       # 거래소 API 문서
│   ├── RISK_MANAGEMENT.md    # 리스크 관리
│   └── DETAILED_SPEC.md      # 세부 기획서 (이 문서)
│
├── src/
│   ├── exchanges/            # 거래소 어댑터
│   │   ├── __init__.py
│   │   ├── base.py           # BaseExchange
│   │   ├── upbit.py          # 업비트 API
│   │   └── binance.py        # 바이낸스 API
│   │
│   ├── executor/             # 주문 실행
│   │   ├── __init__.py
│   │   └── order_executor.py # OrderExecutor
│   │
│   └── risk/                 # 리스크 관리
│       ├── __init__.py
│       └── risk_manager.py   # RiskManager
│
├── strategies/               # research와 공유
└── tests/
```

---

## 6. 인터페이스 정의

### 6.1 Order 데이터 구조

```python
@dataclass
class Order:
    id: str                    # 주문 ID (UUID)
    exchange: str              # upbit | binance
    symbol: str                # BTC-KRW | BTCUSDT
    side: OrderSide            # BUY | SELL
    type: OrderType            # MARKET | LIMIT
    quantity: Decimal          # 수량
    price: Optional[Decimal]   # 가격 (지정가)
    status: OrderStatus        # PENDING | FILLED | CANCELLED
    signal_id: str             # 원본 신호 ID
    created_at: datetime
```

### 6.2 BaseExchange 인터페이스

```python
from abc import ABC, abstractmethod

class BaseExchange(ABC):
    @abstractmethod
    async def execute_order(self, order: Order) -> Fill:
        """주문 실행"""
        pass

    @abstractmethod
    async def get_balance(self) -> Dict[str, Decimal]:
        """잔고 조회"""
        pass

    @abstractmethod
    async def get_position(self, symbol: str) -> Position:
        """포지션 조회"""
        pass
```

---

## 7. 구현 로드맵

| 주차 | 작업 | 산출물 |
|------|------|--------|
| 4주차 | 거래소 API 연동 | UpbitExchange, BinanceExchange 클래스 |
| 5주차 | 주문 실행 파이프라인 | OrderExecutor, 동시 실행 |
| 5주차 | 리스크 관리 | RiskManager, 중복 방지 |

---

*— 문서 끝 —*
