"""
core/ml_engine.py — Modul Khusus Pemrosesan Machine Learning
Berisi logic tingkat lanjut untuk prediksi (forecasting), segmentasi (clustering), dan deteksi anomali pada data Shopee.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
# Import library ML sesuai kebutuhan di masa depan, contoh:
# from sklearn.cluster import KMeans
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

class MLEngine:
    """
    Mesin pemroses Machine Learning untuk DataBuddy.
    Menangani tugas-tugas prediktif dan analitik lanjutan yang tidak bisa 
    ditangani oleh query SQL biasa atau agregasi pandas sederhana.
    """
    def __init__(self, df_master: pd.DataFrame):
        """
        Inisialisasi ML Engine dengan data master (dari AnalyticsEngine).
        
        Args:
            df_master (pd.DataFrame): Dataframe gabungan (fakta + dimensi) yang siap pakai.
        """
        self.df = df_master.copy() if df_master is not None else pd.DataFrame()

    def market_basket_analysis(self, min_support: float = 0.01, min_confidence: float = 0.20) -> Dict[str, Any]:
        """
        Menjalankan Market Basket Analysis (Association Rule Mining) menggunakan Apriori.
        Mencari kombinasi produk yang sering dibeli bersamaan untuk keperluan Bundling.
        """
        if self.df.empty:
            return {"error": "Data kosong."}
            
        # 1. Filter hanya transaksi Selesai
        df_valid = self.df[self.df["order_status"] == "Selesai"].copy()
        if df_valid.empty:
            return {"error": "Tidak ada data transaksi Selesai."}

        # 2. Buat kolom product_item (HANYA Nama Produk, abaikan variasi untuk cross-selling bersih)
        df_valid["product_item"] = df_valid["product_name"]
        
        # 3. Buat Basket Transaction (List of items per order_id)
        basket_series = df_valid.groupby("order_id")["product_item"].apply(lambda x: list(set(x)))
        basket_df = basket_series.reset_index()
        basket_df.columns = ["order_id", "items"]
        
        # Hanya gunakan order yang beli lebih dari 1 macam barang
        basket_df["jumlah_item"] = basket_df["items"].apply(len)
        multi_item_basket = basket_df[basket_df["jumlah_item"] >= 2].copy()
        
        total_transactions = len(basket_df)
        analyzed_transactions = len(multi_item_basket)
        
        if analyzed_transactions == 0:
            return {"error": "Tidak ada transaksi dengan lebih dari 1 item."}

        # 4. One-Hot Encoding
        transactions = multi_item_basket["items"].tolist()
        te = TransactionEncoder()
        te_array = te.fit(transactions).transform(transactions)
        basket_encoded = pd.DataFrame(te_array, columns=te.columns_)

        # 5. Apriori - Cari Frequent Itemsets
        # Kita coba beberapa level support secara bertahap jika min_support gagal
        support_levels = [min_support, 0.005, 0.003, 0.001]
        frequent_itemsets = pd.DataFrame()
        used_support = min_support
        
        for supp in support_levels:
            try:
                temp_itemsets = apriori(basket_encoded, min_support=supp, use_colnames=True)
                if len(temp_itemsets) > 0:
                    frequent_itemsets = temp_itemsets
                    used_support = supp
                    break
            except Exception:
                continue

        if frequent_itemsets.empty:
            return {"error": "Tidak ditemukan frequent itemsets yang memenuhi kriteria support."}

        # 6. Association Rules
        try:
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        except Exception:
            rules = pd.DataFrame()

        if rules.empty:
            return {"error": "Tidak ada aturan asosiasi (rules) yang memenuhi batas confidence."}

        # Filter Lift > 1 (Hanya yang benar-benar berhubungan kuat)
        rules = rules[rules["lift"] > 1].copy()
        if rules.empty:
            return {"error": "Tidak ada aturan asosiasi dengan Lift > 1."}

        # Sort dan Format output
        rules = rules.sort_values(["lift", "confidence", "support"], ascending=False).reset_index(drop=True) # type: ignore
        
        rules["antecedents"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
        rules["consequents"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
        
        # Ambil kolom yang diperlukan
        rules_clean = rules[["antecedents", "consequents", "support", "confidence", "lift"]].copy()
        
        # Hitung metrics performa model
        avg_confidence = rules_clean["confidence"].mean()
        avg_lift = rules_clean["lift"].mean()
        total_rules = len(rules_clean)
        
        return {
            "success": True,
            "rules": rules_clean,
            "metrics": {
                "total_transactions": total_transactions,
                "analyzed_transactions": analyzed_transactions,
                "used_support": used_support,
                "total_rules": total_rules,
                "avg_confidence": avg_confidence,
                "avg_lift": avg_lift
            }
        }

    def rfm_segmentation(self) -> pd.DataFrame:
        """
        Sistem Pakar (Rule-Based AI) untuk Segmentasi Pelanggan (Loyalty Tier).
        Menggunakan Forward Chaining berdasarkan histori transaksi (Frekuensi & Nominal).
        """
        if self.df.empty:
            return pd.DataFrame()
            
        print("[ML Engine] Menjalankan Expert System Segmentation...")
        
        # 1. Filter pesanan sukses
        df_valid = self.df[self.df["is_completed"] == 1].copy()
        if df_valid.empty:
            return pd.DataFrame()
            
        # 2. Hapus duplikat invoice (order_id) untuk perhitungan frekuensi yang tepat
        # Pakai customer_username jika ada, jika tidak pakai customer_id
        cust_col = "customer_username" if "customer_username" in df_valid.columns else "customer_id"
        
        df_unique_orders = df_valid.drop_duplicates(subset=["order_id"]) # type: ignore
        
        # 3. Agregasi data per pelanggan
        customer_stats = df_unique_orders.groupby(cust_col).agg(
            Frekuensi_Order=("order_id", "count"),
            Total_Belanja=("valid_item_revenue", "sum")
        ).reset_index()
        
        # 4. Inference Engine (Forward Chaining Rules)
        def inference_engine(row):
            freq = row["Frekuensi_Order"]
            monetary = row["Total_Belanja"]
            
            # Rule 1: Super VIP (Target B2B/Kafe - 1% dari Omzet 300Jt)
            if freq >= 5 and monetary >= 3_000_000:
                return pd.Series([
                    "Super VIP",
                    "Prioritas Packing #1. VIP Direct Order WA khusus B2B/Grosir.",
                    f"Sangat loyal ({freq}x) & value setara agen (Rp {monetary:,.0f})."
                ])
            # Rule 2: Loyal (Konsumen Rutin)
            elif freq >= 3 and monetary >= 500_000:
                return pd.Series([
                    "Loyal",
                    "Prioritas Packing #2. Flyer ajakan Restock via WA.",
                    f"Pecandu kopi rutin ({freq}x) (Rp {monetary:,.0f})."
                ])
            # Rule 3: Review Manual (Sultan Dadakan / Kafe Baru Coba-Coba)
            elif freq == 1 and monetary >= 1_000_000:
                return pd.Series([
                    "Review Manual",
                    "Follow up manual segera (Potensi kafe baru atau penipuan COD).",
                    f"Baru 1x beli langsung borong (Rp {monetary:,.0f})."
                ])
            # Rule 4: Reguler
            elif freq <= 2:
                return pd.Series([
                    "Reguler",
                    "Proses antrean standar.",
                    "Konsumen standar/baru."
                ])
            # Fallback
            else:
                return pd.Series([
                    "Review Manual", 
                    "Cek histori pesanan", 
                    f"Tidak standar (Freq: {freq}x, Nominal: Rp {monetary:,.0f})"
                ])
                
        # 5. Terapkan rules ke dataframe
        customer_stats[["Tier_Loyalitas", "Rekomendasi_Tindakan", "Alasan"]] = customer_stats.apply(inference_engine, axis=1) # type: ignore
        
        # 6. Sort berdasarkan Total Belanja untuk kemudahan UI
        customer_stats = customer_stats.sort_values("Total_Belanja", ascending=False).reset_index(drop=True)
        
        return customer_stats
        
    def forecast_sales(self, periods: int = 7) -> pd.DataFrame:
        """
        [Template] Prediksi Penjualan (Sales Forecasting).
        Memprediksi omzet penjualan n periode ke depan.
        
        Args:
            periods (int): Jumlah hari/bulan ke depan yang akan diprediksi.
            
        Returns:
            pd.DataFrame: Dataframe berisi tanggal masa depan dan prediksi revenue.
        """
        if self.df.empty:
            return pd.DataFrame()
            
        # TODO: Implementasi Time Series Forecasting (misal: ARIMA / Facebook Prophet / XGBoost)
        print(f"[ML Engine] Memprediksi penjualan untuk {periods} periode ke depan...")
        return pd.DataFrame()

    def detect_anomalies(self) -> pd.DataFrame:
        """
        [Template] Deteksi Anomali.
        Mencari data transaksi yang aneh/tidak wajar (fraud, typo harga ekstrim, dsb).
        
        Returns:
            pd.DataFrame: Data transaksi yang terdeteksi sebagai anomali.
        """
        if self.df.empty:
            return pd.DataFrame()
            
        # TODO: Implementasi Anomaly Detection (misal: Isolation Forest atau DBSCAN)
        print("[ML Engine] Mendeteksi anomali transaksi...")
        return pd.DataFrame()

    def product_recommendation(self, customer_id: str) -> List[str]:
        """
        [Template] Rekomendasi Produk (Market Basket Analysis / Collaborative Filtering).
        Memberikan rekomendasi produk apa yang cocok ditawarkan ke customer tertentu.
        
        Args:
            customer_id (str): ID Pelanggan
            
        Returns:
            List[str]: Daftar nama produk/SKU rekomendasi
        """
        if self.df.empty:
            return []
            
        # TODO: Implementasi sistem rekomendasi
        print(f"[ML Engine] Mengambil rekomendasi produk untuk customer: {customer_id}")
        return []

    def revenue_forecasting(self, forecast_days: int = 30) -> Dict:
        """
        Memprediksi omzet (revenue) harian untuk N hari ke depan menggunakan
        Holt-Winters Exponential Smoothing.
        """
        if self.df.empty:
            return {"error": "Data kosong."}
            
        # 1. Siapkan data harian (omzet dari transaksi Selesai)
        df_valid = self.df[self.df["order_status"] == "Selesai"].copy()
        if df_valid.empty:
            return {"error": "Tidak ada data transaksi Selesai."}
            
        # Group by tanggal_pesanan (tanggal saja, tanpa jam)
        df_valid["tanggal"] = pd.to_datetime(df_valid["order_created_at"])
        df_valid["tanggal"] = df_valid["tanggal"].dt.floor("D") # type: ignore
        daily_revenue = df_valid.groupby("tanggal")["valid_item_revenue"].sum().reset_index()
        
        # Urutkan berdasarkan waktu
        daily_revenue = daily_revenue.sort_values("tanggal").set_index("tanggal")
        
        # Isi tanggal yang bolong dengan 0 (karena tidak ada penjualan hari itu)
        all_days = pd.date_range(start=daily_revenue.index.min(), end=daily_revenue.index.max(), freq="D")
        daily_revenue = daily_revenue.reindex(all_days, fill_value=0)
        
        if len(daily_revenue) < 14:
            return {"error": "Data harian kurang dari 14 hari. Prediksi tidak dapat diandalkan."}
            
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            from sklearn.metrics import mean_absolute_percentage_error
            
            # Gunakan additive trend & seasonality (mingguan = 7 hari)
            seasonal_periods = 7 if len(daily_revenue) >= 21 else None
            trend_type = "add"
            seasonal_type = "add" if seasonal_periods else None
            
            # 2. Fit Model
            series = daily_revenue["valid_item_revenue"].astype(float)
            model = ExponentialSmoothing(
                series,
                trend=trend_type,
                seasonal=seasonal_type,
                seasonal_periods=seasonal_periods,
                initialization_method="estimated"
            )
            fit_model = model.fit()
            
            # 3. Evaluasi (Prediksi di masa lalu untuk menghitung error)
            fitted_values = fit_model.fittedvalues
            actual_safe = series.replace(0, 1)
            mape = mean_absolute_percentage_error(actual_safe, fitted_values)
            
            # 4. Prediksi Masa Depan (Forecast)
            forecast = fit_model.forecast(forecast_days)
            forecast = forecast.apply(lambda x: max(0, x))
            
            history_df = series.reset_index()
            history_df.columns = ["date", "revenue"]
            history_df["type"] = "Actual"
            
            forecast_df = forecast.reset_index()
            forecast_df.columns = ["date", "revenue"]
            forecast_df["type"] = "Forecast"
            
            total_forecast = forecast.sum()
            
            return {
                "history": history_df,
                "forecast": forecast_df,
                "metrics": {
                    "mape_percent": round(mape * 100, 2),
                    "total_forecast": float(total_forecast),
                    "avg_daily_forecast": float(total_forecast / forecast_days),
                    "days": forecast_days,
                    "data_points": len(series)
                }
            }
        except Exception as e:
            return {"error": f"Gagal menjalankan model: {str(e)}"}
