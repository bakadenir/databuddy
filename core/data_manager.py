"""
core/data_manager.py — Query engine untuk dashboard
Bekerja dengan data dari session state (lokal) atau Supabase (nanti)

Semua fungsi menerima dict `tables` yang berisi 8 DataFrame hasil ETL.
Nanti tinggal ganti source-nya ke Supabase query tanpa ubah logika dashboard.
"""

import pandas as pd
import numpy as np
from typing import Optional


def get_tables() -> Optional[dict]:
    """Ambil tabel ETL dari Streamlit session state, atau dari Supabase jika belum ada."""
    import streamlit as st
    from core.config import config

    tables = st.session_state.get("etl_tables", None)
    if tables and isinstance(tables, dict) and not tables.get("fact_order_item", pd.DataFrame()).empty:
        return tables

    # Fetch dari Supabase jika dikonfigurasi
    if config.has_supabase:
        try:
            from core.database import get_supabase_client
            client = get_supabase_client()

            with st.spinner("Mendownload data dari Supabase (ini mungkin memakan waktu sebentar)..."):
                fetched_tables = fetch_all_supabase_tables(client)

                # Simpan di session_state supaya tidak diload ulang setiap klik
                if not fetched_tables["fact_order_item"].empty:
                    st.session_state["etl_tables"] = fetched_tables
                    return fetched_tables

        except Exception as e:
            st.error(f"Gagal mengambil data dari Supabase: {e}")

    return None


def fetch_all_supabase_tables(client) -> dict:
    """Fetch semua tabel dari Supabase (reusable function)."""
    fetched_tables = {}
    tables_to_fetch = [
        "dim_product", "dim_customer", "dim_location",
        "dim_date", "dim_payment", "dim_status", "dim_shipping",
        "fact_order_item"
    ]

    for table_name in tables_to_fetch:
        data = []
        chunk_size = 1000
        start = 0
        while True:
            res = client.table(table_name).select("*").range(start, start + chunk_size - 1).execute()
            if not res.data:
                break
            data.extend(res.data)
            if len(res.data) < chunk_size:
                break
            start += chunk_size

        fetched_tables[table_name] = pd.DataFrame(data) if data else pd.DataFrame()

    return fetched_tables


def prefetch_supabase() -> None:
    """
    Preload data dari Supabase ke session_state secara silent.
    Menggunakan deferred execution: UI render dulu, baru load di background.

    Cara kerja:
    1. Panggil fungsi ini di atas script
    2. Fungsi akan defer ke rerun berikutnya dengan st.session_state flag
    3. UI sudah ter-render di rerun pertama
    4. Data di-load di rerun kedua (silent, tanpa spinner)
    """
    import streamlit as st
    from core.config import config

    # Cek apakah sudah pernah prefetch (berhasil atau gagal)
    if st.session_state.get("supabase_prefetch_done", False):
        return

    # Cek apakah data sudah ada dari ETL lokal
    if st.session_state.get("etl_tables") is not None:
        st.session_state["supabase_prefetch_done"] = True
        return

    # Tandai bahwa kita mau prefetch di rerun berikutnya
    if not st.session_state.get("supabase_prefetch_scheduled", False):
        st.session_state["supabase_prefetch_scheduled"] = True
        # Trigger rerun - UI sudah ter-render sebelum ini dipanggil
        st.rerun()
        return

    # Ini rerun kedua - lakukan fetch sebenarnya
    st.session_state["supabase_prefetch_done"] = True

    if not config.has_supabase:
        return

    try:
        from core.database import get_supabase_client
        client = get_supabase_client()

        # Fetch silent tanpa spinner
        fetched_tables = fetch_all_supabase_tables(client)

        if not fetched_tables["fact_order_item"].empty:
            st.session_state["etl_tables"] = fetched_tables
    except Exception:
        # Silent fail - tidak boleh break app
        pass


def build_master(tables: dict) -> pd.DataFrame:
    """
    Join semua tabel menjadi satu DataFrame master untuk analisis.
    Ini adalah 'denormalized view' dari star schema.
    """
    # 🚀 CACHE: join hanya sekali, simpan di session_state
    import streamlit as st
    if "df_master" in st.session_state and st.session_state["df_master"] is not None:
        return st.session_state["df_master"]

    fact = tables["fact_order_item"].copy()
    
    # Konversi tipe
    for col in ["quantity", "original_price", "discounted_price",
                "total_discount", "valid_item_revenue"]:
        fact[col] = pd.to_numeric(fact[col], errors="coerce")
        fact[col] = fact[col].fillna(0)

    for col in ["is_completed", "is_cancelled"]:
        fact[col] = pd.to_numeric(fact[col], errors="coerce")
        fact[col] = fact[col].fillna(0).astype(int)

    fact["date_id"] = pd.to_numeric(fact["date_id"], errors="coerce")
    fact["product_id"] = pd.to_numeric(fact["product_id"], errors="coerce")
    fact["customer_id"] = pd.to_numeric(fact["customer_id"], errors="coerce")
    fact["payment_id"] = pd.to_numeric(fact["payment_id"], errors="coerce")
    fact["location_id"] = pd.to_numeric(fact["location_id"], errors="coerce")
    fact["status_id"] = pd.to_numeric(fact["status_id"], errors="coerce")
    fact["shipping_id"] = pd.to_numeric(fact["shipping_id"], errors="coerce")

    # Joins
    df = fact.merge(tables["dim_date"],     on="date_id",     how="left")
    df = df.merge(tables["dim_product"],    on="product_id",  how="left")
    df = df.merge(tables["dim_customer"],   on="customer_id", how="left")
    df = df.merge(tables["dim_location"],   on="location_id", how="left")
    df = df.merge(tables["dim_payment"],    on="payment_id",  how="left")
    df = df.merge(tables["dim_status"],     on="status_id",   how="left")
    df = df.merge(tables["dim_shipping"],   on="shipping_id", how="left")

    # Parse tanggal
    df["tanggal_pesanan"] = pd.to_datetime(df["tanggal_pesanan"], errors="coerce")
    df["order_created_at"] = pd.to_datetime(df["order_created_at"], errors="coerce")

    # Simpan di cache biar ganti tab ga join ulang
    st.session_state["df_master"] = df
    return df


