"""
pages/1_📊_Dashboard.py
Dashboard Interaktif — akan diimplementasi di Phase 2
"""

import streamlit as st

st.set_page_config(page_title="Dashboard | DataBuddy", page_icon="📊", layout="wide")

st.markdown("""
<h2 style="
    background: linear-gradient(135deg, #f97316, #fbbf24);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
">📊 Dashboard Interaktif</h2>
""", unsafe_allow_html=True)

st.info("🔄 **Phase 1 (ETL)** harus selesai dulu sebelum dashboard bisa menampilkan data.")

st.markdown("""
### Yang akan tersedia di Phase 2:
- 📈 **Overview KPI** — Revenue, Orders, Avg Basket Size
- 📅 **Sales Trend** — Chart harian / mingguan / bulanan  
- 🏆 **Top Produk** — Produk terlaris by revenue & quantity
- 🗺️ **Geo Analysis** — Distribusi pembeli per kota/provinsi
- 🔄 **Status Pesanan** — Selesai / Dibatalkan / Retur
- 👥 **Cohort Analysis** — Repeat buyer & retensi pelanggan
""")
