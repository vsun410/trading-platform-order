"""
김프율 차트 컴포넌트 - Neon Daybreak Design

김프율 추이를 Plotly 차트로 표시합니다.
Neo-brutalist 스타일의 하드 섀도우와 라임 액센트 적용
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

from src.database.supabase_client import SupabaseClient


def get_kimp_data(hours: int = 1) -> pd.DataFrame:
    """최근 김프 데이터 조회"""
    try:
        db = SupabaseClient()
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        result = (
            db._client.table("kimp_1m")
            .select("timestamp, kimp_rate, upbit_price, binance_price, exchange_rate")
            .gte("timestamp", since.isoformat())
            .order("timestamp", desc=False)
            .execute()
        )

        if result.data:
            return pd.DataFrame(result.data)
        return pd.DataFrame()

    except Exception as e:
        return pd.DataFrame()


def render_kimp_chart():
    """김프율 차트 렌더링 - Neon Daybreak Style"""

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
        ">KIMCHI PREMIUM</h2>
    """, unsafe_allow_html=True)

    df = get_kimp_data(hours=1)

    if df.empty:
        st.markdown("""
            <div style="
                background: #f3f4f6;
                border: 2px dashed #9ca3af;
                padding: 2rem;
                text-align: center;
            ">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📊</div>
                <div style="
                    font-family: 'IBM Plex Sans', sans-serif;
                    font-weight: 600;
                    color: #6b7280;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">NO DATA (LAST 1 HOUR)</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 현재 김프율
    current_kimp = df["kimp_rate"].iloc[-1] if not df.empty else 0

    # 메트릭 표시
    col1, col2, col3 = st.columns(3)

    with col1:
        # 현재 김프 - 강조 표시
        delta_val = None
        if len(df) > 1:
            delta_val = f"{current_kimp - df['kimp_rate'].iloc[-2]:.2f}%"

        # 색상 결정
        kimp_color = "#84cc16" if current_kimp >= 3.0 else "#dc2626" if current_kimp <= 1.0 else "#111827"

        st.markdown(f"""
            <div style="
                background: #000;
                padding: 1rem;
                border: 2px solid #000;
            ">
                <div style="
                    font-size: 0.75rem;
                    color: #84cc16;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    margin-bottom: 0.25rem;
                ">CURRENT KIMP</div>
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 2rem;
                    font-weight: 700;
                    color: {kimp_color};
                    text-shadow: 2px 2px 0px rgba(0,0,0,0.3);
                ">{current_kimp:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if "upbit_price" in df.columns and not df["upbit_price"].isna().all():
            upbit_price = df["upbit_price"].iloc[-1]
            st.metric("🇰🇷 UPBIT BTC", f"₩{upbit_price:,.0f}")

    with col3:
        if "binance_price" in df.columns and not df["binance_price"].isna().all():
            binance_price = df["binance_price"].iloc[-1]
            st.metric("🌐 BINANCE BTC", f"${binance_price:,.2f}")

    # 차트
    try:
        import plotly.express as px
        import plotly.graph_objects as go

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig = go.Figure()

        # 메인 라인
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["kimp_rate"],
            mode='lines',
            name='Kimp Rate',
            line=dict(color='#84cc16', width=3),
            fill='tozeroy',
            fillcolor='rgba(132, 204, 22, 0.1)',
        ))

        # 진입 기준선 (3%)
        fig.add_hline(
            y=3.0,
            line_dash="dash",
            line_color="#22c55e",
            line_width=2,
            annotation_text="ENTRY 3%",
            annotation_position="right",
            annotation_font=dict(size=10, color="#22c55e", family="IBM Plex Sans"),
        )

        # 청산 기준선 (1%)
        fig.add_hline(
            y=1.0,
            line_dash="dash",
            line_color="#dc2626",
            line_width=2,
            annotation_text="EXIT 1%",
            annotation_position="right",
            annotation_font=dict(size=10, color="#dc2626", family="IBM Plex Sans"),
        )

        # 레이아웃 - Neon Daybreak 스타일
        fig.update_layout(
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            font=dict(
                family="IBM Plex Sans, -apple-system, sans-serif",
                color="#111827",
            ),
            xaxis=dict(
                gridcolor='#e5e7eb',
                linecolor='#000000',
                linewidth=2,
                tickfont=dict(family="JetBrains Mono, monospace", size=10),
                title=None,
            ),
            yaxis=dict(
                gridcolor='#e5e7eb',
                linecolor='#000000',
                linewidth=2,
                tickfont=dict(family="JetBrains Mono, monospace", size=10),
                title=dict(text="KIMP %", font=dict(size=10)),
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            height=250,
            showlegend=False,
            hovermode='x unified',
        )

        # 차트 컨테이너에 border 추가
        st.markdown("""
            <div style="border: 2px solid #000; box-shadow: 2px 2px 0px rgba(0,0,0,1);">
        """, unsafe_allow_html=True)

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("</div>", unsafe_allow_html=True)

    except ImportError:
        # Plotly 없으면 기본 차트
        st.line_chart(df.set_index("timestamp")["kimp_rate"])

    # 카드 컨테이너 종료
    st.markdown("</div>", unsafe_allow_html=True)
