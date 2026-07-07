"""
core/database.py — Koneksi SQLite lokal & Supabase
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pathlib import Path
from core.config import config


# ── SQLite (offline / development) ────────────────────────────

def get_local_engine():
    """Buat SQLAlchemy engine ke SQLite lokal."""
    db_path = config.LOCAL_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=config.is_development)


def get_local_session():
    """Return session factory untuk SQLite lokal."""
    engine = get_local_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_local_connection() -> bool:
    """Cek apakah koneksi SQLite berhasil."""
    try:
        engine = get_local_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] SQLite error: {e}")
        return False


# ── Base Model untuk ORM ───────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Supabase ───────────────────────────────────────────────────

def get_supabase_client():
    """
    Return Supabase client.
    Hanya bisa dipanggil setelah SUPABASE_URL & SUPABASE_KEY diset di .env
    """
    if not config.has_supabase:
        raise EnvironmentError(
            "SUPABASE_URL dan SUPABASE_KEY belum diset di file .env"
        )
    from supabase import create_client
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


def test_supabase_connection() -> bool:
    """Cek apakah koneksi Supabase berhasil."""
    try:
        client = get_supabase_client()
        # Ping dengan query sederhana
        client.table("_health").select("*").limit(1).execute()
        return True
    except Exception as e:
        print(f"[DB] Supabase error: {e}")
        return False


def reset_supabase_data() -> dict:
    """
    Hapus SEMUA data dari semua tabel Supabase via RPC Function.
    Pastikan function reset_databuddy_tables() sudah dibuat di Supabase!

    Returns:
        dict with status and details
    """
    try:
        client = get_supabase_client()

        # Debug: cek koneksi
        print("[DEBUG] Supabase client OK, memanggil RPC...")

        # Panggil RPC function yang sudah dibuat di Supabase
        response = client.rpc("reset_databuddy_tables").execute()

        print("[DEBUG] RPC response:", response)

        return {
            "success": True,
            "total_deleted": len(response.data) if response.data else 8, # type: ignore
            "details": response.data if response.data else [],
            "message": "Semua tabel berhasil di-reset!"
        }

    except Exception as e:
        error_msg = str(e)
        print("[ERROR] RPC Error:", error_msg)

        # Cek apakah error karena function belum dibuat
        if "function" in error_msg.lower() and ("not exist" in error_msg.lower() or "does not exist" in error_msg.lower()):
            return {
                "success": False,
                "error": "RPC Function belum dibuat! Jalankan SQL di Supabase Dashboard → SQL Editor",
                "setup_required": True
            }

        # Cek permission error
        if "permission" in error_msg.lower() or "access" in error_msg.lower():
            return {
                "success": False,
                "error": f"Permission denied: {error_msg}. Pastikan GRANT EXECUTE sudah dijalankan.",
                "setup_required": True
            }

        return {
            "success": False,
            "error": error_msg,
            "full_traceback": str(e.__traceback__) if hasattr(e, '__traceback__') else None
        }


def get_supabase_table_count(table_name: str) -> int:
    """Hitung jumlah baris di tabel Supabase."""
    try:
        client = get_supabase_client()
        response = client.table(table_name).select("*", count="exact").execute() # type: ignore
        return response.count if hasattr(response, 'count') and response.count is not None else 0
    except Exception:
        return 0
