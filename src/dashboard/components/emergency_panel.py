"""
비상 제어 패널 - Neon Daybreak Design

비상정지/재개 버튼과 현재 상태를 표시합니다.
Neo-brutalist 스타일의 하드 섀도우와 라임 액센트 적용
"""

import asyncio
import streamlit as st

from src.dashboard.services.emergency_stop import get_emergency_stop


def render_emergency_panel():
    """비상 제어 패널 렌더링 - Neon Daybreak Style"""

    emergency = get_emergency_stop()

    # 상태 조회
    try:
        status = asyncio.run(emergency.get_status())
        is_stopped = status.get("active", False)
    except Exception:
        is_stopped = False
        status = {"active": False, "reason": "unknown"}

    # 패널 컨테이너
    st.markdown("""
        <div class="emergency-panel" style="
            background: #ffffff;
            border: 3px solid #000000;
            box-shadow: 6px 6px 0px rgba(0,0,0,0.8);
            padding: 1.5rem;
            margin-bottom: 1rem;
            position: relative;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: repeating-linear-gradient(
                    90deg,
                    #eab308 0px,
                    #eab308 20px,
                    #000000 20px,
                    #000000 40px
                );
            "></div>
    """, unsafe_allow_html=True)

    # 섹션 헤더
    st.markdown("""
        <h2 style="
            background: #000;
            color: #84cc16;
            padding: 0.5rem 1rem;
            display: inline-block;
            margin: 0 0 1rem 0;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 700;
        ">⚡ EMERGENCY CONTROL</h2>
    """, unsafe_allow_html=True)

    # 버튼 및 상태 영역
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        # 비상정지 버튼 (커스텀 스타일)
        st.markdown("""<div class="danger-btn">""", unsafe_allow_html=True)
        if st.button(
            "⬛ EMERGENCY STOP",
            type="primary" if not is_stopped else "secondary",
            disabled=is_stopped,
            use_container_width=True,
            key="emergency_stop_btn"
        ):
            if not is_stopped:
                st.session_state["confirm_stop"] = True
        st.markdown("""</div>""", unsafe_allow_html=True)

    with col2:
        # 재개 버튼
        st.markdown("""<div class="success-btn">""", unsafe_allow_html=True)
        if st.button(
            "▶ RESUME SYSTEM",
            type="primary" if is_stopped else "secondary",
            disabled=not is_stopped,
            use_container_width=True,
            key="resume_btn"
        ):
            if is_stopped:
                asyncio.run(emergency.deactivate())
                st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)

    with col3:
        # 현재 상태 표시
        if is_stopped:
            reason = status.get('reason', 'MANUAL')
            st.markdown(f"""
                <div class="status-stopped" style="
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    background: #dc2626;
                    color: #ffffff;
                    font-weight: 700;
                    text-transform: uppercase;
                    padding: 0.75rem 1.25rem;
                    border: 2px solid #000000;
                    box-shadow: 4px 4px 0px rgba(0,0,0,1);
                    font-family: 'IBM Plex Sans', sans-serif;
                    letter-spacing: 0.05em;
                ">
                    <span style="font-size:1.5rem;">🔴</span>
                    <div>
                        <div style="font-size:1rem;">STOPPED</div>
                        <div style="font-size:0.7rem;opacity:0.9;">REASON: {reason.upper()}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="status-active" style="
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    background: #84cc16;
                    color: #000000;
                    font-weight: 700;
                    text-transform: uppercase;
                    padding: 0.75rem 1.25rem;
                    border: 2px solid #000000;
                    box-shadow: 4px 4px 0px rgba(0,0,0,1);
                    font-family: 'IBM Plex Sans', sans-serif;
                    letter-spacing: 0.05em;
                ">
                    <span style="font-size:1.5rem;">⚡</span>
                    <div>
                        <div style="font-size:1rem;">SYSTEM ACTIVE</div>
                        <div style="font-size:0.7rem;opacity:0.8;">AUTO-TRADING ENABLED</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # 패널 닫기
    st.markdown("</div>", unsafe_allow_html=True)

    # 확인 다이얼로그
    if st.session_state.get("confirm_stop", False):
        st.markdown("""
            <div style="
                background: #fef3c7;
                border: 2px solid #000;
                box-shadow: 4px 4px 0px rgba(0,0,0,1);
                padding: 1rem;
                margin-top: 1rem;
            ">
                <p style="font-weight:700;color:#000;margin:0 0 0.5rem 0;text-transform:uppercase;">
                    ⚠️ CONFIRM EMERGENCY STOP
                </p>
                <p style="font-size:0.875rem;color:#374151;margin:0;">
                    • New entries will be blocked<br>
                    • Existing positions remain open
                </p>
            </div>
        """, unsafe_allow_html=True)

        confirm_col1, confirm_col2 = st.columns(2)

        with confirm_col1:
            if st.button("✓ CONFIRM STOP", type="primary", use_container_width=True, key="confirm_yes"):
                asyncio.run(emergency.activate(reason="dashboard_manual"))
                st.session_state["confirm_stop"] = False
                st.rerun()

        with confirm_col2:
            if st.button("✕ CANCEL", use_container_width=True, key="confirm_no"):
                st.session_state["confirm_stop"] = False
                st.rerun()
