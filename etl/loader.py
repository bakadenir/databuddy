"""
etl/loader.py — Load file CSV atau Excel menjadi DataFrame
Mendukung: .csv, .xlsx, .xls
"""

import pandas as pd
from pathlib import Path


# Kolom wajib yang harus ada di file Shopee
REQUIRED_COLUMNS = [
    'No. Pesanan',
    'Waktu Pesanan Dibuat',
    'Nama Produk',
    'Nama Variasi',
    'Username (Pembeli)',
    'Kota/Kabupaten',
    'Provinsi',
    'Metode Pembayaran',
    'Status Pesanan',
    'Opsi Pengiriman',
    'Jumlah',
    'Harga Awal',
    'Harga Setelah Diskon',
    'Total Diskon',
]


def load_file(file) -> tuple[pd.DataFrame, dict]:
    """
    Load file CSV atau Excel dari Streamlit UploadedFile.

    Returns:
        (df, info) — DataFrame mentah + info file
    """
    filename = file.name.lower()
    info = {"filename": file.name, "rows": 0, "missing_cols": []}

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file, encoding="utf-8")
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(file, engine="openpyxl")
        elif filename.endswith(".xls"):
            df = pd.read_excel(file, engine="xlrd")
        else:
            raise ValueError(f"Format file tidak didukung: {file.name}")

        info["rows"] = len(df)
        info["columns"] = list(df.columns)

        # Cek kolom yang hilang
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        info["missing_cols"] = missing

        return df, info

    except Exception as e:
        raise RuntimeError(f"Gagal membaca file '{file.name}': {e}")


def load_from_path(file_path: str) -> pd.DataFrame:
    """Load langsung dari path (untuk testing / Jupyter)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    if path.suffix == ".csv":
        return pd.read_csv(file_path, encoding="utf-8")
    elif path.suffix in (".xlsx",):
        return pd.read_excel(file_path, engine="openpyxl")
    elif path.suffix == ".xls":
        return pd.read_excel(file_path, engine="xlrd")
    else:
        raise ValueError(f"Format tidak didukung: {path.suffix}")
