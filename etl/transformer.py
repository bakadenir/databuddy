"""
etl/transformer.py — Transformasi data Shopee mentah → 7 dim + 1 fact

Ported & upgraded dari Google Colab script:
- Cleaning whitespace & parsing tanggal
- Pembuatan semua tabel dimensi
- Perakitan fact_order_item
- Dukungan HPP Source of Truth (dari Supabase via existing_products)
"""

import pandas as pd
import numpy as np
import re
from typing import Optional


# ── KONSTANTA ─────────────────────────────────────────────────
DEFAULT_HPP = 0  # Pakai 0 bukan 50000 → lebih jelas "belum diisi"

NAMA_BULAN_ID = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}

NAMA_HARI_ID = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat",
    "Saturday": "Sabtu", "Sunday": "Minggu",
}


# ── PARSER NOMINAL IDR ────────────────────────────────────────

def parse_idr(val) -> int:
    """
    Parse format Rupiah Indonesia ke integer.

    Format yang didukung (dari Excel Shopee):
      "50.000"       → 50000   (titik = pemisah ribuan Indonesia)
      "1.500.000"    → 1500000
      "50,000"       → 50000   (koma = pemisah ribuan barat)
      "50000"        → 50000   (tanpa pemisah)
      "50.000,00"    → 50000   (ribuan titik + desimal koma)
      ""  / nan      → 0

    Masalah umum:
      pd.to_numeric("50.000") = 50.0  ← SALAH (titik dianggap desimal)
      parse_idr("50.000")     = 50000 ← BENAR
    """
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0
    s = str(val).strip()
    if s in ("", "nan", "None", "-", "0.0"):
        return 0

    # Hapus karakter non-numerik kecuali titik dan koma
    s = re.sub(r"[^\d.,]", "", s)
    if not s:
        return 0

    # ── Deteksi & konversi format ──────────────────────────────
    # Case 1: Ada koma DAN titik → format "1.500.000,00" atau "1,500,000.00"
    if "." in s and "," in s:
        last_dot   = s.rfind(".")
        last_comma = s.rfind(",")
        if last_dot > last_comma:
            # Format barat: 1,500,000.00 → hapus koma, titik = desimal
            s = s.replace(",", "")
        else:
            # Format Indonesia: 1.500.000,00 → hapus titik, ganti koma = desimal
            s = s.replace(".", "").replace(",", ".")

    # Case 2: Hanya titik → cek apakah pemisah ribuan atau desimal
    elif "." in s and "," not in s:
        parts = s.split(".")
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            # Semua bagian setelah titik adalah 3 digit → ribuan Indonesia
            # Contoh: "50.000" → ["50","000"] → 50000
            # Contoh: "1.500.000" → ["1","500","000"] → 1500000
            s = s.replace(".", "")
        # else: titik = desimal (misal "50.5" → biarkan)

    # Case 3: Hanya koma → cek apakah pemisah ribuan atau desimal
    elif "," in s and "." not in s:
        parts = s.split(",")
        if len(parts[-1]) == 3:
            # "50,000" → pemisah ribuan barat
            s = s.replace(",", "")
        else:
            # "50,5" → desimal
            s = s.replace(",", ".")

    try:
        return int(float(s))
    except (ValueError, OverflowError):
        return 0


def parse_idr_series(series: pd.Series) -> pd.Series:
    """Terapkan parse_idr ke seluruh kolom Series."""
    return series.apply(parse_idr)


# ── STAGE 1: CLEANING AWAL ────────────────────────────────────

