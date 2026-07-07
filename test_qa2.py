import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from core.database import get_supabase_client
from core.data_manager import fetch_all_supabase_tables, build_master

client = get_supabase_client()
tables = fetch_all_supabase_tables(client)
df_master = build_master(tables)

import importlib.util
spec = importlib.util.spec_from_file_location("chatbox", "pages/3_Chatbox.py")
chatbox = importlib.util.module_from_spec(spec)
sys.modules["chatbox"] = chatbox
spec.loader.exec_module(chatbox)

res = chatbox.query_analytics("berapa omset di bulan januari?", df_master, "")
print("RESULT:", res)

