"""
거래 이력 컴포넌트 - Neon Daybreak Design

최근 거래 이력을 테이블로 표시합니다.
Neo-brutalist 스타일의 하드 섀도우와 라임 액센트 적용
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from src.database.supabase_client import SupabaseClient


def get_recent_trades(limit: int = 10) -> list:
    """최근 거래 조회"""
    try:
        db = SupabaseClient()

        result = (
            db._client.table("trades")
            .select("*")
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data if result.data else []

    except Exception:
        return []


def render_trade_history():
    """거래 이력 렌더링 - Neon Daybreak Style"""

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
        ">TRADE HISTORY</h2>
    """, unsafe_allow_html=True)

    trades = get_recent_trades(limit=10)

    if not trades:
        st.markdown("""
            <div style="
                background: #f3f4f6;
                border: 2px dashed #9ca3af;
                padding: 2rem;
                text-align: center;
            ">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📝</div>
                <div style="
                    font-family: 'IBM Plex Sans', sans-serif;
                    font-weight: 600;
                    color: #6b7280;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                ">NO TRADE HISTORY</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 테이블 헤더
    st.markdown("""
        <div style="
            display: grid;
            grid-template-columns: 1fr 1.2fr 1fr 1fr 1.2fr;
            gap: 0;
            background: #000;
            color: #84cc16;
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 700;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 2px solid #000;
        ">
            <div style="padding:0.75rem;border-right:1px solid #333;">TIME</div>
            <div style="padding:0.75rem;border-right:1px solid #333;">EXCHANGE</div>
            <div style="padding:0.75rem;border-right:1px solid #333;">ACTION</div>
            <div style="padding:0.75rem;border-right:1px solid #333;">QTY</div>
            <div style="padding:0.75rem;">PRICE</div>
        </div>
    """, unsafe_allow_html=True)

    # 테이블 바디
    for idx, trade in enumerate(trades):
        bg_color = "#ffffff" if idx % 2 == 0 else "#f9fafb"

        # 시간
        timestamp = trade.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%m-%d %H:%M")
            except Exception:
                time_str = timestamp[:16]
        else:
            time_str = "N/A"

        # 거래소
        exchange = trade.get("exchange", "")
        if exchange == "upbit":
            exchange_display = "UPBIT"
            exchange_icon = "🇰🇷"
        elif exchange == "binance":
            exchange_display = "BINANCE"
            exchange_icon = "🌐"
        else:
            exchange_display = exchange.upper()
            exchange_icon = "📊"

        # 액션
        side = trade.get("side", "")
        if side == "buy":
            action_display = "BUY"
            action_color = "#22c55e"
            action_icon = "▲"
        elif side == "sell":
            action_display = "SELL"
            action_color = "#dc2626"
            action_icon = "▼"
        elif side == "short":
            action_display = "SHORT"
            action_color = "#dc2626"
            action_icon = "▼"
        elif side == "cover":
            action_display = "COVER"
            action_color = "#22c55e"
            action_icon = "▲"
        else:
            action_display = side.upper() if side else "N/A"
            action_color = "#6b7280"
            action_icon = "●"

        # 수량
        quantity = trade.get("quantity", 0)
        try:
            qty_str = f"{float(quantity):.4f}"
        except Exception:
            qty_str = str(quantity)

        # 가격
        price = trade.get("price", 0)
        try:
            if exchange == "upbit":
                price_str = f"₩{float(price):,.0f}"
            else:
                price_str = f"${float(price):,.2f}"
        except Exception:
            price_str = str(price)

        st.markdown(f"""
            <div style="
                display: grid;
                grid-template-columns: 1fr 1.2fr 1fr 1fr 1.2fr;
                gap: 0;
                background: {bg_color};
                border: 1px solid #e5e7eb;
                border-top: none;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
            ">
                <div style="
                    padding: 0.75rem;
                    border-right: 1px solid #e5e7eb;
                    color: #6b7280;
                ">{time_str}</div>
                <div style="
                    padding: 0.75rem;
                    border-right: 1px solid #e5e7eb;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span>{exchange_icon}</span>
                    <span style="font-weight:600;">{exchange_display}</span>
                </div>
                <div style="
                    padding: 0.75rem;
                    border-right: 1px solid #e5e7eb;
                    color: {action_color};
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 0.25rem;
                ">
                    <span>{action_icon}</span>
                    <span>{action_display}</span>
                </div>
                <div style="
                    padding: 0.75rem;
                    border-right: 1px solid #e5e7eb;
                    font-weight: 600;
                ">{qty_str}</div>
                <div style="
                    padding: 0.75rem;
                    font-weight: 600;
                ">{price_str}</div>
            </div>
        """, unsafe_allow_html=True)

    # 푸터
    st.markdown(f"""
        <div style="
            background: #f3f4f6;
            border: 1px solid #e5e7eb;
            border-top: none;
            padding: 0.5rem 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span style="
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.7rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">SHOWING {len(trades)} RECENT TRADES</span>
            <span style="
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.65rem;
                color: #9ca3af;
            ">AUTO-REFRESH: 5s</span>
        </div>
    """, unsafe_allow_html=True)

    # 카드 컨테이너 종료
    st.markdown("</div>", unsafe_allow_html=True)
