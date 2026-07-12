import streamlit as st
from components.ui import render_navbar, render_sidebar_footer
from core.ml_context import get_ml_summary_context

st.set_page_config(
    page_title="Strategi - DataBuddy",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_navbar()

st.title("🎯 Strategi & Prediksi Bisnis")
st.markdown("Halaman khusus untuk pengolahan Machine Learning tingkat lanjut guna menentukan strategi bisnis.")

# Workaround untuk bug tombol di dalam tombol (nested buttons)
if st.session_state.get("switch_to_chatbox"):
    st.session_state["switch_to_chatbox"] = False
    st.switch_page("pages/3_Chatbox.py")

def trigger_chatbox(ai_ctx):
    st.session_state["ai_ml_context"] = ai_ctx
    st.session_state["switch_to_chatbox"] = True

# Tabs untuk memisahkan ketiga pilar ML
tab1, tab2, tab3 = st.tabs([
    "🛍️ Bundling (Association Rule)", 
    "👥 Clustering Pelanggan", 
    "📈 Forecasting Omzet"
])

with tab1:
    st.subheader("Pilar Barang: Rekomendasi Bundling")
    st.caption("Mencari insight barang apa saja yang sering dibeli bersamaan (Market Basket Analysis) menggunakan algoritma Apriori.")

    # Initialize session state for bundling results
    if "bundling_result" not in st.session_state:
        st.session_state.bundling_result = None
    if "bundling_params" not in st.session_state:
        st.session_state.bundling_params = {}
    if "bundling_just_run" not in st.session_state:
        st.session_state.bundling_just_run = False

    col_supp, col_conf = st.columns(2)
    with col_supp:
        min_supp = st.slider("Batas Kepopuleran (Support)", min_value=0.001, max_value=0.1, value=0.020, step=0.001, format="%.3f", help="Batas minimal seberapa sering kombinasi produk muncul di seluruh transaksi. Semakin kecil, semakin banyak kemungkinan barang langka yang tergali.", key="bundling_supp")
    with col_conf:
        min_conf = st.slider("Kekuatan Hubungan (Confidence)", min_value=0.1, max_value=1.0, value=0.35, step=0.05, format="%.2f", help="Peluang (dalam persentase) barang kedua ikut terbeli jika barang pertama dimasukkan ke keranjang.", key="bundling_conf")

    # Check if parameters changed
    params_changed = (
        st.session_state.bundling_params.get("min_supp") != min_supp or
        st.session_state.bundling_params.get("min_conf") != min_conf
    )

    # Reset button
    if st.session_state.bundling_result is not None and not params_changed:
        if st.button("🔄 Reset Hasil", key="reset_bundling"):
            st.session_state.bundling_result = None
            st.session_state.bundling_params = {}
            st.session_state.bundling_just_run = False
            st.rerun()

    # Auto-run on first visit or when parameters changed
    should_run_bundling = st.button("🚀 Jalankan Analisis Bundling", type="primary", key="run_bundling") or st.session_state.bundling_result is None

    if should_run_bundling:
        with st.spinner("Mengunduh data dan menjalankan model Apriori..."):
            from core.data_manager import get_tables, build_master
            from core.analytics_engine import AnalyticsEngine
            from core.ml_engine import MLEngine
            
            tables = get_tables()
            if not tables:
                st.error("❌ Gagal memuat data dari memori/database.")
                st.stop()
                
            df_master = build_master(tables)
            
            if df_master.empty:
                st.error("❌ Data transaksi kosong. Pastikan Anda sudah mengunggah data di halaman Upload.")
                st.stop()
                
            analytics = AnalyticsEngine(df_master)
            ml = MLEngine(analytics.df_completed) # type: ignore
            result = ml.market_basket_analysis(min_support=min_supp, min_confidence=min_conf)
            
            if "error" in result:
                st.error(f"❌ Gagal: {result['error']}")
            else:
                # Store result in session state
                st.session_state.bundling_result = result
                st.session_state.bundling_params = {"min_supp": min_supp, "min_conf": min_conf}
                st.session_state.bundling_just_run = True
                metrics = result["metrics"]
                rules_df = result["rules"]

                st.markdown("### 📊 Model Performance & Metrics")
                
                # Menampilkan metrik seperti di screenshot
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Support Digunakan", f"{metrics['used_support']:.3f}")
                m2.metric("Rata-rata Confidence", f"{metrics['avg_confidence'] * 100:.1f}%")
                m3.metric("Rata-rata Lift", f"{metrics['avg_lift']:.2f}")
                m4.metric("Total Aturan (Rules)", f"{metrics['total_rules']}")
                
                m5, m6, m7, m8 = st.columns(4)
                m5.metric("Total Transaksi Valid", f"{metrics['total_transactions']:,}")
                m6.metric("Transaksi ≥2 Item", f"{metrics['analyzed_transactions']:,}")
                m7.metric("Metode", "Apriori")
                m8.metric("Evaluasi", "Lift > 1")
                
                st.markdown("### 🛍️ Hasil Asosiasi (Association Rules)")
                if not rules_df.empty:
                    # Rename untuk tampilan UI
                    display_df = rules_df.rename(columns={
                        "antecedents": "Jika beli...",
                        "consequents": "...Maka sering beli",
                        "support": "Support",
                        "confidence": "Confidence",
                        "lift": "Lift (Kekuatan Hubungan)"
                    })
                    st.dataframe(display_df, use_container_width=True)
                    st.success("✨ Selesai! Gunakan pasangan produk di atas untuk promo Bundling Anda.")
                    
                    # Generate Summary & Rekomendasi
                    top_rule = rules_df.iloc[0]
                    st.markdown("### 📝 Kesimpulan & Rekomendasi Bisnis")
                    st.info(f"💡 **Rekomendasi Utama:** Buatlah paket *bundling* atau promo diskon untuk pembelian **{top_rule['antecedents']}** yang dipasangkan dengan **{top_rule['consequents']}**.")
                    
                    st.markdown(f"""
                    **📖 Cara Membaca Score (Mengapa direkomendasikan?):**
                    - **Support ({top_rule['support']:.3f}):** Kombinasi kedua produk ini cukup sering terjadi dalam keseluruhan pesanan di toko Anda.
                    - **Confidence ({top_rule['confidence']*100:.1f}%):** Artinya, jika ada pembeli yang berniat membeli `{top_rule['antecedents']}`, ada jaminan/peluang sebesar **{top_rule['confidence']*100:.1f}%** mereka juga pasti akan ikut membeli `{top_rule['consequents']}`.
                    - **Lift ({top_rule['lift']:.2f}):** Nilai *Lift* di atas 1.0 membuktikan bahwa ini **bukanlah sebuah kebetulan**. Pembeli memang secara sadar membeli kedua produk ini bersamaan (kekuatan hubungannya {top_rule['lift']:.2f}x lebih kuat dari pada pembelian acak).
                    """)
                    
                    st.write("")
                    ml_summary = get_ml_summary_context()
                    ai_ctx = f"""
═══════════════════════════════════════════════════════════════
🎯 FOKUS UTAMA: STRATEGI BUNDLING (MARKET BASKET ANALYSIS)
═══════════════════════════════════════════════════════════════

Anda adalah AI Data Analyst. User ingin mendiskusikan STRATEGI BUNDLING.

📊 DATA YANG DIBAHAS SAAT INI:
- Top Bundling Recommendation: "{top_rule['antecedents']}" + "{top_rule['consequents']}"
- Support: {top_rule['support']:.3f} (seberapa sering kombinasi ini muncul)
- Confidence: {top_rule['confidence']*100:.1f}% (peluang barang kedua terbeli jika barang pertama dibeli)
- Lift: {top_rule['lift']:.2f} (kekuatan hubungan, >1 = bukan kebetulan)

🎯 TUGAS ANDA:
Buat strategi pemasaran untuk bundling ini, termasuk:
1. Ide nama promo yang menarik
2. Target market yang tepat
3. Copywriting untuk marketplace/WhatsApp
4. Strategi diskon/promo yang efektif

{ml_summary}
"""
                    st.button("🤖 Diskusikan Strategi Bundling Ini dengan AI Data Analyst", type="secondary", key="btn_ai_bundling", on_click=trigger_chatbox, args=(ai_ctx,))
                else:
                    st.warning("Tidak ada data bundling yang memenuhi batas kriteria.")

    # Display cached results if available (and parameters haven't changed and wasn't just run)
    if st.session_state.bundling_result is not None and not params_changed and not st.session_state.bundling_just_run:
        result = st.session_state.bundling_result
        metrics = result["metrics"]
        rules_df = result["rules"]

        st.markdown("### 📊 Model Performance & Metrics (Cached)")

        # Menampilkan metrik seperti di screenshot
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Support Digunakan", f"{metrics['used_support']:.3f}")
        m2.metric("Rata-rata Confidence", f"{metrics['avg_confidence'] * 100:.1f}%")
        m3.metric("Rata-rata Lift", f"{metrics['avg_lift']:.2f}")
        m4.metric("Total Aturan (Rules)", f"{metrics['total_rules']}")

        m5, m6, m7, m8 = st.columns(4)
        m5.metric("Total Transaksi Valid", f"{metrics['total_transactions']:,}")
        m6.metric("Transaksi ≥2 Item", f"{metrics['analyzed_transactions']:,}")
        m7.metric("Metode", "Apriori")
        m8.metric("Evaluasi", "Lift > 1")

        st.markdown("### 🛍️ Hasil Asosiasi (Association Rules)")
        if not rules_df.empty:
            # Rename untuk tampilan UI
            display_df = rules_df.rename(columns={
                "antecedents": "Jika beli...",
                "consequents": "...Maka sering beli",
                "support": "Support",
                "confidence": "Confidence",
                "lift": "Lift (Kekuatan Hubungan)"
            })
            st.dataframe(display_df, use_container_width=True)
            st.success("✨ Selesai! Gunakan pasangan produk di atas untuk promo Bundling Anda.")

            # Generate Summary & Rekomendasi
            top_rule = rules_df.iloc[0]
            st.markdown("### 📝 Kesimpulan & Rekomendasi Bisnis")
            st.info(f"💡 **Rekomendasi Utama:** Buatlah paket *bundling* atau promo diskon untuk pembelian **{top_rule['antecedents']}** yang dipasangkan dengan **{top_rule['consequents']}**.")

            st.markdown(f"""
            **📖 Cara Membaca Score (Mengapa direkomendasikan?):**
            - **Support ({top_rule['support']:.3f}):** Kombinasi kedua produk ini cukup sering terjadi dalam keseluruhan pesanan di toko Anda.
            - **Confidence ({top_rule['confidence']*100:.1f}%):** Artinya, jika ada pembeli yang berniat membeli `{top_rule['antecedents']}`, ada jaminan/peluang sebesar **{top_rule['confidence']*100:.1f}%** mereka juga pasti akan ikut membeli `{top_rule['consequents']}`.
            - **Lift ({top_rule['lift']:.2f}):** Nilai *Lift* di atas 1.0 membuktikan bahwa ini **bukanlah sebuah kebetulan**. Pembeli memang secara sadar membeli kedua produk ini bersamaan (kekuatan hubungannya {top_rule['lift']:.2f}x lebih kuat dari pada pembelian acak).
            """)

            st.write("")
            ml_summary = get_ml_summary_context()
            ai_ctx = f"""
═══════════════════════════════════════════════════════════════
🎯 FOKUS UTAMA: STRATEGI BUNDLING (MARKET BASKET ANALYSIS)
═══════════════════════════════════════════════════════════════

Anda adalah AI Data Analyst. User ingin mendiskusikan STRATEGI BUNDLING.

📊 DATA YANG DIBAHAS SAAT INI:
- Top Bundling Recommendation: "{top_rule['antecedents']}" + "{top_rule['consequents']}"
- Support: {top_rule['support']:.3f} (seberapa sering kombinasi ini muncul)
- Confidence: {top_rule['confidence']*100:.1f}% (peluang barang kedua terbeli jika barang pertama dibeli)
- Lift: {top_rule['lift']:.2f} (kekuatan hubungan, >1 = bukan kebetulan)

🎯 TUGAS ANDA:
Buat strategi pemasaran untuk bundling ini, termasuk:
1. Ide nama promo yang menarik
2. Target market yang tepat
3. Copywriting untuk marketplace/WhatsApp
4. Strategi diskon/promo yang efektif

{ml_summary}
"""
            st.button("🤖 Diskusikan Strategi Bundling Ini dengan AI Data Analyst", type="secondary", key="btn_ai_bundling_cached", on_click=trigger_chatbox, args=(ai_ctx,))
        else:
            st.warning("Tidak ada data bundling yang memenuhi batas kriteria.")

    # Reset the just-run flag after cached display check
    st.session_state.bundling_just_run = False

with tab2:
    st.subheader("Pilar Pelanggan: Segmentasi (Clustering)")
    st.caption("Membagi pelanggan berdasarkan loyalitas untuk diarahkan ke *direct sales* (WA) guna menghemat potongan admin *marketplace*.")
    st.markdown("---")

    st.info("💡 **Metode:** Sistem Pakar (Rule-Based AI). Menilai pelanggan dari Frekuensi Order dan Total Belanja.")

    # Initialize session state for clustering results
    if "clustering_result" not in st.session_state:
        st.session_state.clustering_result = None

    # Reset button
    if st.session_state.clustering_result is not None:
        if st.button("🔄 Refresh Data Clustering", key="reset_clustering"):
            st.session_state.clustering_result = None
            st.rerun()

    with st.spinner("Memproses seluruh data pelanggan dengan mesin inferensi..."):
        from core.data_manager import get_tables, build_master
        from core.ml_engine import MLEngine
        import plotly.express as px
        import plotly.graph_objects as go
        
        tables = get_tables()
        if not tables:
            st.error("❌ Gagal memuat data. Pastikan Anda sudah mengunggah data di halaman Upload.")
            st.stop()
            
        df_master = build_master(tables)
        ml = MLEngine(df_master)
        
        # Run rule-based segmentation (only if not cached)
        if st.session_state.clustering_result is None:
            df_segment = ml.rfm_segmentation()
            st.session_state.clustering_result = df_segment
        else:
            df_segment = st.session_state.clustering_result

        if df_segment.empty:
            st.warning("Tidak ada data pelanggan yang valid untuk disegmentasi.")
        else:
            st.success(f"✨ Berhasil mengklasifikasikan {len(df_segment)} pelanggan!")
            
            warna_tier = {'Super VIP': '#d1ff33', 'Loyal': '#4db8ff', 'Reguler': '#cccccc', 'Review Manual': '#ff6b6b'}
            
            col1, col2 = st.columns(2)
            
            # 1. Pie Chart Komposisi Pelanggan
            with col1:
                st.markdown("#### Komposisi Pelanggan")
                tier_counts = df_segment['Tier_Loyalitas'].value_counts().reset_index()
                tier_counts.columns = ['Tier_Loyalitas', 'Jumlah']
                fig_pie = px.pie(tier_counts, values='Jumlah', names='Tier_Loyalitas',
                                 color='Tier_Loyalitas', color_discrete_map=warna_tier,
                                 hole=0.4)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Fungsi bantuan untuk format Rupiah singkat (Jt/Rb)
            def format_idr_short(x):
                if x >= 1_000_000:
                    return f"Rp {x/1_000_000:,.1f} Jt"
                elif x >= 1_000:
                    return f"Rp {x/1_000:,.0f} Rb"
                return f"Rp {x:,.0f}"

            # 2. Bar Chart Pendapatan per Tier
            with col2:
                st.markdown("#### Kontribusi Pendapatan")
                revenue_tier = df_segment.groupby('Tier_Loyalitas')['Total_Belanja'].sum().reset_index()
                revenue_tier['Label'] = revenue_tier['Total_Belanja'].apply(format_idr_short)
                fig_bar = px.bar(revenue_tier, x='Tier_Loyalitas', y='Total_Belanja',
                                 color='Tier_Loyalitas', color_discrete_map=warna_tier,
                                 text='Label')
                fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Total (Rp)", margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # 3. Horizontal Bar: Top 10 Pelanggan Sultan
            st.markdown("#### 👑 Top 10 Pelanggan 'Sultan' (Target Direct Order)")
            top_10 = df_segment.head(10).copy()
            cust_col = 'customer_username' if 'customer_username' in top_10.columns else 'customer_id'
            top_10[cust_col] = top_10[cust_col].astype(str)
            top_10['Label'] = top_10['Total_Belanja'].apply(format_idr_short)
            fig_top = px.bar(top_10, x='Total_Belanja', y=cust_col, 
                             color='Tier_Loyalitas', color_discrete_map=warna_tier,
                             orientation='h', text='Label')
            fig_top.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Total Belanja (Rp)", yaxis_title="")
            st.plotly_chart(fig_top, use_container_width=True)
            
            # 4. Tabel Detail
            st.markdown("#### 📋 Tabel Detail Rekomendasi Tindakan")
            st.dataframe(df_segment, use_container_width=True)
            
            st.write("")
            
            # Kalkulasi dinamis persentase pendapatan VIP + Loyal
            total_omzet = df_segment['Total_Belanja'].sum()
            vip_loyal_omzet = df_segment[df_segment['Tier_Loyalitas'].isin(['Super VIP', 'Loyal'])]['Total_Belanja'].sum()
            persentase_sultan = (vip_loyal_omzet / total_omzet) * 100 if total_omzet > 0 else 0
            
            st.info(f"""
            **💡 Insight Bisnis & Aturan Segmentasi:**
            
            **Aturan Klasifikasi (Rule-Base):**
            - 👑 **Super VIP:** Belanja minimal **5x** DAN total **Rp 3.000.000**. *(Target B2B / Agen / Kafe)*
            - 💎 **Loyal:** Belanja minimal **3x** DAN total **Rp 500.000**. *(Konsumen Rutin)*
            - ⚠️ **Review Manual:** Beli 1x tapi langsung tembus **Rp 1.000.000**. *(Sultan Dadakan / Kafe Baru / Cek Fraud COD)*
            - 👤 **Reguler:** Pelanggan eceran standar (1-2x order) di bawah nominal VIP.
            
            **Insight Operasional (Data-Driven):**
            Perhatikan metrik Anda: gabungan dari pelanggan kelas **Super VIP** dan **Loyal** ternyata berhasil menyumbang **{persentase_sultan:.1f}% dari total omzet toko Anda!** 
            Meskipun secara jumlah kepala (kuantitas) mereka adalah kelompok minoritas, secara kualitas merekalah tulang punggung (*cashflow*) utama bisnis Anda. Sangat krusial untuk menjaga hubungan baik dengan mereka. 
            👉 *Saran:* Segera hubungi mereka via WhatsApp secara berkala dengan penawaran *Direct Order* prioritas. Dengan memindahkan transaksi pembeli raksasa ini ke luar *marketplace*, **margin keuntungan Anda akan bertambah jauh lebih besar** karena terbebas dari potongan biaya admin/pajak platform!
            """)
            
            st.write("")
            ml_summary = get_ml_summary_context()
            vip_count = len(df_segment[df_segment['Tier_Loyalitas'] == 'Super VIP'])
            loyal_count = len(df_segment[df_segment['Tier_Loyalitas'] == 'Loyal'])
            vip_rev = df_segment[df_segment['Tier_Loyalitas'] == 'Super VIP']['Total_Belanja'].sum()
            ai_ctx = f"""
═══════════════════════════════════════════════════════════════
👥 FOKUS UTAMA: STRATEGI PELANGGAN VIP (CLUSTERING/SEGMENTASI)
═══════════════════════════════════════════════════════════════

Anda adalah AI Data Analyst. User ingin mendiskusikan STRATEGI PELANGGAN VIP.

📊 DATA YANG DIBAHAS SAAT INI:
- Super VIP: {vip_count} pelanggan (total belanja Rp {vip_rev:,.0f})
- Loyal: {loyal_count} pelanggan
- Total Revenue dari semua pelanggan: Rp {df_segment['Total_Belanja'].sum():,.0f}
- Target: Pindahkan transaksi VIP ke Direct Order (WhatsApp) untuk hemat potongan marketplace

🎯 TUGAS ANDA:
Buat strategi retensi pelanggan VIP, termasuk:
1. Draf pesan WhatsApp yang personal, eksklusif, dan sopan
2. Ide penawaran khusus (prioritas packing, diskon agen/kafe)
3. Strategi komunikasi berkala
4. Cara mengidentifikasi pelanggan potensial baru

{ml_summary}
"""
            st.button("🤖 Diskusikan Pelanggan VIP Ini dengan AI Data Analyst", type="secondary", key="btn_ai_clustering", on_click=trigger_chatbox, args=(ai_ctx,))

with tab3:
    st.subheader("Pilar Operasional: Prediksi (Forecasting)")
    st.caption("Memprediksi omzet bulan depan untuk keperluan stok barang agar tidak *overstock* atau *out of stock*.")
    st.markdown("---")

    # Initialize session state for forecasting results
    if "forecast_result" not in st.session_state:
        st.session_state.forecast_result = None
    if "forecast_params" not in st.session_state:
        st.session_state.forecast_params = {}

    col_days, col_btn = st.columns([1, 2])
    with col_days:
        forecast_days = st.number_input("Rentang Waktu Prediksi (Hari)", min_value=7, max_value=90, value=30, step=7, key="forecast_days")
    with col_btn:
        st.write("") # spacing
        st.write("") # spacing

    # Check if parameters changed
    forecast_params_changed = st.session_state.forecast_params.get("forecast_days") != forecast_days

    # Reset button
    if st.session_state.forecast_result is not None and not forecast_params_changed:
        if st.button("🔄 Reset Hasil", key="reset_forecast"):
            st.session_state.forecast_result = None
            st.session_state.forecast_params = {}
            st.rerun()

    # Auto-run on first visit or when parameters changed
    run_forecast = st.button("📈 Jalankan Prediksi Omzet", type="primary", key="run_forecast") or st.session_state.forecast_result is None

    if run_forecast:
        with st.spinner("Memproses data historis dan melatih model Holt-Winters ETS..."):
            from core.data_manager import get_tables, build_master
            from core.ml_engine import MLEngine
            
            tables = get_tables()
            if not tables:
                st.error("❌ Gagal memuat data tabel dari Supabase/Session.")
                st.stop()
                
            df_master = build_master(tables)
            if df_master.empty:
                st.error("❌ Data transaksi kosong. Pastikan Anda sudah mengunggah data di halaman Upload.")
                st.stop()
                
            ml = MLEngine(df_master)
            result = ml.revenue_forecasting(forecast_days=forecast_days)
            
            if "error" in result:
                st.error(f"❌ Gagal: {result['error']}")
            else:
                # Store result in session state
                st.session_state.forecast_result = result
                st.session_state.forecast_params = {"forecast_days": forecast_days}
                metrics = result["metrics"]
                history_df = result["history"]
                forecast_df = result["forecast"]

                st.success("✨ Prediksi berhasil dijalankan!")
                
                # Metrics Row
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Omzet Prediksi", f"Rp {metrics['total_forecast']:,.0f}")
                m2.metric("Rata-rata Harian Prediksi", f"Rp {metrics['avg_daily_forecast']:,.0f}")
                
                # Menentukan kualitas model dari MAPE
                mape = metrics['mape_percent']
                kualitas = "Sangat Baik 🏆" if mape < 10 else "Baik 👍" if mape < 20 else "Cukup 🆗" if mape < 30 else "Buruk ⚠️"
                m3.metric("Error Model (MAPE)", f"{mape}%", kualitas, delta_color="off")
                
                # Plotly Chart
                import plotly.graph_objects as go
                import pandas as pd
                
                fig = go.Figure()
                
                # History (Actual)
                fig.add_trace(go.Scatter(
                    x=history_df["date"], y=history_df["revenue"],
                    mode="lines", name="Omzet Aktual",
                    line=dict(color="#0ea5e9", width=2)
                ))
                
                # Connect last history point to first forecast point for a smooth line
                last_hist = history_df.iloc[-1:]
                first_fc = forecast_df.iloc[:1]
                connect_df = pd.concat([last_hist, first_fc])
                fig.add_trace(go.Scatter(
                    x=connect_df["date"], y=connect_df["revenue"],
                    mode="lines", showlegend=False,
                    line=dict(color="#f59e0b", width=2, dash="dash")
                ))
                
                # Forecast
                fig.add_trace(go.Scatter(
                    x=forecast_df["date"], y=forecast_df["revenue"],
                    mode="lines", name="Prediksi (Forecast)",
                    line=dict(color="#f59e0b", width=2, dash="dash")
                ))
                
                fig.update_layout(
                    title=f"Grafik Prediksi Omzet {forecast_days} Hari Kedepan",
                    xaxis_title="Tanggal",
                    yaxis_title="Omzet (Rp)",
                    hovermode="x unified",
                    plot_bgcolor="rgba(255,255,255,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Insight Text
                st.info(f"""
                **💡 Insight Bisnis:** 
                Berdasarkan data {metrics['data_points']} hari ke belakang, model memproyeksikan total pendapatan sebesar **Rp {metrics['total_forecast']:,.0f}** 
                untuk {forecast_days} hari ke depan (rata-rata **Rp {metrics['avg_daily_forecast']:,.0f}** / hari). 
                Gunakan angka ini sebagai patokan anggaran pengadaan stok agar *cashflow* Anda tetap sehat.

                *(Catatan: Mengapa garis prediksi terlihat mendatar/stagnan? Karena sistem prediksi (Machine Learning Klasik) ini sangat berhati-hati. Jika ia melihat ada penurunan omzet di minggu-minggu terakhir (seperti akhir Juni), ia akan memproyeksikan tren yang stabil/datar untuk mencegah Anda kulakan barang terlalu banyak alias overstock).*
                """)
                
                st.write("")
                ml_summary = get_ml_summary_context()
                ai_ctx = f"""
═══════════════════════════════════════════════════════════════
📈 FOKUS UTAMA: PREDIKSI OMZET & STRATEGI STOK (FORECASTING)
═══════════════════════════════════════════════════════════════

Anda adalah AI Data Analyst. User ingin mendiskusikan PREDIKSI OMZET & STRATEGI STOK.

📊 DATA YANG DIBAHAS SAAT INI:
- Prediksi {forecast_days} hari ke depan: Rp {metrics['total_forecast']:,.0f}
- Rata-rata harian: Rp {metrics['avg_daily_forecast']:,.0f}
- Error Model (MAPE): {mape}% ({'Sangat Baik 🏆' if mape < 10 else 'Baik 👍' if mape < 20 else 'Cukup 🆗' if mape < 30 else 'Buruk ⚠️'})
- Data historis: {metrics['data_points']} hari ke belakang

🎯 TUGAS ANDA:
Analisis tren omzet dan buat strategi operasional:
1. Penjelasan tren (kenapa naik/turun, efek payday/gajian, seasonal pattern)
2. Rekomendasi pengadaan stok (berapa, kapan, apa produk)
3. Strategi marketing di tanggal-tanggal sibuk
4. Cara mengatasi prediksi yang stagnan/menurun

{ml_summary}
"""
                st.button("🤖 Diskusikan Grafik & Tren Omzet Ini dengan AI Data Analyst", type="secondary", key="btn_ai_forecasting", on_click=trigger_chatbox, args=(ai_ctx,))

    # Display cached forecast results if available (and parameters haven't changed)
    if st.session_state.forecast_result is not None and not forecast_params_changed:
        result = st.session_state.forecast_result
        metrics = result["metrics"]
        history_df = result["history"]
        forecast_df = result["forecast"]
        forecast_days = st.session_state.forecast_params.get("forecast_days", 30)

        st.success("✨ Prediksi berhasil dijalankan! (Cached)")

        # Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Omzet Prediksi", f"Rp {metrics['total_forecast']:,.0f}")
        m2.metric("Rata-rata Harian Prediksi", f"Rp {metrics['avg_daily_forecast']:,.0f}")

        # Menentukan kualitas model dari MAPE
        mape = metrics['mape_percent']
        kualitas = "Sangat Baik 🏆" if mape < 10 else "Baik 👍" if mape < 20 else "Cukup 🆗" if mape < 30 else "Buruk ⚠️"
        m3.metric("Error Model (MAPE)", f"{mape}%", kualitas, delta_color="off")

        # Plotly Chart
        import plotly.graph_objects as go
        import pandas as pd

        fig = go.Figure()

        # History (Actual)
        fig.add_trace(go.Scatter(
            x=history_df["date"], y=history_df["revenue"],
            mode="lines", name="Omzet Aktual",
            line=dict(color="#0ea5e9", width=2)
        ))

        # Connect last history point to first forecast point for a smooth line
        last_hist = history_df.iloc[-1:]
        first_fc = forecast_df.iloc[:1]
        connect_df = pd.concat([last_hist, first_fc])
        fig.add_trace(go.Scatter(
            x=connect_df["date"], y=connect_df["revenue"],
            mode="lines", showlegend=False,
            line=dict(color="#f59e0b", width=2, dash="dash")
        ))

        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_df["date"], y=forecast_df["revenue"],
            mode="lines", name="Prediksi (Forecast)",
            line=dict(color="#f59e0b", width=2, dash="dash")
        ))

        fig.update_layout(
            title=f"Grafik Prediksi Omzet {forecast_days} Hari Kedepan",
            xaxis_title="Tanggal",
            yaxis_title="Omzet (Rp)",
            hovermode="x unified",
            plot_bgcolor="rgba(255,255,255,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Insight Text
        st.info(f"""
        **💡 Insight Bisnis:**
        Berdasarkan data {metrics['data_points']} hari ke belakang, model memproyeksikan total pendapatan sebesar **Rp {metrics['total_forecast']:,.0f}**
        untuk {forecast_days} hari ke depan (rata-rata **Rp {metrics['avg_daily_forecast']:,.0f}** / hari).
        Gunakan angka ini sebagai patokan anggaran pengadaan stok agar *cashflow* Anda tetap sehat.

        *(Catatan: Mengapa garis prediksi terlihat mendatar/stagnan? Karena sistem prediksi (Machine Learning Klasik) ini sangat berhati-hati. Jika ia melihat ada penurunan omzet di minggu-minggu terakhir (seperti akhir Juni), ia akan memproyeksikan tren yang stabil/datar untuk mencegah Anda kulakan barang terlalu banyak alias overstock).*
        """)

        st.write("")
        ml_summary = get_ml_summary_context()
        ai_ctx = f"""
═══════════════════════════════════════════════════════════════
📈 FOKUS UTAMA: PREDIKSI OMZET & STRATEGI STOK (FORECASTING)
═══════════════════════════════════════════════════════════════

Anda adalah AI Data Analyst. User ingin mendiskusikan PREDIKSI OMZET & STRATEGI STOK.

📊 DATA YANG DIBAHAS SAAT INI:
- Prediksi {forecast_days} hari ke depan: Rp {metrics['total_forecast']:,.0f}
- Rata-rata harian: Rp {metrics['avg_daily_forecast']:,.0f}
- Error Model (MAPE): {mape}% ({'Sangat Baik 🏆' if mape < 10 else 'Baik 👍' if mape < 20 else 'Cukup 🆗' if mape < 30 else 'Buruk ⚠️'})
- Data historis: {metrics['data_points']} hari ke belakang

🎯 TUGAS ANDA:
Analisis tren omzet dan buat strategi operasional:
1. Penjelasan tren (kenapa naik/turun, efek payday/gajian, seasonal pattern)
2. Rekomendasi pengadaan stok (berapa, kapan, apa produk)
3. Strategi marketing di tanggal-tanggal sibuk
4. Cara mengatasi prediksi yang stagnan/menurun

{ml_summary}
"""
        st.button("🤖 Diskusikan Grafik & Tren Omzet Ini dengan AI Data Analyst", type="secondary", key="btn_ai_forecasting_cached", on_click=trigger_chatbox, args=(ai_ctx,))

render_sidebar_footer()
