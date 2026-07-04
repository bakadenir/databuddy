"""
pages/0_Upload_ETL.py — Halaman Upload & ETL Pipeline
Upload file CSV/Excel Shopee → ETL → Preview → Push ke Supabase
Modern Soft Design
"""

import streamlit as st
import pandas as pd
import io
from components.ui import (
    render_navbar, section_header, card, info_box,
    empty_state, COLORS, SPACING, BORDER_RADIUS
)

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="ETL — DataBuddy",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Render Top Navigation
render_navbar()

# ── Header ─────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom: 0.5rem;">
    <h1 style="
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        line-height: 1.2;
        letter-spacing: -0.02em;
    ">Upload & ETL Pipeline</h1>
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1.5rem; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 0.5rem; background: white; padding: 0.5rem 1rem; border-radius: 50px; font-size: 0.9rem; font-weight: 600; color: #475569; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
            <span style="font-size: 1.1rem;">📤</span> 1. Upload Data Shopee
        </div>
        <div style="color: #94a3b8; font-size: 1.2rem;">➔</div>
        <div style="display: flex; align-items: center; gap: 0.5rem; background: #e0e7ff; padding: 0.5rem 1rem; border-radius: 50px; font-size: 0.9rem; font-weight: 600; color: #4338ca; border: 1px solid #c7d2fe; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
            <span style="font-size: 1.1rem;">⚙️</span> 2. AI Otomatis Memproses
        </div>
        <div style="color: #94a3b8; font-size: 1.2rem;">➔</div>
        <div style="display: flex; align-items: center; gap: 0.5rem; background: #dcfce7; padding: 0.5rem 1rem; border-radius: 50px; font-size: 0.9rem; font-weight: 600; color: #15803d; border: 1px solid #bbf7d0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
            <span style="font-size: 1.1rem;">📊</span> 3. Dashboard Analitik Siap
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# (Technical ETL details hidden for cleaner UX)
# ── Upload File ────────────────────────────────────────────────
section_header("Upload File Shopee", "📤", "Pilih file CSV atau Excel hasil ekspor Shopee Seller Center")

uploaded = st.file_uploader(
    "Upload area",
    type=["csv", "xlsx", "xls"],
    help="Maksimal 200MB. Format: CSV UTF-8 atau Excel (.xlsx / .xls)",
    key="shopee_file_upload",
    label_visibility="collapsed"
)

if not uploaded:
    st.markdown(f"""
    <div style="
        background: {COLORS['info_light']};
        border-left: 4px solid {COLORS['info']};
        border-radius: {BORDER_RADIUS['md']};
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    ">
        <div style="color: {COLORS['info']}; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem;">
            💡 Kolom yang harus ada di file Shopee:
        </div>
        <div style="color: {COLORS['text']}; font-size: 0.85rem; line-height: 1.6;">
            No. Pesanan · Waktu Pesanan Dibuat · Nama Produk · Nama Variasi ·
            Username (Pembeli) · Kota/Kabupaten · Provinsi · Metode Pembayaran ·
            Status Pesanan · Opsi Pengiriman · Jumlah · Harga Awal ·
            Harga Setelah Diskon · Total Diskon
        </div>
    </div>
    """, unsafe_allow_html=True)

