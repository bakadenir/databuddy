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
