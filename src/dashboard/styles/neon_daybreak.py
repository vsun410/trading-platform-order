"""
Neon Daybreak Design System for KimchiPRO Dashboard

Design Philosophy: Kinetic Minimalism
- High-energy, clean, sharp, daylight cyberpunk
- Hard shadows only (no soft/blurred shadows)
- No rounded corners (> sm)
- Primary accent: Lime 500
"""

NEON_DAYBREAK_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════
   NEON DAYBREAK - KimchiPRO Design System
   ═══════════════════════════════════════════════════════════════ */

/* Import Fonts - Sharp, Modern Sans-Serif */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* CSS Variables - Design Tokens */
:root {
    /* Colors */
    --color-bg-canvas: #f3f4f6;
    --color-bg-surface: #ffffff;
    --color-primary: #84cc16;
    --color-primary-hover: #a3e635;
    --color-primary-dark: #65a30d;
    --color-secondary: #16a34a;
    --color-danger: #dc2626;
    --color-danger-hover: #ef4444;
    --color-success: #22c55e;
    --color-warning: #eab308;
    --color-text-heading: #111827;
    --color-text-body: #374151;
    --color-text-muted: #6b7280;
    --color-border: #e5e7eb;
    --color-border-dark: #000000;

    /* Shadows - Hard Only */
    --shadow-sm: 2px 2px 0px rgba(0,0,0,1);
    --shadow-md: 4px 4px 0px rgba(0,0,0,1);
    --shadow-lg: 6px 6px 0px rgba(0,0,0,0.8);
    --shadow-xl: 8px 8px 0px rgba(0,0,0,0.8);

    /* Typography */
    --font-sans: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
}

/* Base Styles */
.stApp {
    background-color: var(--color-bg-canvas) !important;
    font-family: var(--font-sans) !important;
}

.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ═══════════════════════════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════════════════════════ */

h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: var(--font-sans) !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: var(--color-text-heading) !important;
}

/* Main Title */
h1, .stMarkdown h1 {
    font-size: 2.5rem !important;
    text-transform: uppercase !important;
    border-bottom: 4px solid var(--color-primary) !important;
    padding-bottom: 0.75rem !important;
    margin-bottom: 1.5rem !important;
}

/* Section Headers */
h2, .stMarkdown h2, .stSubheader {
    font-size: 1.25rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    background: var(--color-primary) !important;
    color: #000000 !important;
    padding: 0.5rem 1rem !important;
    margin: 0 0 1rem 0 !important;
    display: inline-block !important;
}

p, span, div {
    font-family: var(--font-sans) !important;
}

/* Monospace for Data */
.stMetric [data-testid="stMetricValue"],
.stDataFrame,
code, pre {
    font-family: var(--font-mono) !important;
}

/* ═══════════════════════════════════════════════════════════════
   CARDS & CONTAINERS
   ═══════════════════════════════════════════════════════════════ */

/* Generic Card Style */
.neon-card {
    background: var(--color-bg-surface);
    border: 2px solid var(--color-border-dark);
    box-shadow: var(--shadow-md);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.15s ease;
}

.neon-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translate(-2px, -2px);
}

/* Streamlit Native Card Override */
[data-testid="stExpander"],
[data-testid="stForm"] {
    background: var(--color-bg-surface) !important;
    border: 2px solid var(--color-border-dark) !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-md) !important;
}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════════ */

/* Primary Button */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background-color: var(--color-primary) !important;
    color: #000000 !important;
    font-family: var(--font-sans) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border: 2px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-md) !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.1s ease !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: var(--color-primary-hover) !important;
    box-shadow: var(--shadow-lg) !important;
    transform: translate(-2px, -2px) !important;
}

.stButton > button[kind="primary"]:active,
.stButton > button[data-testid="baseButton-primary"]:active {
    box-shadow: var(--shadow-sm) !important;
    transform: translate(2px, 2px) !important;
}

/* Secondary Button */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
.stButton > button:not([kind]) {
    background-color: var(--color-bg-surface) !important;
    color: var(--color-text-heading) !important;
    font-family: var(--font-sans) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.025em !important;
    border: 2px solid var(--color-border-dark) !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.1s ease !important;
}

.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    background-color: var(--color-bg-canvas) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translate(-1px, -1px) !important;
}

/* Danger Button (Emergency Stop) */
.danger-btn > button {
    background-color: var(--color-danger) !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
    box-shadow: var(--shadow-md) !important;
}

