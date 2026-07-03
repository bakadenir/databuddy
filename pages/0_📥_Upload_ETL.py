"""
pages/0_📥_Upload_ETL.py — Halaman Upload & ETL Pipeline
Upload file CSV/Excel Shopee → ETL → Preview → Push ke Supabase
"""

import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Upload & ETL | DataBuddy",
    page_icon="📥",
    layout="wide",
)

# ── Styling ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #f0f9ff 0%, #fafafa 45%, #fdf4ff 100%);
}
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] * { color: #334155 !important; }

.stProgress > div > div { background: linear-gradient(90deg, #0ea5e9, #6366f1); }

.success-box {
    background: #f0fdf4; border: 1px solid #86efac;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    color: #166534;
}
.warning-box {
    background: #fffbeb; border: 1px solid #fcd34d;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    color: #92400e;
}
.error-box {
    background: #fef2f2; border: 1px solid #fca5a5;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    color: #991b1b;
}
.info-card {
    background: #f0f9ff; border: 1px solid #bae6fd;
    border-radius: 12px; padding: 1rem 1.2rem;
}
div[data-testid="metric-container"] {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 16px; padding: 1rem 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
div[data-testid="metric-container"] label {
    color: #64748b !important; font-size: 0.8rem !important;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #0f172a !important; font-size: 1.5rem !important; font-weight: 700 !important;
}
hr { border-color: #e2e8f0 !important; }
.stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }
div[data-testid="stAlert"] { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────
st.markdown("""
<h2 style="
    background: linear-gradient(135deg, #0ea5e9, #6366f1, #f97316);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0; font-weight: 800;
">📥 Upload & ETL Pipeline</h2>
<p style="color:#64748b; margin-top:0.2rem;">
    Upload data ekspor Shopee → Otomatis diproses → Simpan ke database
</p>
""", unsafe_allow_html=True)

st.divider()

# ── Alur ETL ───────────────────────────────────────────────────
with st.expander("📋 Lihat Alur ETL", expanded=False):
    st.markdown("""
    ```
    Upload CSV/Excel
         │
         ▼
    [Validator] Cek kolom wajib Shopee
         │
         ▼
    [Transformer] Buat 7 dimensi + 1 fact table
         │  ├─ dim_product   (+ HPP dari Supabase jika tersedia)
         │  ├─ dim_customer
         │  ├─ dim_location
         │  ├─ dim_date      (1 baris per hari — ~180 baris = BENAR ✓)
         │  ├─ dim_payment
         │  ├─ dim_status
         │  ├─ dim_shipping
         │  └─ fact_order_item
         │
         ▼
    [Preview] Tampilkan hasil ETL
         │
         ▼
    [Pilih] Simpan Lokal (CSV) ATAU Push ke Supabase
    ```
    """)
    st.info(
        "**Tentang dim_date:** Tabel ini berisi 1 baris per HARI unik (kalender harian), "
        "bukan per transaksi. Untuk data 6 bulan → ~180 baris adalah **BENAR** ✓. "
        "Tabel `fact_order_item` yang menyimpan semua 8000+ transaksi."
    )

# ── Upload File ────────────────────────────────────────────────
st.subheader("1️⃣ Upload File Shopee")

uploaded = st.file_uploader(
    "Pilih file CSV atau Excel hasil ekspor Shopee Seller Center",
    type=["csv", "xlsx", "xls"],
    help="Maksimal 200MB. Format: CSV UTF-8 atau Excel (.xlsx / .xls)",
    key="shopee_file_upload",
)

if not uploaded:
    st.markdown("""
    <div class="info-card">
        <p style="color:#94a3b8; margin:0; font-size:0.9rem;">
            💡 <strong style="color:#f8fafc;">Kolom yang harus ada di file Shopee:</strong><br>
            No. Pesanan · Waktu Pesanan Dibuat · Nama Produk · Nama Variasi ·
            Username (Pembeli) · Kota/Kabupaten · Provinsi · Metode Pembayaran ·
            Status Pesanan · Opsi Pengiriman · Jumlah · Harga Awal ·
            Harga Setelah Diskon · Total Diskon
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

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

col1, col2, col3 = st.columns(3)
col1.metric("📄 Total Baris", f"{file_info['rows']:,}")
col2.metric("📊 Total Kolom", len(file_info.get('columns', [])))
col3.metric("✅ Status", "Valid" if validation["valid"] else "Ada Masalah")

if not validation["valid"]:
    st.markdown(f"""
    <div class="error-box">
        ❌ <strong>Kolom wajib tidak ditemukan:</strong><br>
        {', '.join(validation['missing_cols'])}
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if validation["warnings"]:
    for w in validation["warnings"]:
        st.markdown(f'<div class="warning-box">⚠️ {w}</div>', unsafe_allow_html=True)

st.markdown('<div class="success-box">✅ File valid! Siap diproses.</div>', unsafe_allow_html=True)

st.divider()

# ── Jalankan ETL ───────────────────────────────────────────────
st.subheader("2️⃣ Proses ETL")

# Cek HPP Source of Truth
hpp_source = "offline"
existing_products = None

if config.has_supabase:
    st.info(
        "🔗 **Supabase terdeteksi!** HPP produk yang sudah ada akan diambil dari "
        "Supabase sebagai Source of Truth. Produk baru akan mendapat HPP = 0 (perlu diisi manual)."
    )
    hpp_source = "supabase"
else:
    st.warning(
        "⚠️ **Mode Offline** — Supabase belum dikonfigurasi. "
        "Semua produk mendapat HPP = 0. Isi `.env` untuk aktifkan Supabase."
    )

run_btn = st.button(
    "🚀 Jalankan ETL",
    type="primary",
    width="stretch",
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
                # ⬇️ Wajib clear cache dashboard agar pakai data terbaru
                st.cache_data.clear()
                st.success("✅ ETL selesai! Semua 8 tabel berhasil dibuat.")
            except Exception as e:
                st.error(f"❌ ETL gagal: {e}")
                st.exception(e)
                st.stop()

    tables = st.session_state.get("etl_tables", {})
    if not tables:
        st.stop()

    st.divider()

    # ── Preview Hasil ──────────────────────────────────────────
    st.subheader("3️⃣ Preview Hasil ETL")

    TABLE_INFO = {
        "fact_order_item": ("🧾 Fakta Transaksi", "#f97316"),
        "dim_product":     ("📦 Dimensi Produk",  "#8b5cf6"),
        "dim_customer":    ("👤 Pelanggan",        "#06b6d4"),
        "dim_date":        ("📅 Tanggal",          "#22c55e"),
        "dim_payment":     ("💳 Pembayaran",       "#eab308"),
        "dim_status":      ("🏷️ Status Pesanan",  "#f43f5e"),
        "dim_shipping":    ("🚚 Ekspedisi",        "#a78bfa"),
        "dim_location":    ("📍 Lokasi",           "#34d399"),
    }

    # Summary cards
    cols = st.columns(4)
    for i, (tbl, df_tbl) in enumerate(tables.items()):
        label, color = TABLE_INFO.get(tbl, (tbl, "#94a3b8"))
        with cols[i % 4]:
            st.markdown(f"""
            <div style="
                background:#ffffff; border:1px solid #e2e8f0;
                border-left:4px solid {color}; border-radius:12px;
                padding:0.8rem; margin-bottom:0.5rem; text-align:center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            ">
                <div style="color:{color}; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">{label}</div>
                <div style="color:#0f172a; font-size:1.5rem; font-weight:800;">{len(df_tbl):,}</div>
                <div style="color:#94a3b8; font-size:0.7rem;">baris</div>
            </div>
            """, unsafe_allow_html=True)

    # Detail per tabel
    selected = st.selectbox(
        "Lihat detail tabel:",
        options=list(tables.keys()),
        format_func=lambda x: TABLE_INFO.get(x, (x, ""))[0],
        key="preview_table_select",
    )
    if selected:
        df_preview = tables[selected]
        st.dataframe(df_preview.head(50), width="stretch", height=300)

        # HPP warning untuk dim_product
        if selected == "dim_product" and "hpp" in df_preview.columns:
            n_zero = (df_preview["hpp"] == 0).sum()
            if n_zero > 0:
                st.warning(
                    f"⚠️ **{n_zero} produk** memiliki HPP = 0. "
                    "Setelah upload ke Supabase, isi HPP-nya langsung di tabel Supabase."
                )

    # ── 🔍 Diagnostik Harga (Debug Revenue) ───────────────────
    with st.expander("🔍 Diagnostik Harga — Klik untuk verifikasi parsing nominal", expanded=True):
        fact_tbl = tables.get("fact_order_item", pd.DataFrame())
        if not fact_tbl.empty and "discounted_price" in fact_tbl.columns:
            price_cols = ["order_id", "quantity", "original_price",
                          "discounted_price", "total_discount", "valid_item_revenue"]
            sample = fact_tbl[price_cols].head(10)

            st.markdown("**10 Baris Pertama — Kolom Harga (setelah parse):**")
            st.dataframe(sample, width="stretch", height=250)

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
    st.subheader("4️⃣ Simpan Hasil")

    save_col1, save_col2 = st.columns(2)

    with save_col1:
        st.markdown("**💾 Download Lokal (CSV)**")
        for tbl_name, df_tbl in tables.items():
            buf = io.StringIO()
            df_tbl.to_csv(buf, index=False)
            st.download_button(
                label=f"⬇️ {tbl_name}.csv",
                data=buf.getvalue(),
                file_name=f"{tbl_name}.csv",
                mime="text/csv",
                key=f"dl_{tbl_name}",
                width="stretch",
            )

    with save_col2:
        st.markdown("**☁️ Push ke Supabase**")
        if not config.has_supabase:
            st.markdown("""
            <div class="warning-box">
                ⚠️ Supabase belum dikonfigurasi.<br>
                Isi <code>SUPABASE_URL</code> dan <code>SUPABASE_KEY</code>
                di file <code>.env</code> untuk mengaktifkan fitur ini.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(
                "Upload akan melakukan **Upsert** (insert jika baru, skip jika sudah ada). "
                "HPP yang sudah diisi manual di Supabase **tidak akan tertimpa**."
            )
            push_btn = st.button(
                "☁️ Push ke Supabase",
                type="primary",
                width="stretch",
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
