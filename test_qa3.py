import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from core.database import get_supabase_client
from core.data_manager import fetch_all_supabase_tables, build_master
from core.analytics_engine import AnalyticsEngine

client = get_supabase_client()
tables = fetch_all_supabase_tables(client)
df_master = build_master(tables)

engine = AnalyticsEngine(df_master)
q_lower = "berapa omset di bulan januari?"
combined_q = q_lower + " "

bulan_map = {
    "januari": 1, "jan": 1, "1": 1,
    "februari": 2, "feb": 2, "2": 2,
    "maret": 3, "mar": 3, "3": 3,
    "april": 4, "apr": 4, "4": 4,
    "mei": 5, "may": 5, "5": 5,
    "juni": 6, "jun": 6, "6": 6,
    "juli": 7, "jul": 7, "7": 7,
    "agustus": 8, "aug": 8, "8": 8,
    "september": 9, "sep": 9, "9": 9,
    "oktober": 10, "oct": 10, "okt": 10, "10": 10,
    "november": 11, "nov": 11, "11": 11,
    "desember": 12, "dec": 12, "12": 12
}

bulan_number = None
for bulan_name, bulan_num in bulan_map.items():
    if bulan_name in q_lower and len(bulan_name) > 3:
        bulan_number = bulan_num
        break

if bulan_number is None:
    for bulan_name, bulan_num in bulan_map.items():
        if bulan_name in q_lower:
            bulan_number = bulan_num
            break

print("bulan_number:", bulan_number)

has_revenue = any(keyword in combined_q for keyword in ["omzet", "revenue", "pendapatan", "hasil", "cara", "jualan", "income", "pemasukan"])
print("has_revenue:", has_revenue)

if has_revenue:
    if bulan_number:
        tahun = df_master["tanggal_pesanan"].dt.year.max()
        print("tahun:", tahun)
        result = engine.revenue_per_bulan(tahun=tahun)
        print("result empty?", result.empty)
        if not result.empty:
            bulan_data = result[result["bulan"] == bulan_number]
            print("bulan_data empty?", bulan_data.empty)

