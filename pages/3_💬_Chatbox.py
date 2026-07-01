"""
pages/3_💬_Chatbox.py
LLM Chatbox — akan diimplementasi di Phase 4
"""

import streamlit as st

st.set_page_config(page_title="AI Chatbox | DataBuddy", page_icon="💬", layout="wide")

st.markdown("""
<h2 style="
    background: linear-gradient(135deg, #06b6d4, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
">💬 AI Data Chatbox</h2>
""", unsafe_allow_html=True)

st.info("🔄 Tersedia setelah **Phase 3 (ML Models)** selesai.")

st.markdown("""
### Yang akan tersedia di Phase 4:
- 🗣️ **Tanya jawab dalam Bahasa Indonesia** tentang data Shopee kamu
- 📊 **Context-aware** — AI memahami dashboard & hasil ML yang aktif
- 🔍 **Analisis on-demand** — "Produk mana yang paling sering di-retur bulan lalu?"
- 💡 **Rekomendasi bisnis** berbasis data aktual
""")
