import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules

def generate_rfm_segments(df: pd.DataFrame) -> dict:
    """
    Menghitung RFM (Recency, Frequency, Monetary) dan melakukan K-Means Clustering.
    Mengembalikan dictionary berisi ringkasan cluster.
    """
    # Filter hanya order yang completed
    completed = df[df["is_completed"] == 1].copy()
    
    if completed.empty:
        return {"error": "Tidak ada data transaksi yang selesai untuk dianalisis."}
        
    # Pastikan tipe data datetime
    completed["order_created_at"] = pd.to_datetime(completed["order_created_at"], errors="coerce")
    completed = completed.dropna(subset=["order_created_at"])
    
    # Hitung Recency, Frequency, Monetary per customer
    max_date = completed["order_created_at"].max() + pd.Timedelta(days=1)
    
    rfm = completed.groupby("customer_id").agg(
        Recency=("order_created_at", lambda x: (max_date - x.max()).days),
        Frequency=("order_id", "nunique"),
        Monetary=("valid_item_revenue", "sum")
    ).reset_index()
    
    # Jika pelanggan terlalu sedikit, fallback
    if len(rfm) < 3:
        return {"error": "Data pelanggan terlalu sedikit untuk di-clustering."}
        
    # K-Means Clustering
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[["Recency", "Frequency", "Monetary"]])
    
    # Gunakan 3 cluster (Loyal, Sleeping, New/Regular)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(rfm_scaled)
    
    # Penamaan Cluster Berdasarkan Logika Bisnis
    # Kita hitung rata-rata tiap cluster untuk melabeli
    cluster_stats = rfm.groupby("Cluster").agg(
        R_mean=("Recency", "mean"),
        F_mean=("Frequency", "mean"),
        M_mean=("Monetary", "mean"),
        Count=("customer_id", "count")
    ).reset_index()
    
    # Urutkan berdasarkan Monetary dan Frequency
    cluster_stats = cluster_stats.sort_values(by=["M_mean", "F_mean"], ascending=[False, False])
    
    labels = ["Loyal Customer", "Regular Customer", "Sleeping/At-Risk Customer"]
    label_map = {}
    for i, (_, row) in enumerate(cluster_stats.iterrows()):
        label_map[row["Cluster"]] = labels[i]
        
    rfm["Segment"] = rfm["Cluster"].map(label_map)
    
    # Buat Summary untuk Prompt AI
    summary_list = []
    for segment in labels:
        segment_data = rfm[rfm["Segment"] == segment]
        if not segment_data.empty:
            count = len(segment_data)
            avg_r = int(segment_data["Recency"].mean())
            avg_f = int(segment_data["Frequency"].mean())
            avg_m = int(segment_data["Monetary"].mean())
            summary_list.append(
                f"- **{segment}**: {count} orang. Rata-rata transaksi {avg_f} kali, terakhir belanja rata-rata {avg_r} hari lalu, total kontribusi rata-rata Rp {avg_m:,} per orang."
            )
            
    return {
        "status": "success",
        "raw_rfm": rfm,
        "summary_text": "\n".join(summary_list)
    }

def generate_bundling_rules(df: pd.DataFrame, min_support=0.01, min_lift=1.2) -> dict:
    """
    Mencari aturan asosiasi (Market Basket Analysis) dengan algoritma Apriori.
    """
    completed = df[df["is_completed"] == 1].copy()
    
    if completed.empty:
        return {"error": "Tidak ada data transaksi yang selesai."}
        
    # Asumsikan nama kolom produk adalah 'product_name' (biasanya dari dim_product)
    # Jika tidak ada, gunakan 'product_id' sebagai fallback
    prod_col = "product_name" if "product_name" in completed.columns else "product_id"
    
    # Buat basket: 1 order_id memiliki produk apa saja
    # Grupkan berdasarkan order_id dan product
    basket = completed.groupby(["order_id", prod_col])["quantity"].sum().unstack().reset_index().fillna(0).set_index("order_id")
    
    # Konversi ke binary (1 jika dibeli, 0 jika tidak)
    def encode_units(x):
        if x <= 0: return 0
        if x >= 1: return 1
    basket_sets = basket.map(encode_units)
    
    if basket_sets.empty or basket_sets.shape[1] < 2:
        return {"error": "Data keranjang belanja kurang variatif."}
    
    # Jalankan Apriori
    try:
        frequent_itemsets = apriori(basket_sets, min_support=min_support, use_colnames=True)
        if frequent_itemsets.empty:
            return {"error": "Tidak ada pola pembelian bersamaan yang kuat (coba turunkan min_support)."}
            
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift, num_itemsets=2)
        
        if rules.empty:
            return {"error": "Tidak ada rekomendasi bundling yang signifikan."}
            
        # Urutkan berdasarkan lift dan confidence tertinggi
        rules = rules.sort_values(["lift", "confidence"], ascending=[False, False])
        
        # Ambil Top 5 Aturan untuk AI
        top_rules = rules.head(5)
        
        summary_list = []
        for idx, row in top_rules.iterrows():
            antecedents = ", ".join(list(row['antecedents']))
            consequents = ", ".join(list(row['consequents']))
            confidence = round(row['confidence'] * 100, 1)
            lift = round(row['lift'], 2)
            summary_list.append(
                f"- Jika orang membeli **{antecedents}**, kemungkinannya **{confidence}%** mereka juga akan membeli **{consequents}** (Kekuatan/Lift: {lift}x lipat lebih tinggi dari kebetulan)."
            )
            
        return {
            "status": "success",
            "raw_rules": rules,
            "summary_text": "\n".join(summary_list)
        }
    except Exception as e:
        return {"error": f"Gagal memproses Apriori: {str(e)}"}
