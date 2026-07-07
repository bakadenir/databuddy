"""
etl/loader.py — Load file CSV atau Excel menjadi DataFrame
Mendukung: .csv, .xlsx, .xls

Catatan khusus Shopee Excel Export:
- File Excel Shopee kadang punya baris kosong / metadata di atas header
- Fungsi ini otomatis mendeteksi baris header yang benar
- Sheet yang dipakai: sheet pertama (index 0)
"""

import pandas as pd
from pathlib import Path
from io import BytesIO


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


from typing import Literal

def _detect_header_row(file_bytes: bytes, engine: Literal["openpyxl", "xlrd"]) -> int:
    """
    Deteksi otomatis baris mana yang merupakan header.
    Beberapa format export Shopee punya baris kosong/metadata di atas.
    Coba baca 10 baris pertama dan cari baris yang mengandung 'No. Pesanan'.
    """
    for skip in range(10):
        try:
            df_test = pd.read_excel(
                BytesIO(file_bytes),
                engine=engine,
                header=skip,
                nrows=3,
            )
            cols = [c.strip() for c in df_test.columns]
            if "No. Pesanan" in cols:
                return skip
        except Exception:
            continue
    return 0  # fallback ke row pertama


def _read_excel_robust(file_bytes: bytes, engine: Literal["openpyxl", "xlrd"]) -> pd.DataFrame:
    """
    Baca Excel dengan auto-detect header row.
    Handles Shopee export yang punya metadata di atas tabel data.
    """
    header_row = _detect_header_row(file_bytes, engine)

    df = pd.read_excel(
        BytesIO(file_bytes),
        engine=engine,
        header=header_row,
        sheet_name=0,          # selalu pakai sheet pertama
        dtype=str,             # baca semua sebagai string dulu (aman untuk cleaning)
    )

    # Bersihkan nama kolom (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Buang baris yang seluruhnya NaN (sering ada di file Excel Shopee)
    df = df.dropna(how="all").reset_index(drop=True)

    return df


def load_file(file) -> tuple[pd.DataFrame, dict]:
    """
    Load file CSV atau Excel dari Streamlit UploadedFile.

    Returns:
        (df, info) — DataFrame mentah + info file
    """
    filename = file.name.lower()
    info = {
        "filename": file.name,
        "rows": 0,
        "missing_cols": [],
        "format": "",
        "header_row": 0,
    }

    try:
        if filename.endswith(".csv"):
            # Coba UTF-8 dulu, fallback ke latin-1 (common di Windows)
            try:
                df = pd.read_csv(file, encoding="utf-8", dtype=str)
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding="latin-1", dtype=str)
            df.columns = [c.strip() for c in df.columns]
            df = df.dropna(how="all").reset_index(drop=True)
            info["format"] = "CSV"

        elif filename.endswith(".xlsx"):
            file_bytes = file.read()
            header_row = _detect_header_row(file_bytes, "openpyxl")
            df = _read_excel_robust(file_bytes, "openpyxl")
            info["format"] = "Excel (.xlsx)"
            info["header_row"] = header_row

        elif filename.endswith(".xls"):
            file_bytes = file.read()
            header_row = _detect_header_row(file_bytes, "xlrd")
            df = _read_excel_robust(file_bytes, "xlrd")
            info["format"] = "Excel (.xls)"
            info["header_row"] = header_row

        else:
            raise ValueError(
                f"Format file tidak didukung: '{file.name}'. "
                "Gunakan .csv, .xlsx, atau .xls"
            )

        info["rows"] = len(df)
        info["columns"] = list(df.columns)

        # Cek kolom yang hilang
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        info["missing_cols"] = missing

        return df, info

    except Exception as e:
        raise RuntimeError(f"Gagal membaca file '{file.name}': {e}")


def load_from_path(file_path: str) -> pd.DataFrame:
    """
    Load langsung dari path lokal (untuk testing / Jupyter Notebook).
    Mendukung: .csv, .xlsx, .xls

    Contoh:
        df = load_from_path('/Users/kamu/Downloads/shopee_orders.xlsx')
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        try:
            df = pd.read_csv(file_path, encoding="utf-8", dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin-1", dtype=str)
        df.columns = [c.strip() for c in df.columns]

    elif suffix == ".xlsx":
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        df = _read_excel_robust(file_bytes, "openpyxl")

    elif suffix == ".xls":
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        df = _read_excel_robust(file_bytes, "xlrd")

    else:
        raise ValueError(
            f"Format tidak didukung: '{suffix}'. Gunakan .csv, .xlsx, atau .xls"
        )

    df = df.dropna(how="all").reset_index(drop=True)
    print(f"[OK] File '{path.name}' berhasil dibaca: {len(df)} baris, {len(df.columns)} kolom")
    return df
