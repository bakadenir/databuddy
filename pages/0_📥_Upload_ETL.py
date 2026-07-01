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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stProgress > div > div { background: linear-gradient(90deg, #f97316, #fbbf24); }

.success-box {
    background: #052e16; border: 1px solid #166534;
    border-radius: 10px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    color: #86efac;
}
.warning-box {
    background: #1c1917; border: 1px solid #a16207;
    border-radius: 10px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    color: #fde68a;
}
.error-box {
    background: #1c0a09; border: 1px solid #991b1b;
    border-radius: 10px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    color: #fca5a5;
}
.info-card {
    background: #1e293b; border: 1px solid #334155;
    border-radius: 10px; padding: 1rem 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────
st.markdown("""
<h2 style="
    background: linear-gradient(135deg, #f97316, #fbbf24);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0;
">📥 Upload & ETL Pipeline</h2>
<p style="color:#94a3b8; margin-top:0.2rem;">
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
                background:#1e293b; border:1px solid #334155;
                border-left:4px solid {color}; border-radius:8px;
                padding:0.8rem; margin-bottom:0.5rem; text-align:center;
            ">
                <div style="color:{color}; font-size:0.75rem; font-weight:600;">{label}</div>
                <div style="color:#f8fafc; font-size:1.4rem; font-weight:700;">{len(df_tbl):,}</div>
                <div style="color:#64748b; font-size:0.7rem;">baris</div>
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

    st.divider()

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
