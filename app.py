"""
DataBuddy — Entry Point Streamlit
Shopee Data Analytics & Science Assistant
Light & Colorful Theme
"""

import streamlit as st

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="DataBuddy — Shopee Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — Light Colorful Theme ──────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Background ── */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #fafafa 45%, #fdf4ff 100%);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 12px rgba(0,0,0,0.04);
    }
    section[data-testid="stSidebar"] * {
        color: #334155 !important;
    }
    section[data-testid="stSidebar"] a {
        color: #0ea5e9 !important;
        font-weight: 500;
    }

    /* ── Main content area ── */
    .main .block-container {
        padding-top: 2rem;
    }

    /* ── Header transparent ── */
    header[data-testid="stHeader"] {
        background: rgba(255,255,255,0.8);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #e2e8f0;
    }

    /* ── Metric cards ── */
    div[data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] label {
        color: #64748b !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: #0f172a !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 0.75rem !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #e2e8f0 !important;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(14,165,233,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(14,165,233,0.4) !important;
    }

    /* ── Selectbox, multiselect ── */
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stMultiSelect"] > div {
        background: #ffffff;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* ── Progress bar ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #0ea5e9, #6366f1);
    }

    /* ── Section header ── */
    .section-header {
        color: #475569;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 1.5rem 0 0.5rem 0;
    }

    /* ── Card base ── */
    .card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    }

    /* ── Expander ── */
    details {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    /* ── Info / Warning / Error boxes ── */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ───────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h1 style="
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #f97316 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.2rem;
            line-height: 1.2;
        ">📊 DataBuddy</h1>
        <p style="color: #64748b; font-size: 1.1rem; margin-top: 0; font-weight: 400;">
            Shopee Data Analytics & Science Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        border-radius: 14px;
        padding: 0.6rem 1.2rem;
        text-align: center;
        margin-top: 1.2rem;
        box-shadow: 0 4px 14px rgba(14,165,233,0.3);
    ">
        <span style="color: white; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em;">
            v0.2 — Phase 2 ✅
        </span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Status Cards ───────────────────────────────────────────────
st.markdown('<p class="section-header">🚦 Status Fase Pengembangan</p>', unsafe_allow_html=True)

phases = [
    {"icon": "✅", "phase": "Phase 0", "name": "Environment Setup",   "status": "Selesai",  "gradient": "linear-gradient(135deg,#22c55e,#16a34a)", "shadow": "rgba(34,197,94,0.2)"},
    {"icon": "✅", "phase": "Phase 1", "name": "ETL Pipeline",         "status": "Selesai",  "gradient": "linear-gradient(135deg,#0ea5e9,#0284c7)", "shadow": "rgba(14,165,233,0.2)"},
    {"icon": "✅", "phase": "Phase 2", "name": "Dashboard Interaktif", "status": "Selesai",  "gradient": "linear-gradient(135deg,#f97316,#ea580c)", "shadow": "rgba(249,115,22,0.2)"},
    {"icon": "🔲", "phase": "Phase 3", "name": "ML Models",            "status": "Berikutnya","gradient": "linear-gradient(135deg,#a855f7,#7c3aed)", "shadow": "rgba(168,85,247,0.2)"},
    {"icon": "🔲", "phase": "Phase 4", "name": "LLM Chatbox",          "status": "Menunggu", "gradient": "linear-gradient(135deg,#94a3b8,#64748b)", "shadow": "rgba(100,116,139,0.2)"},
]

cols = st.columns(len(phases))
for col, p in zip(cols, phases):
    with col:
        st.markdown(f"""
        <div style="
            background: {p['gradient']};
            border-radius: 16px;
            padding: 1.2rem;
            text-align: center;
            height: 130px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 18px {p['shadow']};
        ">
            <div style="font-size: 1.8rem; margin-bottom: 0.2rem;">{p['icon']}</div>
            <div style="color: rgba(255,255,255,0.8); font-weight: 600; font-size: 0.7rem; letter-spacing:0.08em; text-transform:uppercase;">{p['phase']}</div>
            <div style="color: white; font-weight: 700; font-size: 0.8rem; margin: 0.2rem 0;">{p['name']}</div>
            <div style="color: rgba(255,255,255,0.9); font-size: 0.7rem; font-weight: 500;">{p['status']}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Quick Guide ────────────────────────────────────────────────
st.markdown('<p class="section-header">🗺️ Cara Pakai DataBuddy</p>', unsafe_allow_html=True)

guides = [
    {
        "step": "1️⃣",
        "title": "Upload Data",
        "desc": "Upload file Excel hasil ekspor dari Shopee Seller Center. Sistem otomatis deteksi format & kolom.",
        "color": "#0ea5e9",
        "bg": "linear-gradient(135deg,#eff6ff,#f0f9ff)",
        "border": "#bae6fd",
    },
    {
        "step": "2️⃣",
        "title": "ETL & Transform",
        "desc": "Data dibersihkan, parsing nominal IDR otomatis, dan dipecah jadi 8 tabel dimensi + fakta.",
        "color": "#f97316",
        "bg": "linear-gradient(135deg,#fff7ed,#ffedd5)",
        "border": "#fed7aa",
    },
    {
        "step": "3️⃣",
        "title": "Analisis & Insight",
        "desc": "Dashboard interaktif, model ML clustering, dan chatbox AI untuk tanya-jawab data Shopee kamu.",
        "color": "#a855f7",
        "bg": "linear-gradient(135deg,#faf5ff,#f3e8ff)",
        "border": "#d8b4fe",
    },
]

c1, c2, c3 = st.columns(3)
for col, g in zip([c1, c2, c3], guides):
    with col:
        st.markdown(f"""
        <div style="
            background: {g['bg']};
            border-radius: 16px;
            padding: 1.4rem;
            border: 1px solid {g['border']};
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
            height: 100%;
        ">
            <div style="font-size: 1.5rem; margin-bottom: 0.6rem;">{g['step']}</div>
            <h4 style="color: {g['color']}; margin: 0 0 0.5rem 0; font-weight: 700; font-size: 1rem;">
                {g['title']}
            </h4>
            <p style="color: #64748b; font-size: 0.85rem; margin: 0; line-height: 1.5;">
                {g['desc']}
            </p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Footer ─────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.8rem; padding: 1rem 0;">
    DataBuddy — Shopee Data Analytics Assistant &nbsp;|&nbsp; Built with ❤️ using Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