.danger-btn > button:hover {
    background-color: var(--color-danger-hover) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* Success Button (Resume) */
.success-btn > button {
    background-color: var(--color-success) !important;
    color: #000000 !important;
    border: 2px solid #000000 !important;
    box-shadow: var(--shadow-md) !important;
}

/* ═══════════════════════════════════════════════════════════════
   METRICS
   ═══════════════════════════════════════════════════════════════ */

[data-testid="stMetric"] {
    background: var(--color-bg-surface) !important;
    border: 2px solid var(--color-border-dark) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 1rem !important;
    border-radius: 0 !important;
}

[data-testid="stMetricLabel"] {
    font-family: var(--font-sans) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    color: var(--color-text-muted) !important;
}

[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    font-size: 1.75rem !important;
    color: var(--color-text-heading) !important;
}

[data-testid="stMetricDelta"] {
    font-family: var(--font-mono) !important;
    font-weight: 500 !important;
}

/* ═══════════════════════════════════════════════════════════════
   STATUS BADGES & ALERTS
   ═══════════════════════════════════════════════════════════════ */

/* Success Alert */
.stAlert[data-baseweb="notification"][kind="success"],
div[data-testid="stAlert"]:has([data-testid="stNotificationContentSuccess"]) {
    background-color: var(--color-primary) !important;
    color: #000000 !important;
    border: 2px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Error Alert */
.stAlert[data-baseweb="notification"][kind="error"],
div[data-testid="stAlert"]:has([data-testid="stNotificationContentError"]) {
    background-color: var(--color-danger) !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Warning Alert */
.stAlert[data-baseweb="notification"][kind="warning"],
div[data-testid="stAlert"]:has([data-testid="stNotificationContentWarning"]) {
    background-color: var(--color-warning) !important;
    color: #000000 !important;
    border: 2px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Info Alert */
.stAlert[data-baseweb="notification"][kind="info"],
div[data-testid="stAlert"]:has([data-testid="stNotificationContentInfo"]) {
    background-color: var(--color-bg-surface) !important;
    color: var(--color-text-body) !important;
    border: 2px solid var(--color-border-dark) !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Override default Streamlit alerts */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 0 !important;
    border-width: 2px !important;
    box-shadow: var(--shadow-sm) !important;
}

.stSuccess {
    background-color: var(--color-primary) !important;
    border-color: #000000 !important;
}

.stError {
    background-color: var(--color-danger) !important;
    border-color: #000000 !important;
    color: #ffffff !important;
}

/* ═══════════════════════════════════════════════════════════════
   DATA TABLE
   ═══════════════════════════════════════════════════════════════ */

[data-testid="stDataFrame"] {
    border: 2px solid var(--color-border-dark) !important;
    border-radius: 0 !important;
    box-shadow: var(--shadow-md) !important;
}

[data-testid="stDataFrame"] table {
    font-family: var(--font-mono) !important;
}

[data-testid="stDataFrame"] th {
    background-color: var(--color-text-heading) !important;
    color: var(--color-primary) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border: none !important;
}

[data-testid="stDataFrame"] td {
    border-bottom: 1px solid var(--color-border) !important;
}

[data-testid="stDataFrame"] tr:hover td {
    background-color: rgba(132, 204, 22, 0.1) !important;
}

/* ═══════════════════════════════════════════════════════════════
   CHARTS (Plotly)
   ═══════════════════════════════════════════════════════════════ */

.stPlotlyChart {
    border: 2px solid var(--color-border-dark) !important;
    box-shadow: var(--shadow-md) !important;
    background: var(--color-bg-surface) !important;
}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════════════ */

[data-testid="stSidebar"] {
    background-color: var(--color-text-heading) !important;
    border-right: 4px solid var(--color-primary) !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stButton > button {
    background-color: var(--color-primary) !important;
    color: #000000 !important;
}

[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
    color: #ffffff !important;
}

/* ═══════════════════════════════════════════════════════════════
   DIVIDERS
   ═══════════════════════════════════════════════════════════════ */

hr, .stDivider {
    border: none !important;
    border-top: 2px solid var(--color-border-dark) !important;
    margin: 2rem 0 !important;
}

/* ═══════════════════════════════════════════════════════════════
   INPUT FIELDS
   ═══════════════════════════════════════════════════════════════ */

.stTextInput input,
.stNumberInput input,
.stSelectbox select {
    background-color: var(--color-bg-surface) !important;
    border: 2px solid var(--color-border-dark) !important;
    border-radius: 0 !important;
    font-family: var(--font-mono) !important;
    padding: 0.75rem !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--color-primary) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ═══════════════════════════════════════════════════════════════ */

/* Emergency Panel */
.emergency-panel {
    background: var(--color-bg-surface);
    border: 3px solid var(--color-border-dark);
    box-shadow: var(--shadow-lg);
    padding: 1.5rem;
    position: relative;
}

.emergency-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: repeating-linear-gradient(
        90deg,
        var(--color-warning) 0px,
        var(--color-warning) 20px,
        var(--color-border-dark) 20px,
        var(--color-border-dark) 40px
    );
}

/* Status Indicator */
.status-active {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--color-primary);
    color: #000000;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.5rem 1rem;
    border: 2px solid #000000;
    box-shadow: var(--shadow-sm);
}

.status-stopped {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--color-danger);
    color: #ffffff;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.5rem 1rem;
    border: 2px solid #000000;
    box-shadow: var(--shadow-sm);
    animation: pulse-danger 1s infinite;
}

@keyframes pulse-danger {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.85; }
}

/* Service Status Cards */
.service-card {
    background: var(--color-bg-surface);
    border: 2px solid var(--color-border-dark);
    box-shadow: var(--shadow-sm);
    padding: 1rem;
    text-align: center;
    transition: all 0.15s ease;
}

.service-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.service-card.status-ok {
    border-left: 4px solid var(--color-primary);
}

.service-card.status-error {
    border-left: 4px solid var(--color-danger);
}

.service-card.status-warning {
    border-left: 4px solid var(--color-warning);
}

/* Data Highlight */
.data-highlight {
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 2rem;
    color: var(--color-primary);
    text-shadow: 2px 2px 0 var(--color-border-dark);
}

/* Caption / Muted Text */
.stCaption, small {
    font-family: var(--font-sans) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: var(--color-text-muted) !important;
}

/* ═══════════════════════════════════════════════════════════════
   HEADER BANNER
   ═══════════════════════════════════════════════════════════════ */

.header-banner {
    background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    color: #000000;
    padding: 1rem 2rem;
    margin: -2rem -1rem 2rem -1rem;
    border-bottom: 4px solid #000000;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-logo {
    font-family: var(--font-sans);
    font-weight: 700;
    font-size: 1.5rem;
    letter-spacing: -0.025em;
    text-transform: uppercase;
}

.header-time {
    font-family: var(--font-mono);
    font-size: 0.875rem;
    background: #000000;
    color: var(--color-primary);
    padding: 0.25rem 0.75rem;
}

/* ═══════════════════════════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════════════════════════ */

@keyframes slide-in {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-in {
    animation: slide-in 0.3s ease-out;
}

/* Hover Effects */
.hover-lift {
    transition: all 0.15s ease;
}

.hover-lift:hover {
    transform: translate(-2px, -2px);
    box-shadow: var(--shadow-lg);
}

/* ═══════════════════════════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════════════════════════ */

@media (max-width: 768px) {
    h1, .stMarkdown h1 {
        font-size: 1.75rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
    }

    .neon-card {
        padding: 1rem;
    }
}
</style>
"""


def inject_neon_daybreak_css():
    """Inject Neon Daybreak CSS into Streamlit app"""
    import streamlit as st
    st.markdown(NEON_DAYBREAK_CSS, unsafe_allow_html=True)


# Plotly theme configuration
PLOTLY_THEME = {
    "layout": {
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#ffffff",
        "font": {
            "family": "IBM Plex Sans, -apple-system, sans-serif",
            "color": "#111827",
        },
        "title": {
            "font": {
                "family": "IBM Plex Sans, sans-serif",
                "size": 16,
                "color": "#111827",
            },
            "x": 0,
        },
        "xaxis": {
            "gridcolor": "#e5e7eb",
            "linecolor": "#000000",
            "linewidth": 2,
            "tickfont": {"family": "JetBrains Mono, monospace"},
        },
        "yaxis": {
            "gridcolor": "#e5e7eb",
            "linecolor": "#000000",
            "linewidth": 2,
            "tickfont": {"family": "JetBrains Mono, monospace"},
        },
        "colorway": ["#84cc16", "#16a34a", "#22c55e", "#a3e635"],
    }
}


def apply_plotly_theme(fig):
    """Apply Neon Daybreak theme to Plotly figure"""
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(
            family="IBM Plex Sans, -apple-system, sans-serif",
            color="#111827",
        ),
        xaxis=dict(
            gridcolor="#e5e7eb",
            linecolor="#000000",
            linewidth=2,
            tickfont=dict(family="JetBrains Mono, monospace"),
        ),
        yaxis=dict(
            gridcolor="#e5e7eb",
            linecolor="#000000",
            linewidth=2,
            tickfont=dict(family="JetBrains Mono, monospace"),
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig
