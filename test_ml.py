import sys
import os
sys.path.append('.')
from core.data_manager import get_tables, build_master
from core.ml_engine import MLEngine

# Trick Streamlit to allow session state mock
import streamlit as st
import pandas as pd

# Kita pakai build_master tapi kita harus mock session_state
st.session_state = {}
# For test_ml to work, we need to bypass get_tables and directly fetch from Supabase
from core.database import get_supabase_client
from core.data_manager import fetch_all_supabase_tables
client = get_supabase_client()
tables = fetch_all_supabase_tables(client)

df = build_master(tables)
ml = MLEngine(df[df['is_completed'] == 1])
res = ml.market_basket_analysis(min_support=0.02)
if 'error' in res:
    print(res['error'])
else:
    print(res['metrics'])
    print(res['rules'].head(5))
