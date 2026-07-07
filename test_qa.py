import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

from core.database import get_supabase_client
from core.data_manager import fetch_all_supabase_tables, build_master
from pages._3_Chatbox import query_analytics # wait, python modules can't import files starting with numbers if not carefully done