def clean_raw(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning dasar:
    - Strip whitespace semua kolom teks
    - Parse 'Waktu Pesanan Dibuat' ke datetime
    - Buang baris tanpa tanggal valid
    """
    df = df.copy()

    # Strip whitespace semua kolom object
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Parse tanggal
    df["Waktu Pesanan Dibuat"] = pd.to_datetime(
        df["Waktu Pesanan Dibuat"], errors="coerce"
    )
    rows_before = len(df)
    df = df.dropna(subset=["Waktu Pesanan Dibuat"]).copy()
    rows_dropped = rows_before - len(df)

    if rows_dropped > 0:
        print(f"[WARN] {rows_dropped} baris dibuang karena tanggal tidak valid.")

    # Buat kolom bantu SKU sintetis
    # Catatan: Jika Shopee sudah punya kolom SKU resmi, ganti ke kolom tersebut
    df["sku_sintetis"] = df["Nama Produk"] + " - " + df["Nama Variasi"]

    print(f"[OK] Cleaning selesai. {len(df)} baris valid.")
    return df


# ── STAGE 2: DIMENSI ──────────────────────────────────────────

def build_dim_product(
    df: pd.DataFrame,
    existing_products: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Buat dim_product.

    Logic HPP Source of Truth:
    - Jika existing_products (dari Supabase) diberikan:
        → SKU yang sudah ada: pakai HPP dari Supabase (tidak ditimpa)
        → SKU baru: pakai DEFAULT_HPP (0), tandai untuk diisi manual
    - Jika existing_products tidak diberikan (mode offline):
        → Semua produk pakai DEFAULT_HPP
    """
    unique_skus = (
        df[["sku_sintetis", "Nama Produk", "Nama Variasi"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim = pd.DataFrame({
        "sku": unique_skus["sku_sintetis"],
        "product_name": unique_skus["Nama Produk"],
        "product_variation": unique_skus["Nama Variasi"],
        "hpp": DEFAULT_HPP,
    })

    # ── HPP Source of Truth ─────────────────────────────────
    if existing_products is not None and not existing_products.empty:
        # Build lookup: sku → hpp dari Supabase
        hpp_lookup = existing_products.set_index("sku")["hpp"].to_dict()

        def resolve_hpp(sku: str) -> int:
            if sku in hpp_lookup:
                return hpp_lookup[sku]          # ← pakai HPP Supabase
            return DEFAULT_HPP                  # ← produk baru, set 0

        dim["hpp"] = dim["sku"].apply(resolve_hpp)

        n_existing = dim["sku"].isin(hpp_lookup).sum()
        n_new = len(dim) - n_existing
        print(f"[OK] dim_product: {n_existing} SKU lama (HPP preserved), {n_new} SKU baru (HPP={DEFAULT_HPP})")
    else:
        print(f"[OK] dim_product: {len(dim)} SKU (mode offline, HPP={DEFAULT_HPP})")

    # Tambah product_id untuk kebutuhan join lokal
    dim.insert(0, "product_id", range(1, len(dim) + 1))
    return dim


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    unique = df[["Username (Pembeli)"]].drop_duplicates().reset_index(drop=True)
    dim = pd.DataFrame({
        "customer_id": range(1, len(unique) + 1),
        "customer_username": unique["Username (Pembeli)"],
    })
    print(f"[OK] dim_customer: {len(dim)} pelanggan unik")
    return dim


def build_dim_location(df: pd.DataFrame) -> pd.DataFrame:
    unique = (
        df[["Kota/Kabupaten", "Provinsi"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim = pd.DataFrame({
        "location_id": range(1, len(unique) + 1),
        "city": unique["Kota/Kabupaten"],
        "province": unique["Provinsi"],
    })
    print(f"[OK] dim_location: {len(dim)} lokasi unik")
    return dim


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    dim_date: 1 baris per HARI unik (bukan per transaksi).
    Untuk 6 bulan data → ~180 baris = BENAR ✓

    Catatan: dim_date adalah kalender harian, bukan log transaksi.
    fact_order_item yang menyimpan semua 8000+ transaksi.
    """
    unique_dates = (
        df[["Waktu Pesanan Dibuat"]]
        .assign(date_id=df["Waktu Pesanan Dibuat"].dt.strftime("%Y%m%d").astype(int))
        .drop_duplicates(subset=["date_id"])   # ← deduplikasi per HARI
        .reset_index(drop=True)
    )

    dim = pd.DataFrame({
        "date_id": unique_dates["date_id"],
        "tanggal_pesanan": unique_dates["Waktu Pesanan Dibuat"].dt.date,
        "tahun": unique_dates["Waktu Pesanan Dibuat"].dt.year,
        "kuartal": unique_dates["Waktu Pesanan Dibuat"].dt.quarter,
        "bulan": unique_dates["Waktu Pesanan Dibuat"].dt.month,
        "nama_bulan": unique_dates["Waktu Pesanan Dibuat"].dt.month.map(NAMA_BULAN_ID),
        "hari": unique_dates["Waktu Pesanan Dibuat"].dt.day_name().map(NAMA_HARI_ID),
    })

    print(f"[OK] dim_date: {len(dim)} hari unik (kalender harian, bukan per transaksi ✓)")
    return dim


def build_dim_payment(df: pd.DataFrame) -> pd.DataFrame:
    unique = df[["Metode Pembayaran"]].drop_duplicates().reset_index(drop=True)
    dim = pd.DataFrame({
        "payment_id": range(1, len(unique) + 1),
        "payment_method": unique["Metode Pembayaran"],
    })
    print(f"[OK] dim_payment: {len(dim)} metode pembayaran")
    return dim


def build_dim_status(df: pd.DataFrame) -> pd.DataFrame:
    unique = df[["Status Pesanan"]].drop_duplicates().reset_index(drop=True)
    dim = pd.DataFrame({
        "status_id": range(1, len(unique) + 1),
        "order_status": unique["Status Pesanan"],
    })
    print(f"[OK] dim_status: {len(dim)} status pesanan")
    return dim


def build_dim_shipping(df: pd.DataFrame) -> pd.DataFrame:
    unique = df[["Opsi Pengiriman"]].drop_duplicates().reset_index(drop=True)
    dim = pd.DataFrame({
        "shipping_id": range(1, len(unique) + 1),
        "courier_name": unique["Opsi Pengiriman"].str.split("-").str[0].str.strip(),
        "service_type": unique["Opsi Pengiriman"],
    })
    print(f"[OK] dim_shipping: {len(dim)} opsi pengiriman")
    return dim


# ── STAGE 3: FACT TABLE ───────────────────────────────────────

def build_fact_order_item(
    df: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_location: pd.DataFrame,
    dim_payment: pd.DataFrame,
    dim_status: pd.DataFrame,
    dim_shipping: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merakit fact_order_item dengan join semua dimensi.
    Setiap baris = 1 item dalam 1 pesanan.
    """
    fact = df.copy()

    # date_id dari timestamp (untuk join ke dim_date)
    fact["date_id"] = fact["Waktu Pesanan Dibuat"].dt.strftime("%Y%m%d").astype(int)
    
    # Simpan waktu spesifik di fact table agar tidak hilang saat agregasi harian di dim_date
    fact["order_created_at"] = fact["Waktu Pesanan Dibuat"]
    fact["jam"] = fact["Waktu Pesanan Dibuat"].dt.hour

    # Join semua dimensi
    fact = fact.merge(
        dim_product[["product_id", "sku"]],
        left_on="sku_sintetis", right_on="sku", how="left"
    )
    fact = fact.merge(
        dim_customer[["customer_id", "customer_username"]],
        left_on="Username (Pembeli)", right_on="customer_username", how="left"
    )
    fact = fact.merge(
        dim_location[["location_id", "city", "province"]],
        left_on=["Kota/Kabupaten", "Provinsi"], right_on=["city", "province"], how="left"
    )
    fact = fact.merge(
        dim_payment[["payment_id", "payment_method"]],
        left_on="Metode Pembayaran", right_on="payment_method", how="left"
    )
    fact = fact.merge(
        dim_status[["status_id", "order_status"]],
        left_on="Status Pesanan", right_on="order_status", how="left"
    )
    fact = fact.merge(
        dim_shipping[["shipping_id", "service_type"]],
        left_on="Opsi Pengiriman", right_on="service_type", how="left"
    )

    # Kolom numerik — parse format IDR Indonesia (titik = ribuan, bukan desimal)
    for col in ["Jumlah", "Harga Awal", "Harga Setelah Diskon", "Total Diskon"]:
        fact[col] = parse_idr_series(fact[col])

    # Debug: print sample nilai untuk validasi
    sample = fact[["Harga Awal", "Harga Setelah Diskon"]].head(3)
    print(f"[DEBUG] Sample harga setelah parse: {sample.to_dict('records')}")

    # Kalkulasi metrik & flags
    fact["valid_item_revenue"] = (fact["Jumlah"] * fact["Harga Setelah Diskon"]).astype(int)
    fact["is_completed"] = np.where(
        fact["Status Pesanan"].str.lower() == "selesai", 1, 0
    )
    fact["is_cancelled"] = np.where(
        fact["Status Pesanan"].str.lower().isin(["batal", "pengembalian", "dibatalkan"]),
        1, 0
    )

    # Susun kolom sesuai schema Supabase
    fact_order_item = pd.DataFrame({
        "order_id": fact["No. Pesanan"],
        "date_id": fact["date_id"],
        "product_id": fact["product_id"],
        "customer_id": fact["customer_id"],
        "payment_id": fact["payment_id"],
        "location_id": fact["location_id"],
        "status_id": fact["status_id"],
        "shipping_id": fact["shipping_id"],
        "quantity": fact["Jumlah"].astype(int),
        "original_price": fact["Harga Awal"].astype(int),
        "discounted_price": fact["Harga Setelah Diskon"].astype(int),
        "total_discount": fact["Total Diskon"].astype(int),
        "valid_item_revenue": fact["valid_item_revenue"],
        "is_completed": fact["is_completed"],
        "is_cancelled": fact["is_cancelled"],
        "order_created_at": fact["order_created_at"],
        "jam": fact["jam"],
    })

    print(f"[OK] fact_order_item: {len(fact_order_item)} baris transaksi")
    return fact_order_item


# ── ENTRYPOINT UTAMA ──────────────────────────────────────────

def run_etl(
    df_raw: pd.DataFrame,
    existing_products: Optional[pd.DataFrame] = None,
) -> dict[str, pd.DataFrame]:
    """
    Jalankan seluruh pipeline ETL.

    Args:
        df_raw: DataFrame mentah dari loader.py
        existing_products: DataFrame dari Supabase dim_product (opsional)
                           Jika None → mode offline (semua HPP = DEFAULT_HPP)

    Returns:
        dict berisi semua 8 tabel siap upload:
        {
            "dim_product", "dim_customer", "dim_location",
            "dim_date", "dim_payment", "dim_status", "dim_shipping",
            "fact_order_item"
        }
    """
    print("=" * 50)
    print("DataBuddy ETL Pipeline — Shopee Data")
    print("=" * 50)

    # Stage 1: Cleaning
    df = clean_raw(df_raw)

    # Stage 2: Dimensi
    dim_product  = build_dim_product(df, existing_products)
    dim_customer = build_dim_customer(df)
    dim_location = build_dim_location(df)
    dim_date     = build_dim_date(df)
    dim_payment  = build_dim_payment(df)
    dim_status   = build_dim_status(df)
    dim_shipping = build_dim_shipping(df)

    # Stage 3: Fakta
    fact = build_fact_order_item(
        df, dim_product, dim_customer, dim_location,
        dim_payment, dim_status, dim_shipping
    )

    print("=" * 50)
    print("[SELESAI] ETL berhasil! Semua 8 tabel siap.")
    print("=" * 50)

    return {
        "dim_product": dim_product,
        "dim_customer": dim_customer,
        "dim_location": dim_location,
        "dim_date": dim_date,
        "dim_payment": dim_payment,
        "dim_status": dim_status,
        "dim_shipping": dim_shipping,
        "fact_order_item": fact,
    }
