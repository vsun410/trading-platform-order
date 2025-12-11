# Trading Platform - Order

완전 자동 주문 실행 시스템

## 🎯 목적

- 전략 신호 수신 → 즉시 주문 실행
- 업비트/바이낸스 API 통합
- 리스크 관리 (포지션 제한, 손절)

## 📊 지원 주문 타입

### 업비트
| 타입 | 설명 |
|:---|:---|
| 시장가 | 즉시 체결 |
| 지정가 | 특정 가격에 대기 |
| 예약 | 조건 충족 시 실행 |

### 바이낸스 (선물)
| 타입 | 설명 |
|:---|:---|
| 시장가 | 즉시 체결 |
| 지정가 | 특정 가격에 대기 |
| Stop-Loss | 손절 주문 |
| Take-Profit | 익절 주문 |
| Trailing Stop | 추적 손절 |

## 🏗️ 프로젝트 구조

```
trading-platform-order/
├── README.md
├── pyproject.toml
├── docs/
│   ├── EXCHANGE_API.md
│   └── RISK_MANAGEMENT.md
├── config/
│   └── .env.example
├── src/
│   ├── exchanges/
│   │   ├── upbit.py
│   │   └── binance.py
│   ├── executor/
│   │   └── order_executor.py
│   └── risk/
│       └── risk_manager.py
└── tests/
```

## 🚀 빠른 시작

```bash
git clone https://github.com/vsun410/trading-platform-order.git
cd trading-platform-order
pip install -e .
cp config/.env.example config/.env
# .env 파일에 API 키 설정
```

## ⚠️ 실행 방식

주문 실행은 **완전 자동**입니다.
- 신호 수신 → 즉시 주문
- 수동 확인 없음

## 🔗 관련 레포

| 레포 | 역할 |
|:---|:---|
| [research](https://github.com/vsun410/trading-platform-research) | 전략 연구 |
| [portfolio](https://github.com/vsun410/trading-platform-portfolio) | 포트폴리오 검증 |
| [storage](https://github.com/vsun410/trading-platform-storage) | 데이터 저장소 |
