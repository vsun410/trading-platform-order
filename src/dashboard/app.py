"""
KimchiPRO - 김프 차익거래 대시보드

Design System: Neon Daybreak (Kinetic Minimalism)
- High-energy, clean, sharp, daylight cyberpunk
- Hard shadows only, no rounded corners
- Primary accent: Lime 500
"""

import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가 (Streamlit 실행 시 필요)
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from datetime import datetime, timezone
import time

# 페이지 설정 (반드시 첫 번째로 호출)
st.set_page_config(
    page_title="KimchiPRO | 김프 트레이딩",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 스타일 임포트
from src.dashboard.styles.neon_daybreak import inject_neon_daybreak_css

# 컴포넌트 임포트
from src.dashboard.components.emergency_panel import render_emergency_panel
from src.dashboard.components.position_card import render_position_card
from src.dashboard.components.kimp_chart import render_kimp_chart
from src.dashboard.components.pnl_card import render_pnl_card
from src.dashboard.components.system_status import render_system_status
from src.dashboard.components.trade_history import render_trade_history


def render_header():
    """헤더 배너 렌더링"""
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    st.markdown(f"""
        <div class="header-banner">
            <div class="header-logo">⚡ KIMCHI<span style="color:#000;background:#fff;padding:0 0.25rem;margin-left:0.25rem;">PRO</span></div>
            <div class="header-time">{current_time}</div>
        </div>
    """, unsafe_allow_html=True)


def main():
    """메인 대시보드"""

    # Neon Daybreak CSS 주입
    inject_neon_daybreak_css()

    # 헤더 배너
    render_header()

    # 비상 제어 패널 (최상단 - 가장 중요)
    render_emergency_panel()

    # 구분선
    st.markdown("<hr style='border:2px solid #000;margin:2rem 0;'>", unsafe_allow_html=True)

    # 메인 대시보드 (2열 레이아웃)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        # 포지션 현황
        render_position_card()

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

        # 손익 현황
        render_pnl_card()

    with col2:
        # 김프율 차트
        render_kimp_chart()

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

        # 시스템 상태
        render_system_status()

    # 구분선
    st.markdown("<hr style='border:2px solid #000;margin:2rem 0;'>", unsafe_allow_html=True)

    # 거래 이력 (전체 너비)
    render_trade_history()

    # 사이드바 설정
    with st.sidebar:
        st.markdown("""
            <div style="padding:1rem 0;">
                <h2 style="color:#84cc16;font-size:1.25rem;margin:0 0 1rem 0;text-transform:uppercase;letter-spacing:0.1em;">
                    SETTINGS
                </h2>
            </div>
        """, unsafe_allow_html=True)

        auto_refresh = st.checkbox("AUTO REFRESH (10s)", value=True)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

        if st.button("🔄 MANUAL REFRESH", use_container_width=True, type="primary"):
            st.rerun()

        st.markdown("<hr style='border:1px solid #333;margin:2rem 0;'>", unsafe_allow_html=True)

        st.markdown("""
            <div style="font-size:0.75rem;color:#666;text-transform:uppercase;letter-spacing:0.05em;">
                <p>Design: Neon Daybreak</p>
                <p>Version: 1.0.0</p>
            </div>
        """, unsafe_allow_html=True)

    # 자동 새로고침
    if auto_refresh:
        time.sleep(10)
        st.rerun()


if __name__ == "__main__":
    main()
