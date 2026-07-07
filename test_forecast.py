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
series = daily["valid_item_revenue"].astype(float)

# Try default
mod1 = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=7, initialization_method="estimated").fit()
f1 = mod1.forecast(30)
print("Default Forecast End:", f1.iloc[-1])

# Try smoothing trend
mod2 = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=7, initialization_method="heuristic").fit()
f2 = mod2.forecast(30)
print("Heuristic Forecast End:", f2.iloc[-1])

# Try damped trend
mod3 = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=7, damped_trend=True, initialization_method="estimated").fit()
f3 = mod3.forecast(30)
print("Damped Forecast End:", f3.iloc[-1])

print("Trend param (beta) in Default:", mod1.params.get('smoothing_trend'))