# ── KPI ───────────────────────────────────────────────────────

def kpi_overview(df: pd.DataFrame) -> dict:
    completed = df[df["is_completed"] == 1]
    cancelled = df[df["is_cancelled"] == 1]
    total_orders = df["order_id"].nunique()
    completed_orders = completed["order_id"].nunique()

    revenue = completed["valid_item_revenue"].sum()
    aov = revenue / completed_orders if completed_orders > 0 else 0

    return {
        "total_revenue":       int(revenue),
        "total_orders":        total_orders,
        "completed_orders":    completed_orders,
        "cancelled_orders":    cancelled["order_id"].nunique(),
        "total_customers":     df["customer_id"].nunique(),
        "total_products_sold": int(completed["quantity"].sum()),
        "aov":                 int(aov),
        "completion_rate":     round(completed_orders / total_orders * 100, 1) if total_orders > 0 else 0,
    }


# ── SALES TREND ───────────────────────────────────────────────

def sales_trend(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    freq: 'H'=jam, 'D'=harian, 'W'=mingguan, 'ME'=bulanan
    """
    completed = df[df["is_completed"] == 1].copy()
    assert isinstance(completed, pd.DataFrame)
    completed = completed.dropna(subset=["order_created_at"])

    trend = (
        completed.groupby(pd.Grouper(key="order_created_at", freq=freq))
        .agg(
            revenue=("valid_item_revenue", "sum"),
            orders=("order_id", "nunique"),
            qty=("quantity", "sum"),
        )
        .reset_index()
    )
    trend.columns = ["tanggal", "revenue", "orders", "qty"]
    return trend


# ── TOP PRODUK ────────────────────────────────────────────────

def top_products(df: pd.DataFrame, n: int = 15, by: str = "revenue") -> pd.DataFrame:
    completed = df[df["is_completed"] == 1]
    grp = (
        completed.groupby("product_name")
        .agg(
            revenue=("valid_item_revenue", "sum"),
            qty=("quantity", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
    )
    sort_col = "revenue" if by == "revenue" else "qty"
    return grp.nlargest(n, sort_col).reset_index(drop=True)


# ── GEO ───────────────────────────────────────────────────────

def by_province(df: pd.DataFrame) -> pd.DataFrame:
    completed = df[df["is_completed"] == 1]
    return (
        completed.groupby("province")
        .agg(
            revenue=("valid_item_revenue", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def by_city(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    completed = df[df["is_completed"] == 1]
    return (
        completed.groupby(["city", "province"])
        .agg(
            revenue=("valid_item_revenue", "sum"),
            orders=("order_id", "nunique"),
        )
        .reset_index()
        .nlargest(top_n, "revenue")
    )


# ── STATUS PESANAN ────────────────────────────────────────────

def by_status(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("order_status")
        .agg(
            orders=("order_id", "nunique"),
            revenue=("valid_item_revenue", "sum"),
        )
        .reset_index()
        .sort_values("orders", ascending=False)
    )


# ── PAYMENT ───────────────────────────────────────────────────

def by_payment(df: pd.DataFrame) -> pd.DataFrame:
    completed = df[df["is_completed"] == 1]
    return (
        completed.groupby("payment_method")
        .agg(
            orders=("order_id", "nunique"),
            revenue=("valid_item_revenue", "sum"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


# ── HEATMAP JAM × HARI ────────────────────────────────────────

def order_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Matrix: baris=hari, kolom=jam, nilai=jumlah order"""
    DAY_ORDER = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    hm = (
        df.groupby(["hari", "jam"])
        .agg(orders=("order_id", "nunique"))
        .reset_index()
    )
    pivot = hm.pivot(index="hari", columns="jam", values="orders").fillna(0)

    # Urutkan hari
    existing_days = [d for d in DAY_ORDER if d in pivot.index]
    pivot = pivot.reindex(existing_days)

    return pivot


# ── SHIPPING ──────────────────────────────────────────────────

def by_shipping(df: pd.DataFrame) -> pd.DataFrame:
    completed = df[df["is_completed"] == 1]
    return (
        completed.groupby("courier_name")
        .agg(
            orders=("order_id", "nunique"),
            revenue=("valid_item_revenue", "sum"),
        )
        .reset_index()
        .sort_values("orders", ascending=False)
    )


# ── REPEAT BUYER ──────────────────────────────────────────────

def repeat_buyer_stats(df: pd.DataFrame) -> dict:
    completed = df[df["is_completed"] == 1]
    order_counts = completed.groupby("customer_username")["order_id"].nunique()
    repeat = (order_counts > 1).sum()
    total_cust = len(order_counts)
    return {
        "total_customers": total_cust,
        "repeat_buyers":   repeat,
        "one_time_buyers": total_cust - repeat,
        "repeat_rate":     round(repeat / total_cust * 100, 1) if total_cust > 0 else 0,
        "order_counts":    order_counts,
    }
