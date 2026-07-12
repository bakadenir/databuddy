"""
ML Context Helper
Memberikan konteks lengkap dari hasil ML dan Dashboard untuk AI Data Analyst
"""

import streamlit as st


def get_ml_summary_context():
    """
    Mengambil summary dari ke-3 hasil ML yang sudah di-run.
    Returns string konteks lengkap atau string kosong jika belum ada data.
    """
    summary_parts = []

    # 1. Bundling Summary
    if st.session_state.get("bundling_result"):
        b_result = st.session_state.bundling_result
        b_metrics = b_result.get("metrics", {})
        b_rules = b_result.get("rules", [])
        if not b_rules.empty:
            top_rule = b_rules.iloc[0]
            summary_parts.append(f"""
📊 **BUNDLING (MARKET BASKET ANALYSIS):**
- Total Rules ditemukan: {b_metrics.get('total_rules', 0)}
- Top Recommendation: Bundling "{top_rule['antecedents']}" + "{top_rule['consequents']}"
- Support: {top_rule['support']:.3f}, Confidence: {top_rule['confidence']*100:.1f}%, Lift: {top_rule['lift']:.2f}
""")

    # 2. Clustering Summary
    if st.session_state.get("clustering_result") is not None and not st.session_state.clustering_result.empty:
        c_df = st.session_state.clustering_result
        vip_count = len(c_df[c_df['Tier_Loyalitas'] == 'Super VIP'])
        loyal_count = len(c_df[c_df['Tier_Loyalitas'] == 'Loyal'])
        total_rev = c_df['Total_Belanja'].sum()
        vip_loyal_rev = c_df[c_df['Tier_Loyalitas'].isin(['Super VIP', 'Loyal'])]['Total_Belanja'].sum()
        persentase = (vip_loyal_rev / total_rev * 100) if total_rev > 0 else 0
        total_customers = len(c_df)
        summary_parts.append(f"""
👥 **CLUSTERING (SEGMENTASI PELANGGAN):**
- Total Pelanggan: {total_customers}
- Super VIP: {vip_count} pelanggan
- Loyal: {loyal_count} pelanggan
- Kontribusi VIP+Loyal ke omzet: {persentase:.1f}% dari total Rp {total_rev:,.0f}
""")

    # 3. Forecasting Summary
    if st.session_state.get("forecast_result"):
        f_result = st.session_state.forecast_result
        f_metrics = f_result.get("metrics", {})
        f_days = st.session_state.forecast_params.get("forecast_days", 30)
        summary_parts.append(f"""
📈 **FORECASTING (PREDIKSI OMZET):**
- Prediksi {f_days} hari ke depan: Rp {f_metrics.get('total_forecast', 0):,.0f}
- Rata-rata harian: Rp {f_metrics.get('avg_daily_forecast', 0):,.0f}
- Error Model (MAPE): {f_metrics.get('mape_percent', 0)}%
- Data historis: {f_metrics.get('data_points', 0)} hari
""")

    if summary_parts:
        return f"""
═══════════════════════════════════════════════════════════════
📋 KONTEKS HASIL MACHINE LEARNING (SUDAH DI-RUN)
═══════════════════════════════════════════════════════════════
Berikut adalah ringkasan dari SEMUA analisis ML yang sudah dijalankan:

{''.join(summary_parts)}
═══════════════════════════════════════════════════════════════
"""
    return ""


def get_dashboard_overview():
    """
    Mengambil overview data dashboard (revenue, orders, dll)
    Returns string konteks dashboard atau string kosong jika belum ada data.
    """
    try:
        from core.data_manager import get_tables, build_master

        tables = get_tables()
        if not tables:
            return ""

        df_master = build_master(tables)
        if df_master is None or df_master.empty:
            return ""

        min_date = df_master["tanggal_pesanan"].min()
        max_date = df_master["tanggal_pesanan"].max()
        total_orders = df_master["order_id"].nunique()
        total_customers = df_master["customer_id"].nunique()
        total_revenue = df_master[df_master["is_completed"] == 1]["valid_item_revenue"].sum()

        return f"""
═══════════════════════════════════════════════════════════════
📊 KONTEKS DASHBOARD (DATA MASTER)
═══════════════════════════════════════════════════════════════
• Periode Data: {min_date.strftime('%d %B %Y')} s.d. {max_date.strftime('%d %B %Y')}
• Total Orders: {total_orders:,}
• Total Customers: {total_customers:,}
• Total Revenue: Rp {total_revenue:,.0f}
═══════════════════════════════════════════════════════════════
"""
    except Exception:
        return ""


def get_full_ai_context():
    """
    Mengambil KONTEKS LENGKAP untuk AI Data Analyst (ML + Dashboard)
    Returns string konteks lengkap
    """
    ml_ctx = get_ml_summary_context()
    dash_ctx = get_dashboard_overview()

    if not ml_ctx and not dash_ctx:
        return ""

    return f"""
{'═══════════════════════════════════════════════════════════════'}
{'🤖 AI DATA ANALYST - KONTEKS LENGKAP'}
{'═══════════════════════════════════════════════════════════════'}

{dash_ctx if dash_ctx else '⚪ Dashboard Data: Belum tersedia'}

{ml_ctx if ml_ctx else '⚪ Hasil ML: Belum ada analisis yang di-run'}

{'═══════════════════════════════════════════════════════════════'}

Gunakan konteks di atas untuk menjawab pertanyaan user dengan akurat.
JANGAN mengarang data di luar yang tersedia di konteks ini.
"""
