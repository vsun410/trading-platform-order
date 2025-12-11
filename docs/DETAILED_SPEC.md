# ⚡ Order 세부 기획서

**Repository:** trading-platform-order  
**Version:** 1.1  
**Date:** 2025-12-11  
**Updated:** 리스크 관리 전략 수정

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
- **청산 조건:** 수익 실현 시에만 청산 (손실 상태 청산 금지)

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

Step 3: 자본 배분 확인
  available = total_balance * 0.95  # 예비비 5% 제외
  IF action == ENTER AND no_position: USE available

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

## 4. 자본 운용 & 청산 전략

> ⚠️ **핵심 원칙:** 김프 차익거래는 현물+선물 헤지 구조로 가격 방향성 리스크가 없습니다.
> 프리미엄 수렴을 기다리면 되므로, **손실 상태에서의 청산은 금지**합니다.

### 4.1 전략 근거

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

**왜 손절하면 안 되는가?**

| 시나리오 | 손절 시 | 홀딩 시 |
|----------|---------|---------|
| 역프 발생 (-2%) | 손실 확정 -2% | 프리미엄 복귀 대기 → 수익 전환 |
| 프리미엄 확대 | 손실 확정 | 더 큰 수익 기회로 전환 |
| 일시적 변동 | 불필요한 손실 | 변동 무시, 수렴 대기 |

### 4.2 자본 배분 규칙

```python
# 자본 배분 설정
CAPITAL_ALLOCATION = {
    "trading_ratio": 0.95,    # 총 자본의 95% 투입
    "reserve_ratio": 0.05,    # 예비비 5% (긴급 상황 대비)
}

def calculate_position_size(total_balance: Decimal) -> Decimal:
    """투입 가능 자본 계산"""
    return total_balance * Decimal("0.95")
```

| 항목 | 비율 | 용도 |
|------|------|------|
| **트레이딩 자본** | 95% | 김프 차익거래 포지션 |
| **예비비** | 5% | 수수료, 마진콜 대비, 긴급 상황 |

### 4.3 청산 조건 (EXIT 신호)

> 🚫 **절대 금지:** 손실 상태에서의 청산

```python
def should_exit(position: Position, current_kimp: Decimal, fees: Decimal) -> bool:
    """
    청산 조건 판단
    
    핵심 규칙: 차익 - 수수료 > 0 인 경우에만 청산
    """
    # 진입 시 김프율
    entry_kimp = position.entry_kimp
    
    # 현재 실현 가능한 차익
    profit = entry_kimp - current_kimp  # 김프 축소분이 이익
    
    # 총 수수료 (진입 + 청산)
    total_fees = fees.entry + fees.exit
    
    # 순이익 계산
    net_profit = profit - total_fees
    
    # ✅ 청산 허용: 순이익 > 0
    # ❌ 청산 금지: 순이익 <= 0
    return net_profit > 0


# 청산 조건 상수
EXIT_CONDITIONS = {
    "min_net_profit": Decimal("0"),      # 최소 순이익 (0 이상이어야 청산)
    "include_funding": True,              # 펀딩비 수익 포함 계산
}
```

### 4.4 청산 판단 플로우

```
┌─────────────────────────────────────────────────────────────┐
│                      EXIT 신호 수신                          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  순이익 계산         │
                    │  = 김프차익 + 펀딩비 │
                    │    - 총수수료        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  순이익 > 0 ?        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │ YES                             │ NO
              ▼                                 ▼
    ┌─────────────────┐               ┌─────────────────┐
    │ ✅ 청산 실행     │               │ ❌ 청산 거부     │
    │ 업비트 매도      │               │ 포지션 유지      │
    │ 바이낸스 청산    │               │ 수렴 대기        │
    └─────────────────┘               └─────────────────┘
```

### 4.5 수수료 계산

```python
@dataclass
class FeeStructure:
    """수수료 구조"""
    # 업비트
    upbit_maker: Decimal = Decimal("0.0005")   # 0.05%
    upbit_taker: Decimal = Decimal("0.0005")   # 0.05%
    
    # 바이낸스 선물
    binance_maker: Decimal = Decimal("0.0002") # 0.02%
    binance_taker: Decimal = Decimal("0.0005") # 0.05%
    
    def total_round_trip(self) -> Decimal:
        """왕복 수수료 (진입 + 청산)"""
        entry = self.upbit_taker + self.binance_taker  # 진입: 시장가
        exit = self.upbit_taker + self.binance_taker   # 청산: 시장가
        return entry + exit  # 약 0.2%

# 예시: 김프 3%에 진입, 1%에 청산 시
# 차익 = 3% - 1% = 2%
# 수수료 = 0.2%
# 순이익 = 2% - 0.2% = 1.8% ✅ 청산 가능
```

---

## 5. 시스템 안전장치

> ⚠️ 참고: 손절/포지션 제한은 의도적으로 제외되었습니다.

