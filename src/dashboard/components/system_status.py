"""
시스템 상태 컴포넌트 - Neon Daybreak Design

각 서비스 연결 상태를 표시합니다.
Neo-brutalist 스타일의 하드 섀도우와 라임 액센트 적용
"""

import streamlit as st
from datetime import datetime, timezone

from src.database.supabase_client import SupabaseClient


def check_service_health() -> dict:
    """서비스 상태 확인"""
    status = {
        "upbit": {"status": "unknown", "latency_ms": None},
        "binance": {"status": "unknown", "latency_ms": None},
        "fx": {"status": "unknown"},
        "db": {"status": "unknown"},
    }

    # DB 연결 확인
    try:
        db = SupabaseClient()
        start = datetime.now()
        db._client.table("kimp_1m").select("timestamp").limit(1).execute()
        latency = (datetime.now() - start).total_seconds() * 1000
        status["db"] = {"status": "ok", "latency_ms": int(latency)}
    except Exception as e:
        status["db"] = {"status": "error", "error": str(e)}

    # 최근 데이터로 서비스 상태 추정
    try:
        db = SupabaseClient()

        result = db._client.table("kimp_1m").select("timestamp, upbit_price, binance_price").order("timestamp", desc=True).limit(1).execute()

        if result.data:
            latest = result.data[0]
            timestamp = datetime.fromisoformat(latest["timestamp"].replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()

            if age < 120:
                if latest.get("upbit_price"):
                    status["upbit"] = {"status": "ok", "latency_ms": int(age * 10)}
                if latest.get("binance_price"):
                    status["binance"] = {"status": "ok", "latency_ms": int(age * 10)}
            else:
                status["upbit"] = {"status": "stale", "age_sec": int(age)}
                status["binance"] = {"status": "stale", "age_sec": int(age)}

        # FX 상태 확인
        fx_result = db._client.table("fx_rates").select("timestamp").order("timestamp", desc=True).limit(1).execute()
        if fx_result.data:
            timestamp = datetime.fromisoformat(fx_result.data[0]["timestamp"].replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()
            if age < 180:
                status["fx"] = {"status": "ok", "age_sec": int(age)}
            else:
                status["fx"] = {"status": "stale", "age_sec": int(age)}

    except Exception:
        pass

    return status


def render_system_status():
    """시스템 상태 렌더링 - Neon Daybreak Style"""

    # 카드 컨테이너 시작
    st.markdown("""
        <div style="
            background: #ffffff;
            border: 2px solid #000000;
            box-shadow: 4px 4px 0px rgba(0,0,0,1);
            padding: 1.5rem;
        ">
    """, unsafe_allow_html=True)

    # 섹션 헤더
    st.markdown("""
        <h2 style="
            background: #84cc16;
            color: #000000;
            padding: 0.5rem 1rem;
            display: inline-block;
            margin: 0 0 1rem 0;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 700;
        ">SYSTEM STATUS</h2>
    """, unsafe_allow_html=True)

    status = check_service_health()

    # 서비스 그리드
    services = [
        ("🇰🇷", "UPBIT", status.get("upbit", {})),
        ("🌐", "BINANCE", status.get("binance", {})),
        ("💱", "FX RATE", status.get("fx", {})),
        ("🗄️", "DATABASE", status.get("db", {})),
    ]

    # 4열 그리드로 표시
    cols = st.columns(4)

    for idx, (icon, name, svc_status) in enumerate(services):
        with cols[idx]:
            svc_state = svc_status.get("status", "unknown")

            # 상태별 색상
            if svc_state == "ok":
                border_color = "#84cc16"
                bg_color = "#f0fdf4"
                status_icon = "●"
                status_text = "ONLINE"
                status_color = "#22c55e"
            elif svc_state == "stale":
                border_color = "#eab308"
                bg_color = "#fefce8"
                status_icon = "●"
                status_text = "DELAYED"
                status_color = "#ca8a04"
            elif svc_state == "error":
                border_color = "#dc2626"
                bg_color = "#fef2f2"
                status_icon = "●"
                status_text = "ERROR"
                status_color = "#dc2626"
            else:
                border_color = "#9ca3af"
                bg_color = "#f3f4f6"
                status_icon = "○"
                status_text = "UNKNOWN"
                status_color = "#6b7280"

            # 추가 정보
            info_text = ""
            if "latency_ms" in svc_status and svc_status["latency_ms"]:
                info_text = f"{svc_status['latency_ms']}ms"
            elif "age_sec" in svc_status:
                info_text = f"{svc_status['age_sec']}s ago"

            st.markdown(f"""
                <div style="
                    background: {bg_color};
                    border: 2px solid #000;
                    border-left: 4px solid {border_color};
                    padding: 0.75rem;
                    text-align: center;
                    transition: all 0.15s ease;
                ">
                    <div style="font-size:1.5rem;margin-bottom:0.25rem;">{icon}</div>
                    <div style="
                        font-family: 'IBM Plex Sans', sans-serif;
                        font-weight: 700;
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                        color: #111827;
                        margin-bottom: 0.25rem;
                    ">{name}</div>
                    <div style="
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 0.25rem;
                        font-size: 0.7rem;
                        color: {status_color};
                        font-weight: 600;
                    ">
                        <span>{status_icon}</span>
                        <span>{status_text}</span>
                    </div>
                    <div style="
                        font-family: 'JetBrains Mono', monospace;
                        font-size: 0.65rem;
                        color: #6b7280;
                        margin-top: 0.25rem;
                    ">{info_text}</div>
                </div>
            """, unsafe_allow_html=True)

    # 카드 컨테이너 종료
    st.markdown("</div>", unsafe_allow_html=True)
