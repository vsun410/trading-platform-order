"""
손익 현황 카드 - Neon Daybreak Design

현재 포지션의 손익 정보를 표시합니다.
Neo-brutalist 스타일의 하드 섀도우와 라임 액센트 적용
"""

import streamlit as st

from src.database.supabase_client import SupabaseClient


def get_pnl_data() -> dict:
    """손익 데이터 조회"""
    try:
        db = SupabaseClient()

        # 현재 오픈 포지션 조회
        position_result = (
            db._client.table("positions")
            .select("*")
            .eq("status", "open")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not position_result.data:
            return None

        position = position_result.data[0]

        # 현재 김프율 조회
        kimp_result = (
            db._client.table("kimp_1m")
            .select("kimp_rate")
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )

        current_kimp = kimp_result.data[0]["kimp_rate"] if kimp_result.data else 0
        entry_kimp = position.get("entry_kimp", 0)

        # 김프 차익 계산 (진입 - 현재)
        kimp_profit = entry_kimp - current_kimp

        # 수수료 추정 (업비트 0.05% + 바이낸스 0.04%)
        fee = 0.09

        # 순이익 (김프 차익 - 수수료)
        net_profit = kimp_profit - fee

        return {
            "kimp_profit": kimp_profit,
            "funding_profit": 0,
            "fee": fee,
            "net_profit": net_profit,
            "entry_kimp": entry_kimp,
            "current_kimp": current_kimp,
        }

    except Exception as e:
        return None


def render_pnl_card():
    """손익 현황 카드 렌더링 - Neon Daybreak Style"""

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
        ">PROFIT & LOSS</h2>
    """, unsafe_allow_html=True)

    pnl = get_pnl_data()

    if pnl is None:
        st.markdown("""
            <div style="
                background: #f3f4f6;
                border: 2px dashed #9ca3af;
                padding: 2rem;
                text-align: center;
            ">
                <div style="font-size:2rem;margin-bottom:0.5rem;">💰</div>
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
            st.metric("NET P&L", "N/A")
        with col2:
            st.metric("KIMP DIFF", "N/A")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 순이익 표시
    net_profit = pnl.get("net_profit", 0)
    is_profit = net_profit >= 0

    # P&L 강조 박스
    pnl_color = "#84cc16" if is_profit else "#dc2626"
    pnl_bg = "#000" if is_profit else "#dc2626"
    pnl_text = "#84cc16" if is_profit else "#ffffff"

    st.markdown(f"""
        <div style="
            background: {pnl_bg};
            padding: 1rem;
            border: 2px solid #000;
            box-shadow: 2px 2px 0px rgba(0,0,0,1);
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <div style="
                    font-size: 0.75rem;
                    color: {pnl_text};
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    opacity: 0.8;
                ">NET PROFIT</div>
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 2rem;
                    font-weight: 700;
                    color: {pnl_text};
                ">{'+' if is_profit else ''}{net_profit:.2f}%</div>
            </div>
            <div style="
                font-size: 2.5rem;
            ">{'📈' if is_profit else '📉'}</div>
        </div>
    """, unsafe_allow_html=True)

    # 김프 변동
    entry_kimp = pnl.get("entry_kimp", 0)
    current_kimp = pnl.get("current_kimp", 0)

    st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="
                background: #f3f4f6;
                padding: 0.75rem 1rem;
                border: 1px solid #e5e7eb;
                flex: 1;
            ">
                <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">ENTRY</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.25rem;font-weight:700;">{entry_kimp:.2f}%</div>
            </div>
            <div style="font-size:1.5rem;color:#6b7280;">→</div>
            <div style="
                background: #f3f4f6;
                padding: 0.75rem 1rem;
                border: 1px solid #e5e7eb;
                flex: 1;
            ">
                <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">CURRENT</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1.25rem;font-weight:700;">{current_kimp:.2f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 상세 정보
    st.markdown("<hr style='border:1px solid #e5e7eb;margin:1rem 0;'>", unsafe_allow_html=True)

    detail_col1, detail_col2, detail_col3 = st.columns(3)

    with detail_col1:
        kimp_profit = pnl.get('kimp_profit', 0)
        st.markdown(f"""
            <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">KIMP PROFIT</div>
            <div style="font-family:'JetBrains Mono',monospace;font-weight:600;">{'+' if kimp_profit >= 0 else ''}{kimp_profit:.3f}%</div>
        """, unsafe_allow_html=True)

    with detail_col2:
        funding = pnl.get('funding_profit', 0)
        st.markdown(f"""
            <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">FUNDING</div>
            <div style="font-family:'JetBrains Mono',monospace;font-weight:600;">{'+' if funding >= 0 else ''}{funding:.3f}%</div>
        """, unsafe_allow_html=True)

    with detail_col3:
        fee = pnl.get('fee', 0)
        st.markdown(f"""
            <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">FEE</div>
            <div style="font-family:'JetBrains Mono',monospace;font-weight:600;color:#dc2626;">-{fee:.3f}%</div>
        """, unsafe_allow_html=True)

    # 청산 조건 안내
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    if net_profit > 0:
        st.markdown("""
            <div style="
                background: #84cc16;
                color: #000;
                padding: 0.5rem 1rem;
                border: 2px solid #000;
                font-weight: 700;
                text-transform: uppercase;
                font-size: 0.875rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <span>✓</span> EXIT AVAILABLE (NET > 0)
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="
                background: #fef3c7;
                color: #000;
                padding: 0.5rem 1rem;
                border: 2px solid #000;
                font-weight: 700;
                text-transform: uppercase;
                font-size: 0.875rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <span>⚠</span> EXIT BLOCKED (NET: {net_profit:.2f}%)
            </div>
        """, unsafe_allow_html=True)

    # 카드 컨테이너 종료
    st.markdown("</div>", unsafe_allow_html=True)
