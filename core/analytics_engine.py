"""
core/analytics_engine.py — Query Engine untuk Jawaban Pertanyaan Bisnis
Berisi formula-formula untuk menjawab pertanyaan umum data analyst
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class AnalyticsEngine:
    """
    Engine untuk menjawab pertanyaan bisnis umum yang biasa ditanyakan atasan.
    Semua fungsi return data dalam format yang mudah dibaca manusia + bisa dipakai AI.
    """

    def __init__(self, df_master: pd.DataFrame):
        """
        Args:
            df_master: DataFrame hasil build_master() dari data_manager
                      Pastikan sudah join semua dimensi dan fact tables
        """
        self.df = df_master.copy()

        # Pastikan tipe data benar
        self.df["tanggal_pesanan"] = pd.to_datetime(self.df["tanggal_pesanan"])
        self.df["order_created_at"] = pd.to_datetime(self.df["order_created_at"])

        # Filter hanya completed orders untuk kebanyakan analisis
        self.df_completed = self.df[self.df["is_completed"] == 1].copy()

        # Extract date components
        self.df["tahun"] = self.df["tanggal_pesanan"].dt.year # type: ignore
        self.df["bulan"] = self.df["tanggal_pesanan"].dt.month # type: ignore
        self.df["bulan_nama"] = self.df["tanggal_pesanan"].dt.strftime("%B") # type: ignore
        self.df_completed["tahun"] = self.df_completed["tanggal_pesanan"].dt.year # type: ignore
        self.df_completed["bulan"] = self.df_completed["tanggal_pesanan"].dt.month # type: ignore
        self.df_completed["bulan_nama"] = self.df_completed["tanggal_pesanan"].dt.strftime("%B") # type: ignore

    # ── REVENUE & SALES TREN ───────────────────────────────────────

    def revenue_per_bulan(self, tahun: Optional[int] = None) -> pd.DataFrame:
        """
        Revenue per bulan. Bisa filter tahun tertentu.

        Pertanyaan: "Berapa omzet bulan Januari?", "Omzet bulan ini vs bulan lalu?"
        """
        if tahun:
            df_filtered = self.df_completed[self.df_completed["tahun"] == tahun]
        else:
            df_filtered = self.df_completed

        result = (
            df_filtered.groupby(["tahun", "bulan", "bulan_nama"])
            .agg(
                revenue=("valid_item_revenue", "sum"),
                orders=("order_id", "nunique"),
                qty=("quantity", "sum"),
            )
            .reset_index()
            .sort_values(["tahun", "bulan"])
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    def revenue_bulanan_comparison(self, bulan_a: int, bulan_b: int, tahun: int) -> Dict:
        """
        Bandingkan revenue antara 2 bulan.

        Pertanyaan: "Gimana sih bulan Mei vs April?", "Bulan naik atau turun?"
        """
        df_bulan_a = self.df_completed[
            (self.df_completed["bulan"] == bulan_a) & (self.df_completed["tahun"] == tahun)
        ]
        df_bulan_b = self.df_completed[
            (self.df_completed["bulan"] == bulan_b) & (self.df_completed["tahun"] == tahun)
        ]

        if df_bulan_a.empty and df_bulan_b.empty:
            raise ValueError(f"Data untuk bulan {bulan_a} dan {bulan_b} tidak tersedia di database.")
        elif df_bulan_a.empty:
            raise ValueError(f"Data untuk bulan {bulan_a} tidak tersedia di database.")
        elif df_bulan_b.empty:
            raise ValueError(f"Data untuk bulan {bulan_b} tidak tersedia di database.")

        rev_a = df_bulan_a["valid_item_revenue"].sum()
        rev_b = df_bulan_b["valid_item_revenue"].sum()

        growth = ((rev_b - rev_a) / rev_a * 100) if rev_a > 0 else 0
        growth_abs = rev_b - rev_a

        return {
            "bulan_a": bulan_a,
            "bulan_b": bulan_b,
            "revenue_a": rev_a,
            "revenue_b": rev_b,
            "growth_percent": round(growth, 2),
            "growth_absolute": growth_abs,
            "insight": "Naik" if growth > 0 else "Turun",
        }

    # ── PRODUCT PERFORMANCE ───────────────────────────────────────

    def produk_terlaris_bulan(self, bulan: int, tahun: int, top_n: int = 10) -> pd.DataFrame:
        """
        Daftar produk paling laku di bulan tertentu.

        Pertanyaan: "Produk apa yang paling larus bulan Mei?", "Top 5 produk bulan ini?"
        """
        df_filtered = self.df_completed[
            (self.df_completed["bulan"] == bulan) & (self.df_completed["tahun"] == tahun)
        ]

        result = (
            df_filtered.groupby(["product_name", "product_variation"])
            .agg(
                qty=("quantity", "sum"),
                revenue=("valid_item_revenue", "sum"),
                orders=("order_id", "nunique"),
            )
            .reset_index()
            .sort_values("qty", ascending=False)
            .head(top_n)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    def produk_tidak_laris(self, bulan: int, tahun: int, bottom_n: int = 10, min_orders: int = 2) -> pd.DataFrame:
        """
        Daftar produk yang TIDAK laris (jual sedikit).

        Pertanyaan: "Produk apa yang ga laris?", "Produk yang perlu promo apa?"
        """
        df_filtered = self.df_completed[
            (self.df_completed["bulan"] == bulan) & (self.df_completed["tahun"] == tahun)
        ]

        # Filter produk yang punya minimal beberapa order (biar fair)
        product_orders = df_filtered.groupby("product_name")["order_id"].nunique()
        valid_products = product_orders[product_orders >= min_orders].index

        df_filtered = df_filtered[df_filtered["product_name"].isin(valid_products)]

        result = (
            df_filtered.groupby(["product_name", "product_variation"])
            .agg(
                qty=("quantity", "sum"),
                revenue=("valid_item_revenue", "sum"),
                orders=("order_id", "nunique"),
            )
            .reset_index()
            .sort_values("qty", ascending=True)
            .head(bottom_n)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    def produk_performance_all_time(self, top_n: int = 20) -> pd.DataFrame:
        """
        Produk paling laku sepanjang waktu.

        Pertanyaan: "Produk best seller sepanjang masa?", "Produk apa yang paling banyak terjual?"
        """
        result = (
            self.df_completed.groupby(["product_name", "product_variation"])
            .agg(
                qty=("quantity", "sum"),
                revenue=("valid_item_revenue", "sum"),
                orders=("order_id", "nunique"),
                first_order=("order_created_at", "min"),
                last_order=("order_created_at", "max"),
            )
            .reset_index()
            .sort_values("qty", ascending=False)
            .head(top_n)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    # ── CUSTOMER ANALYTICS ───────────────────────────────────────

    def top_customers_bulan(self, bulan: int, tahun: int, top_n: int = 10) -> pd.DataFrame:
        """
        Top customers di bulan tertentu.

        Pertanyaan: "Siapa customer paling besar bulan ini?", "Top 5 customer bulan Mei?"
        """
        df_filtered = self.df_completed[
            (self.df_completed["bulan"] == bulan) & (self.df_completed["tahun"] == tahun)
        ]

        result = (
            df_filtered.groupby("customer_username")
            .agg(
                total_spent=("valid_item_revenue", "sum"),
                total_orders=("order_id", "nunique"),
                total_items=("quantity", "sum"),
            )
            .reset_index()
            .sort_values("total_spent", ascending=False)
            .head(top_n)
        )

        result["total_spent_fmt"] = result["total_spent"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    def customer_retention(self) -> Dict:
        """
        Statistik customer retention.

        Pertanyaan: "Berapa banyak customer balik lagi?", "Repeat buyer rate berapa?"
        """
        customer_orders = self.df_completed.groupby("customer_username")["order_id"].nunique()
        total_customers = len(customer_orders)
        repeat_buyers = (customer_orders > 1).sum()
        one_time_buyers = total_customers - repeat_buyers

        return {
            "total_customers": total_customers,
            "repeat_buyers": repeat_buyers,
            "one_time_buyers": one_time_buyers,
            "repeat_rate": round(repeat_buyers / total_customers * 100, 2) if total_customers > 0 else 0,
        }

    # ── GEOGRAPHIC ANALYTICS ────────────────────────────────────

    def performance_per_provinsi(self, bulan: Optional[int] = None, tahun: Optional[int] = None) -> pd.DataFrame:
        """
        Performance per provinsi. Bisa filter bulan/tahun.

        Pertanyaan: "Provinsi mana yang paling besar?", "Performance per daerah gimana?"
        """
        if bulan and tahun:
            df_filtered = self.df_completed[
                (self.df_completed["bulan"] == bulan) & (self.df_completed["tahun"] == tahun)
            ]
        elif tahun:
            df_filtered = self.df_completed[self.df_completed["tahun"] == tahun]
        else:
            df_filtered = self.df_completed

        result = (
            df_filtered.groupby("province")
            .agg(
                revenue=("valid_item_revenue", "sum"),
                orders=("order_id", "nunique"),
                customers=("customer_id", "nunique"),
            )
            .reset_index()
            .sort_values("revenue", ascending=False)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    def performance_per_kota(self, top_n: int = 20) -> pd.DataFrame:
        """
        Top kota/kabupaten berdasarkan revenue.

        Pertanyaan: "Kota mana yang paling besar?", "Top 10 kota dengan omzet tertinggi?"
        """
        result = (
            self.df_completed.groupby(["city", "province"])
            .agg(
                revenue=("valid_item_revenue", "sum"),
                orders=("order_id", "nunique"),
                customers=("customer_id", "nunique"),
            )
            .reset_index()
            .sort_values("revenue", ascending=False)
            .head(top_n)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    # ── TIME-BASED ANALYTICS ─────────────────────────────────────

    def best_jam_penjualan(self) -> pd.DataFrame:
        """
        Jam-jam paling ramai order.

        Pertanyaan: "Jam berapa paling ramai order?", "Prime time kapan?"
        """
        result = (
            self.df.groupby("jam")
            .agg(
                orders=("order_id", "nunique"),
                revenue=("valid_item_revenue", "sum"),
                qty=("quantity", "sum"),
            )
            .reset_index()
            .sort_values("orders", ascending=False)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    def best_hari_penjualan(self) -> pd.DataFrame:
        """
        Hari paling ramai order.

        Pertanyaan: "Hari apa paling ramai?", "Weekday atau weekend lebih laku?"
        """
        hari_order = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

        result = (
            self.df.groupby("hari")
            .agg(
                orders=("order_id", "nunique"),
                revenue=("valid_item_revenue", "sum"),
                qty=("quantity", "sum"),
            )
            .reset_index()
        )

        # Urutkan berdasarkan hari_order
        result["hari_num"] = result["hari"].map(lambda x: hari_order.index(x) if x in hari_order else 999)
        result = result.sort_values("hari_num")
        result = result.drop("hari_num", axis=1)

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    # ── PAYMENT & SHIPPING ───────────────────────────────────────

    def performance_per_payment_method(self) -> pd.DataFrame:
        """
        Performance per metode pembayaran.

        Pertanyaan: "Metode pembayaran apa yang paling dipakai?", "COD vs transfer bagaimana?"
        """
        result = (
            self.df_completed.groupby("payment_method")
            .agg(
                orders=("order_id", "nunique"),
                revenue=("valid_item_revenue", "sum"),
                avg_order_value=("valid_item_revenue", "mean"),
            )
            .reset_index()
            .sort_values("orders", ascending=False)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        result["aov_fmt"] = result["avg_order_value"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    def performance_per_courier(self) -> pd.DataFrame:
        """
        Performance per ekspedisi/kurir.

        Pertanyaan: "Ekspedisi mana yang paling dipakai?", "JNE vs J&T vs Shopee?"
        """
        result = (
            self.df_completed.groupby("courier_name")
            .agg(
                orders=("order_id", "nunique"),
                revenue=("valid_item_revenue", "sum"),
            )
            .reset_index()
            .sort_values("orders", ascending=False)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")
        return result

    # ── ORDER STATUS ANALYTICS ───────────────────────────────────

    def order_status_summary(self) -> pd.DataFrame:
        """
        Ringkasan status pesanan.

        Pertanyaan: "Berapa banyak order yang cancel?", "Completion rate berapa?"
        """
        result = (
            self.df.groupby("order_status")
            .agg(
                orders=("order_id", "nunique"),
                revenue=("valid_item_revenue", "sum"),
            )
            .reset_index()
            .sort_values("orders", ascending=False)
        )

        result["revenue_fmt"] = result["revenue"].apply(lambda x: f"Rp {x:,.0f}")

        # Hitung completion rate
        total = result["orders"].sum()
        completed = result[result["order_status"].str.lower() == "selesai"]["orders"].sum()
        result["completion_rate"] = f"{round(completed / total * 100, 1)}%" if total > 0 else "0%"

        return result

    # ── COMPREHENSIVE SUMMARY ─────────────────────────────────────

    def monthly_summary(self, bulan: int, tahun: int) -> Dict:
        """
        Ringkasan lengkap 1 bulan. All-in-one untuk reporting ke atasan.

        Pertanyaan: "Gimana performa bulan ini?", "Summary bulan Mei gimana?"
        """
        df_filtered = self.df_completed[
            (self.df_completed["bulan"] == bulan) & (self.df_completed["tahun"] == tahun)
        ]

        total_revenue = df_filtered["valid_item_revenue"].sum()
        total_orders = df_filtered["order_id"].nunique()
        total_customers = df_filtered["customer_id"].nunique()
        total_qty = df_filtered["quantity"].sum()
        aov = total_revenue / total_orders if total_orders > 0 else 0

        # Top product
        top_product = (
            df_filtered.groupby("product_name")["quantity"]
            .sum()
            .idxmax() if not df_filtered.empty else "N/A"
        )

        # Top city
        top_city = (
            df_filtered.groupby("city")["valid_item_revenue"]
            .sum()
            .idxmax() if not df_filtered.empty else "N/A"
        )

        # Payment method distribution
        payment_dist = df_filtered.groupby("payment_method")["order_id"].nunique().to_dict()

        return {
            "bulan": bulan,
            "tahun": tahun,
            "total_revenue": int(total_revenue),
            "total_revenue_fmt": f"Rp {total_revenue:,.0f}",
            "total_orders": total_orders,
            "total_customers": total_customers,
            "total_qty": int(total_qty),
            "aov": int(aov),
            "aov_fmt": f"Rp {aov:,.0f}",
            "top_product": top_product,
            "top_city": top_city,
            "payment_distribution": payment_dist,
        }

    def compare_two_months(self, bulan1: int, bulan2: int, tahun: int) -> Dict:
        """
        Bandingkan 2 bulan secara lengkap.

        Pertanyaan: "Bulan ini vs bulan lalu gimana?", "April vs May comparison?"
        """
        summary1 = self.monthly_summary(bulan1, tahun)
        summary2 = self.monthly_summary(bulan2, tahun)

        rev_growth = ((summary2["total_revenue"] - summary1["total_revenue"]) /
                     summary1["total_revenue"] * 100) if summary1["total_revenue"] > 0 else 0
        orders_growth = ((summary2["total_orders"] - summary1["total_orders"]) /
                         summary1["total_orders"] * 100) if summary1["total_orders"] > 0 else 0

        return {
            "bulan1": summary1,
            "bulan2": summary2,
            "revenue_growth_percent": round(rev_growth, 2),
            "orders_growth_percent": round(orders_growth, 2),
            "insight": "Positif" if rev_growth > 0 else "Negatif",
        }


# ── HELPER FUNCTIONS ───────────────────────────────────────────

def format_rupiah(angka: int) -> str:
    """Format integer ke Rupiah."""
    return f"Rp {angka:,.0f}"


def get_bulan_name(bulan: int) -> str:
    """Konversi angka bulan ke nama."""
    bulan_names = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    return bulan_names.get(bulan, str(bulan))