### 5.1 주문 실행 안전장치

| 리스크 | 대응 방안 | 구현 |
|--------|-----------|------|
| 중복 주문 | 신호 ID 기반 멱등성 키 | Redis/Set 중복 체크 |
| API 에러 | 지수 백오프 재시도 | 최대 3회, 1s→2s→4s |
| Rate Limit | 요청 큐잉 + 쓰로틀링 | asyncio.Semaphore |
| 네트워크 장애 | 타임아웃 + 자동 재연결 | 10초 타임아웃 |
| 한쪽 체결 실패 | 수동 알림 + 대기 | Discord 긴급 알림 |

### 5.2 포지션 불일치 처리

```python
async def check_position_sync():
    """
    업비트-바이낸스 포지션 동기화 확인
    
    불일치 시: 알림만 발송, 자동 청산하지 않음
    → 수동으로 확인 후 조치
    """
    upbit_btc = await upbit.get_balance("BTC")
    binance_short = await binance.get_position("BTCUSDT")
    
    if abs(upbit_btc - abs(binance_short)) > THRESHOLD:
        await discord.alert(
            level="WARNING",
            message=f"포지션 불일치 감지: Upbit={upbit_btc}, Binance={binance_short}"
        )
        # ❌ 자동 청산하지 않음 - 수동 확인 필요
```

### 5.3 긴급 정지 조건

```python
# 시스템 레벨 긴급 정지만 유지 (손실 기반 정지 제외)
EMERGENCY_STOP_CONDITIONS = [
    "api_error_count > 10",      # 연속 API 에러 10회 이상
    "position_mismatch",         # 포지션 심각한 불일치
    "manual_stop_flag",          # 수동 정지 플래그
    "exchange_maintenance",      # 거래소 점검
]

# ❌ 제외된 조건 (김프 차익거래에 부적합):
# - "daily_loss > X%"           # 손실 기반 정지 제외
# - "position_loss > X%"        # 포지션 손실 정지 제외
# - "kimp_reversal"             # 역프 기반 정지 제외
```

---

## 6. 디렉토리 구조

```
trading-platform-order/
├── README.md
├── pyproject.toml
├── config/
│   └── .env.example          # API 키 템플릿
│
├── docs/
│   ├── EXCHANGE_API.md       # 거래소 API 문서
│   ├── DESIGN_SYSTEM.md      # UI 디자인 가이드
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
│   │   ├── order_executor.py # OrderExecutor
│   │   └── exit_validator.py # 청산 조건 검증
│   │
│   └── capital/              # 자본 관리
│       ├── __init__.py
│       ├── allocator.py      # 자본 배분
│       └── fee_calculator.py # 수수료 계산
│
├── strategies/               # research와 공유
└── tests/
```

---

## 7. 인터페이스 정의

### 7.1 Order 데이터 구조

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

### 7.2 ExitValidator 인터페이스

```python
class ExitValidator:
    """청산 조건 검증기"""
    
    def __init__(self, fee_structure: FeeStructure):
        self.fees = fee_structure
    
    def can_exit(self, position: Position, current_kimp: Decimal) -> ExitDecision:
        """
        청산 가능 여부 판단
        
        Returns:
            ExitDecision: allowed (bool), reason (str), net_profit (Decimal)
        """
        net_profit = self._calculate_net_profit(position, current_kimp)
        
        if net_profit > 0:
            return ExitDecision(
                allowed=True,
                reason="순이익 실현 가능",
                net_profit=net_profit
            )
        else:
            return ExitDecision(
                allowed=False,
                reason=f"순이익 미달 ({net_profit:.2%}), 수렴 대기",
                net_profit=net_profit
            )
```

### 7.3 BaseExchange 인터페이스

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

## 8. 구현 로드맵

| 주차 | 작업 | 산출물 |
|------|------|--------|
| 4주차 | 거래소 API 연동 | UpbitExchange, BinanceExchange 클래스 |
| 5주차 | 주문 실행 파이프라인 | OrderExecutor, 동시 실행 |
| 5주차 | 청산 조건 검증 | ExitValidator, FeeCalculator |
| 5주차 | 자본 배분 | CapitalAllocator (95% 투입) |

---

## 9. 핵심 설정 요약

```python
# config/settings.py

CAPITAL_CONFIG = {
    "trading_ratio": 0.95,        # 95% 투입
    "reserve_ratio": 0.05,        # 5% 예비비
}

EXIT_CONFIG = {
    "min_net_profit": 0,          # 순이익 > 0 이어야 청산
    "include_funding": True,      # 펀딩비 수익 포함
    "allow_loss_exit": False,     # ❌ 손실 청산 금지
}

EMERGENCY_CONFIG = {
    "max_api_errors": 10,         # API 에러 한도
    "position_mismatch_alert": True,
    "loss_based_stop": False,     # ❌ 손실 기반 정지 비활성화
}
```

---

*— 문서 끝 —*
