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
    """Ambil tabel ETL dari Streamlit session state."""
    import streamlit as st
    return st.session_state.get("etl_tables", None)


def build_master(tables: dict) -> pd.DataFrame:
    """
    Join semua tabel menjadi satu DataFrame master untuk analisis.
    Ini adalah 'denormalized view' dari star schema.
    """
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
