"""
DataBuddy — Entry Point Streamlit
Shopee Data Analytics & Science Assistant
"""

import streamlit as st

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="DataBuddy — Shopee Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }

    /* Main background */
    .main {
        background: #0f172a;
    }

    /* Hide default header */
    header[data-testid="stHeader"] {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ───────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <h1 style="
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
    ">📊 DataBuddy</h1>
    <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 0;">
        Shopee Data Analytics & Science Assistant
    </p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f97316, #fbbf24);
        border-radius: 12px;
        padding: 0.5rem 1rem;
        text-align: center;
        margin-top: 1rem;
    ">
        <span style="color: white; font-weight: 600; font-size: 0.85rem;">v0.1 — Phase 0</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Status Cards ───────────────────────────────────────────────
st.subheader("🚦 Status Fase Pengembangan")

phases = [
    {"icon": "✅", "phase": "Phase 0", "name": "Environment Setup",       "status": "Selesai",   "color": "#22c55e"},
    {"icon": "🔄", "phase": "Phase 1", "name": "ETL Pipeline",             "status": "Berikutnya","color": "#f97316"},
    {"icon": "🔲", "phase": "Phase 2", "name": "Dashboard Interaktif",     "status": "Menunggu",  "color": "#64748b"},
    {"icon": "🔲", "phase": "Phase 3", "name": "ML Models",                "status": "Menunggu",  "color": "#64748b"},
    {"icon": "🔲", "phase": "Phase 4", "name": "LLM Chatbox",              "status": "Menunggu",  "color": "#64748b"},
]

cols = st.columns(len(phases))
for col, p in zip(cols, phases):
    with col:
        st.markdown(f"""
        <div style="
            background: #1e293b;
            border: 1px solid #334155;
            border-left: 4px solid {p['color']};
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 1.8rem;">{p['icon']}</div>
            <div style="color: #cbd5e1; font-weight: 600; font-size: 0.8rem;">{p['phase']}</div>
            <div style="color: #f8fafc; font-weight: 500; font-size: 0.75rem; margin: 0.2rem 0;">{p['name']}</div>
            <div style="color: {p['color']}; font-size: 0.7rem; font-weight: 600;">{p['status']}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Quick Guide ────────────────────────────────────────────────
st.subheader("🗺️ Cara Pakai DataBuddy")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div style="background:#1e293b; border-radius:12px; padding:1.2rem; border:1px solid #334155;">
        <h4 style="color:#f97316; margin:0 0 0.5rem 0;">1️⃣  Upload Data</h4>
        <p style="color:#94a3b8; font-size:0.85rem; margin:0;">
            Upload file CSV atau Excel hasil ekspor dari Shopee Seller Center.
            Sistem akan otomatis mendeteksi format & kolom.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div style="background:#1e293b; border-radius:12px; padding:1.2rem; border:1px solid #334155;">
        <h4 style="color:#f97316; margin:0 0 0.5rem 0;">2️⃣  ETL & Simpan</h4>
        <p style="color:#94a3b8; font-size:0.85rem; margin:0;">
            Data dibersihkan, ditransformasi, dan disimpan ke database lokal.
            Siap untuk analisis & visualisasi.
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div style="background:#1e293b; border-radius:12px; padding:1.2rem; border:1px solid #334155;">
        <h4 style="color:#f97316; margin:0 0 0.5rem 0;">3️⃣  Analisis & Insight</h4>
        <p style="color:#94a3b8; font-size:0.85rem; margin:0;">
            Lihat dashboard interaktif, jalankan model ML, dan tanya ke chatbox AI
            dalam Bahasa Indonesia.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Footer ─────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#475569; font-size:0.8rem; padding: 1rem 0;">
    DataBuddy — Shopee Data Analytics Assistant &nbsp;|&nbsp; Phase 0 Setup Complete 🚀
</div>
""", unsafe_allow_html=True)
