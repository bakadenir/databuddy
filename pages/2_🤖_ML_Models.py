"""
pages/2_🤖_ML_Models.py
Machine Learning Models — akan diimplementasi di Phase 3
"""

import streamlit as st

st.set_page_config(page_title="ML Models | DataBuddy", page_icon="🤖", layout="wide")

st.markdown("""
<h2 style="
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
">🤖 Machine Learning Models</h2>
""", unsafe_allow_html=True)

st.info("🔄 Tersedia setelah **Phase 2 (Dashboard)** selesai.")

st.markdown("""
### Model yang akan tersedia di Phase 3:
- 👥 **Customer Segmentation** — RFM Analysis + K-Means Clustering
- 📦 **Product Bundling** — Apriori / FP-Growth Association Rules
- 📉 **Sales Forecasting** — Prediksi penjualan ke depan
""")
