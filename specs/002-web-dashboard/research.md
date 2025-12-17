# Research: Web Dashboard

**Feature**: 002-web-dashboard
**Date**: 2025-12-17
**Status**: Complete

## Research Questions

### 1. Streamlit vs 다른 대시보드 프레임워크

**Question**: Python 기반 대시보드 구현에 최적의 프레임워크는?

**Decision**: Streamlit 1.29+

**Rationale**:
- Python 전용, 기존 kimptrade 코드베이스와 자연스럽게 통합
- 빠른 개발 속도 (UI 코드 최소화)
- 내장 반응형 지원 (모바일 대응)
- 실시간 데이터 갱신 (`st.rerun()`, `st.experimental_rerun()`)
- Plotly 차트 네이티브 지원

**Alternatives Considered**:
- Dash: 더 강력하지만 복잡, 학습 곡선 높음
- Gradio: ML 데모에 최적화, 대시보드용으로는 제한적
- Panel: 유연하지만 Streamlit보다 성숙도 낮음

---

### 2. Cloudflare Tunnel 설정 방식

**Question**: 서버 포트 노출 없이 외부 접근을 제공하는 방법은?

**Decision**: Cloudflare Tunnel (cloudflared) + Zero Trust Access

**Rationale**:
- 서버 방화벽 포트 오픈 불필요 (아웃바운드만 사용)
- 자동 HTTPS 인증서 (Let's Encrypt 설정 불필요)
- Zero Trust Access로 이메일 OTP 인증 제공
- 무료 티어로 충분 (50명까지)

**Implementation**:
```bash
# 1. cloudflared 설치
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

# 2. 터널 생성 및 설정
cloudflared tunnel login
cloudflared tunnel create kimptrade-dashboard
cloudflared tunnel route dns kimptrade-dashboard dashboard.yourdomain.com

# 3. 서비스로 등록
sudo cloudflared service install
```

**Alternatives Considered**:
- Nginx + Let's Encrypt: 포트 노출 필요, 인증 직접 구현 필요
- ngrok: 무료 티어 제한, 커스텀 도메인 유료
- Tailscale Funnel: 좋지만 Cloudflare 도메인 이미 사용 중

---

### 3. 비상정지 상태 저장소

**Question**: 비상정지 상태를 어디에 저장할 것인가?

**Decision**: Supabase `system_status` 테이블

**Rationale**:
- 기존 Supabase 인프라 재사용 (추가 서비스 불필요)
- collector와 dashboard 간 상태 공유 용이
- 영속적 저장 (서버 재시작 후에도 유지)
- 상태 변경 이력 추적 가능

**Schema**:
```sql
CREATE TABLE system_status (
    key VARCHAR(50) PRIMARY KEY,
    value JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 초기 데이터
INSERT INTO system_status (key, value) VALUES
('emergency_stop', '{"active": false}');
```

**Alternatives Considered**:
- Redis: 빠르지만 추가 인프라 필요
- 파일 시스템: 컨테이너 간 공유 어려움
- 환경변수: 런타임 변경 불가

---

### 4. 실시간 데이터 갱신 전략

**Question**: 대시보드 데이터를 어떻게 실시간으로 갱신할 것인가?

**Decision**: Streamlit `st.rerun()` + `time.sleep()` 폴링 (10초 간격)

**Rationale**:
- Streamlit의 표준 패턴
- 구현 간단, 서버 부하 낮음
- 10초 간격은 김프 데이터 수집 주기(1분)보다 충분히 빠름

**Implementation**:
```python
import streamlit as st
import time

# Auto-refresh every 10 seconds
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 10:
    st.session_state.last_refresh = time.time()
    st.rerun()
```

**Alternatives Considered**:
- WebSocket: Streamlit에서 복잡, 과잉 엔지니어링
- Server-Sent Events: Streamlit 지원 제한적
- streamlit-autorefresh: 외부 의존성 추가

---

### 5. 차트 라이브러리

**Question**: 김프율 추이 차트에 어떤 라이브러리를 사용할 것인가?

**Decision**: Plotly

**Rationale**:
- Streamlit 네이티브 지원 (`st.plotly_chart()`)
- 인터랙티브 (줌, 팬, 호버 툴팁)
- 반응형 (모바일 대응)
- 금융 차트 패턴 지원

**Implementation**:
```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['kimp_rate'], name='김프율'))
st.plotly_chart(fig, use_container_width=True)
```

**Alternatives Considered**:
- Altair: 선언적이지만 인터랙티브 제한
- Matplotlib: 정적 이미지, 반응형 아님
- st.line_chart: 기본 기능만 제공

---

### 6. 인증 방식

**Question**: 대시보드 접근 인증을 어떻게 구현할 것인가?

**Decision**: Cloudflare Zero Trust Access (Email OTP)

**Rationale**:
- Streamlit 앱 코드 변경 없이 인증 추가
- 이메일 화이트리스트로 접근 제어
- 세션 만료 자동 관리 (24시간)
- 추가 구현 비용 없음

**Configuration**:
1. Cloudflare Dashboard → Zero Trust → Access → Applications
2. Add application: Self-hosted
3. Policy: Allow emails in whitelist
4. Identity provider: One-time PIN

**Alternatives Considered**:
- Streamlit 내장 인증: 없음 (Community Edition)
- streamlit-authenticator: 별도 사용자 DB 필요
- OAuth 직접 구현: 복잡, 과잉 엔지니어링

---

## Dependencies Summary

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | >=1.29.0 | 웹 대시보드 프레임워크 |
| plotly | >=5.0.0 | 인터랙티브 차트 |
| pandas | >=2.0.0 | 데이터 처리 |
| supabase | >=2.0.0 | DB 클라이언트 (기존) |
| python-telegram-bot | >=20.0 | 알림 발송 (기존) |
| loguru | >=0.7.0 | 로깅 (기존) |

## Infrastructure Summary

| Component | Choice | Notes |
|-----------|--------|-------|
| Web Framework | Streamlit | 단일 파일 앱 |
| Reverse Proxy | Cloudflare Tunnel | 포트 비노출 |
| Authentication | Zero Trust Access | 이메일 OTP |
| State Storage | Supabase | system_status 테이블 |
| Charts | Plotly | 인터랙티브 |
| Container | Docker | Dockerfile.dashboard |

## Open Questions

*(모든 질문 해결됨)*
