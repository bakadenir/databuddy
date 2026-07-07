import sys
sys.path.append('.')
from core.database import get_supabase_client
from core.data_manager import fetch_all_supabase_tables, build_master
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

client = get_supabase_client()
tables = fetch_all_supabase_tables(client)
df = build_master(tables)

df_valid = df[df["order_status"] == "Selesai"].copy()
df_valid["tanggal"] = pd.to_datetime(df_valid["order_created_at"]).dt.floor("D")
daily = df_valid.groupby("tanggal")["valid_item_revenue"].sum().reset_index()
daily = daily.sort_values("tanggal").set_index("tanggal")
all_days = pd.date_range(start=daily.index.min(), end=daily.index.max(), freq="D")
daily = daily.reindex(all_days, fill_value=0)

weekly = daily.resample('W').sum()
series = weekly["valid_item_revenue"].astype(float)

mod1 = ExponentialSmoothing(series, trend="add", initialization_method="estimated").fit()
f1 = mod1.forecast(4)
print("Weekly Forecast:", f1)
print("Trend param (beta) in Weekly:", mod1.params.get('smoothing_trend'))