else:

    # ── Proses ETL ─────────────────────────────────────────────────
    from etl.loader import load_file
    from etl.validator import validate
    from etl.transformer import run_etl
    from core.config import config

    # Load file
    with st.spinner("📂 Membaca file..."):
        try:
            df_raw, file_info = load_file(uploaded)
        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")
            st.stop()

    # Validasi
    validation = validate(df_raw)

    # Summary cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: {BORDER_RADIUS['lg']};
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        ">
            <div style="color: {COLORS['muted']}; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                📄 Total Baris
            </div>
            <div style="color: {COLORS['text']}; font-size: 1.75rem; font-weight: 800;">
                {file_info['rows']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: {BORDER_RADIUS['lg']};
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        ">
            <div style="color: {COLORS['muted']}; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                📊 Total Kolom
            </div>
            <div style="color: {COLORS['text']}; font-size: 1.75rem; font-weight: 800;">
                {len(file_info.get('columns', []))}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        status_color = COLORS['success'] if validation['valid'] else COLORS['error']
        status_text = "Valid ✅" if validation['valid'] else "Ada Masalah ❌"
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: {BORDER_RADIUS['lg']};
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        ">
            <div style="color: {COLORS['muted']}; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                ✅ Status
            </div>
            <div style="color: {status_color}; font-size: 1.75rem; font-weight: 800;">
                {status_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not validation["valid"]:
        st.error(f"❌ **Kolom wajib tidak ditemukan:** {', '.join(validation['missing_cols'])}")
        st.stop()

    if validation["warnings"]:
        for w in validation["warnings"]:
            st.warning(w)

    st.markdown("<p style='color: #16a34a; font-weight: 600; font-size: 1rem; margin-top: 1rem;'>✅ File ini sudah di-cek dan 100% valid! Data siap diproses ke Database.</p>", unsafe_allow_html=True)

    st.divider()

    # ── Jalankan ETL ───────────────────────────────────────────────
    section_header("Proses ETL", "⚙️", "Transform data ke dalam 8 tabel dimensi dan fakta")

    # Cek HPP Source of Truth
    hpp_source = "offline"
    existing_products = None

    if config.has_supabase:
        info_box(
            "Supabase Terdeteksi 🔗",
            "HPP produk yang sudah ada akan diambil dari Supabase sebagai Source of Truth. "
            "Produk baru akan mendapat HPP = 0 (perlu diisi manual).",
            icon="✅",
            variant="success"
        )
        hpp_source = "supabase"
    else:
        info_box(
            "Mode Offline ⚠️",
            "Supabase belum dikonfigurasi. Semua produk mendapat HPP = 0. "
            "Isi `.env` untuk aktifkan Supabase.",
            icon="⚠️",
            variant="warning"
        )

    run_btn = st.button(
        "🚀 Jalankan ETL",
        type="primary",
        use_container_width=True,
        key="run_etl_btn",
    )

    if run_btn or st.session_state.get("etl_done"):

        if run_btn:
            # Fetch existing products jika Supabase tersedia
            if hpp_source == "supabase":
                from etl.uploader import get_existing_products
                with st.spinner("📡 Mengambil Buku Induk Produk dari Supabase..."):
                    existing_products = get_existing_products()

            with st.spinner("⚙️ Menjalankan ETL pipeline..."):
                try:
                    tables = run_etl(df_raw, existing_products)
                    st.session_state["etl_tables"] = tables
                    st.session_state["etl_done"] = True
                    st.cache_data.clear()
                    st.success("✅ ETL selesai! Mengalihkan ke Dashboard...")
                    import time
                    time.sleep(1.5)
                    st.switch_page("pages/1_Dashboard.py")
                except Exception as e:
                    st.error(f"❌ ETL gagal: {e}")
                    st.exception(e)
                    st.stop()

        tables = st.session_state.get("etl_tables", {})
        if not tables:
            st.stop()

        st.divider()

        # ── Preview Hasil ──────────────────────────────────────────
        section_header("Preview Hasil ETL", "👀", "Lihat 8 tabel hasil transformasi data")

        TABLE_INFO = {
            "fact_order_item": ("🧾 Fakta Transaksi", "#f97316", "#fff7ed"),
            "dim_product":     ("📦 Dimensi Produk",  "#8b5cf6", "#f5f3ff"),
            "dim_customer":    ("👤 Pelanggan",        "#06b6d4", "#ecfeff"),
            "dim_date":        ("📅 Tanggal",          "#22c55e", "#ecfdf5"),
            "dim_payment":     ("💳 Pembayaran",       "#eab308", "#fefce8"),
            "dim_status":      ("🏷️ Status Pesanan",  "#f43f5e", "#fef2f2"),
            "dim_shipping":    ("🚚 Ekspedisi",        "#a78bfa", "#f5f3ff"),
            "dim_location":    ("📍 Lokasi",           "#34d399", "#ecfdf5"),
        }

        # Summary cards
        cols = st.columns(4)
        for i, (tbl, df_tbl) in enumerate(tables.items()):
            label, color, bg = TABLE_INFO.get(tbl, (tbl, COLORS['muted'], COLORS['bg']))
            with cols[i % 4]:
                st.markdown(f"""
                <div style="
                    background: {bg};
                    border: 2px solid {color};
                    border-radius: {BORDER_RADIUS['lg']};
                    padding: 1rem;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                    transition: all 0.2s ease;
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(0,0,0,0.08)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.04)'">
                    <div style="color: {color}; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">
                        {label}
                    </div>
                    <div style="color: {COLORS['text']}; font-size: 1.5rem; font-weight: 800;">
                        {len(df_tbl):,}
                    </div>
                    <div style="color: {COLORS['muted']}; font-size: 0.7rem; margin-top: 0.25rem;">
                        baris
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Detail per tabel
        selected = st.selectbox(
            "Lihat detail tabel:",
            options=list(tables.keys()),
            format_func=lambda x: TABLE_INFO.get(x, (x, "", ""))[0],
            key="preview_table_select",
        )
        if selected:
            df_preview = tables[selected]
            st.dataframe(df_preview.head(50), use_container_width=True, height=300)

            # HPP warning untuk dim_product
            if selected == "dim_product" and "hpp" in df_preview.columns:
                n_zero = (df_preview["hpp"] == 0).sum()
                if n_zero > 0:
                    info_box(
                        f"HPP Kosong pada {n_zero} Produk",
                        "Setelah upload ke Supabase, isi HPP-nya langsung di tabel Supabase.",
                        icon="⚠️",
                        variant="warning"
                    )

        # ── Diagnostik Harga (Debug Revenue) ───────────────────
        with st.expander("🔍 Diagnostik Harga — Klik untuk verifikasi parsing nominal", expanded=True):
            fact_tbl = tables.get("fact_order_item", pd.DataFrame())
            if not fact_tbl.empty and "discounted_price" in fact_tbl.columns:
                price_cols = ["order_id", "quantity", "original_price",
                              "discounted_price", "total_discount", "valid_item_revenue"]
                sample = fact_tbl[price_cols].head(10)

                st.markdown("**10 Baris Pertama — Kolom Harga (setelah parse):**")
                st.dataframe(sample, use_container_width=True, height=250)

                # Statistik cepat
                d1, d2, d3, d4 = st.columns(4)
                d1.metric("Max Harga Satuan",   f"Rp {int(fact_tbl['discounted_price'].max()):,}")
                d2.metric("Median Harga",        f"Rp {int(fact_tbl['discounted_price'].median()):,}")
                d3.metric("Max Revenue/Baris",   f"Rp {int(fact_tbl['valid_item_revenue'].max()):,}")
                d4.metric("Total Revenue Raw",   f"Rp {int(fact_tbl['valid_item_revenue'].sum()):,}")

                st.caption(
                    "💡 Jika 'Max Harga Satuan' masih tampak sangat kecil (< 1000), "
                    "berarti ada masalah parsing format angka. Screenshot dan kirim ke chat."
                )
            else:
                st.info("Jalankan ETL dulu untuk melihat diagnostik harga.")

        # ── Simpan / Upload ────────────────────────────────────────
        section_header("Simpan Hasil", "💾", "Pilih opsi penyimpanan data")

        save_col1, save_col2 = st.columns(2)

        with save_col1:
            st.markdown(f"""
            <div style="
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: {BORDER_RADIUS['lg']};
                padding: 1.25rem;
                margin-bottom: 1rem;
            ">
                <div style="color: {COLORS['text']}; font-weight: 700; font-size: 1rem; margin-bottom: 1rem;">
                    💾 Download Lokal (CSV)
                </div>
            """, unsafe_allow_html=True)

            for tbl_name, df_tbl in tables.items():
                buf = io.StringIO()
                df_tbl.to_csv(buf, index=False)
                st.download_button(
                    label=f"⬇️ {tbl_name}.csv",
                    data=buf.getvalue(),
                    file_name=f"{tbl_name}.csv",
                    mime="text/csv",
                    key=f"dl_{tbl_name}",
                    use_container_width=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        with save_col2:
            st.markdown(f"""
            <div style="
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: {BORDER_RADIUS['lg']};
                padding: 1.25rem;
                margin-bottom: 1rem;
            ">
                <div style="color: {COLORS['text']}; font-weight: 700; font-size: 1rem; margin-bottom: 1rem;">
                    ☁️ Push ke Supabase
                </div>
            """, unsafe_allow_html=True)

            if not config.has_supabase:
                info_box(
                    "Supabase Belum Dikonfigurasi",
                    "Isi `SUPABASE_URL` dan `SUPABASE_KEY` di file `.env` untuk mengaktifkan fitur ini.",
                    icon="⚠️",
                    variant="warning"
                )
            else:
                info_box(
                    "Upsert Mode",
                    "Upload akan melakukan Upsert (insert jika baru, skip jika sudah ada). "
                    "HPP yang sudah diisi manual di Supabase tidak akan tertimpa.",
                    icon="ℹ️",
                    variant="info"
                )
                push_btn = st.button(
                    "☁️ Push ke Supabase",
                    type="primary",
                    use_container_width=True,
                    key="push_supabase_btn",
                )
                if push_btn:
                    from etl.uploader import upload_all
                    with st.spinner("📡 Mengupload ke Supabase..."):
                        try:
                            results = upload_all(tables)
                            success = [r for r in results if r.get("success")]
                            failed  = [r for r in results if not r.get("success")]

                            if failed:
                                st.error(
                                    f"❌ {len(failed)} tabel gagal: "
                                    + ", ".join(r["table"] for r in failed)
                                )
                            else:
                                st.success(f"✅ Semua {len(results)} tabel berhasil diupload ke Supabase!")
                                st.balloons()

                            with st.expander("Detail hasil upload"):
                                for r in results:
                                    icon = "✅" if r.get("success") else "❌"
                                    st.write(f"{icon} **{r['table']}**: {r}")
                        except Exception as e:
                            st.error(f"❌ Upload gagal: {e}")
                            st.exception(e)

            st.markdown("</div>", unsafe_allow_html=True)
