"""
포지션 현황 카드 - Neon Daybreak Design

업비트/바이낸스 포지션 상태를 표시합니다.
Neo-brutalist 스타일의 하드 섀도우와 라임 액센트 적용
"""

import streamlit as st
from datetime import datetime, timezone

from src.database.supabase_client import SupabaseClient


def get_current_position() -> dict:
    """현재 포지션 조회"""
    try:
        db = SupabaseClient()
        result = (
            db._client.table("positions")
            .select("*")
            .eq("status", "open")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    except Exception as e:
        return None


def render_position_card():
    """포지션 현황 카드 렌더링 - Neon Daybreak Style"""

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
        ">POSITION STATUS</h2>
    """, unsafe_allow_html=True)

    position = get_current_position()

    if position is None:
        # 포지션 없음
        st.markdown("""
            <div style="
                background: #f3f4f6;
                border: 2px dashed #9ca3af;
                padding: 2rem;
                text-align: center;
            ">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📭</div>
                <div style="
                    font-family: 'IBM Plex Sans', sans-serif;
                    font-weight: 600;
                    color: #6b7280;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">NO OPEN POSITION</div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("UPBIT", "0 BTC")
        with col2:
            st.metric("BINANCE", "0 BTC")

    else:
        # 포지션 있음
        quantity = position.get("quantity", 0)
        entry_kimp = position.get("entry_kimp", 0)
        entry_price_krw = position.get("entry_price_krw", 0)
        entry_price_usd = position.get("entry_price_usd", 0)
        created_at = position.get("created_at", "")

        # 포지션 방향 표시
        st.markdown(f"""
            <div style="
                background: #84cc16;
                color: #000000;
                padding: 0.75rem 1rem;
                border: 2px solid #000;
                box-shadow: 2px 2px 0px rgba(0,0,0,1);
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <span style="font-size:1.25rem;">📈</span>
                <span style="
                    font-family: 'JetBrains Mono', monospace;
                    font-weight: 700;
                    font-size: 1rem;
                ">LONG POSITION | {quantity:.4f} BTC</span>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
                <div style="
                    font-size: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    color: #6b7280;
                    margin-bottom: 0.25rem;
                    font-weight: 600;
                ">🇰🇷 UPBIT (SPOT LONG)</div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #111827;
                ">{quantity:.4f} BTC</div>
            """, unsafe_allow_html=True)

            if entry_price_krw:
                st.markdown(f"""
                    <div style="
                        font-family: 'JetBrains Mono', monospace;
                        font-size: 0.75rem;
                        color: #6b7280;
                    ">Entry: ₩{entry_price_krw:,.0f}</div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
                <div style="
                    font-size: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    color: #6b7280;
                    margin-bottom: 0.25rem;
                    font-weight: 600;
                ">🌐 BINANCE (FUTURES SHORT)</div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #dc2626;
                ">-{quantity:.4f} BTC</div>
            """, unsafe_allow_html=True)

            if entry_price_usd:
                st.markdown(f"""
                    <div style="
                        font-family: 'JetBrains Mono', monospace;
                        font-size: 0.75rem;
                        color: #6b7280;
                    ">Entry: ${entry_price_usd:,.2f}</div>
                """, unsafe_allow_html=True)

        # 추가 정보
        st.markdown("<hr style='border:1px solid #e5e7eb;margin:1rem 0;'>", unsafe_allow_html=True)

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.metric("ENTRY KIMP", f"{entry_kimp:.2f}%")

        with info_col2:
            # 포지션 보유 시간 계산
            if created_at:
                try:
                    entry_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    holding_time = datetime.now(timezone.utc) - entry_time
                    hours = int(holding_time.total_seconds() // 3600)
                    minutes = int((holding_time.total_seconds() % 3600) // 60)
                    st.metric("HOLD TIME", f"{hours}h {minutes}m")
                except Exception:
                    st.metric("HOLD TIME", "N/A")
            else:
                st.metric("HOLD TIME", "N/A")

        with info_col3:
            status_val = position.get("status", "N/A").upper()
            st.metric("STATUS", status_val)

    # 카드 컨테이너 종료
    st.markdown("</div>", unsafe_allow_html=True)
