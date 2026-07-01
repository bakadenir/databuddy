"""
etl/validator.py — Validasi kolom & kualitas data Shopee
"""

import pandas as pd
from etl.loader import REQUIRED_COLUMNS


def validate(df: pd.DataFrame) -> dict:
    """
    Validasi DataFrame dari file Shopee.

    Returns:
        {
          "valid": bool,
          "missing_cols": list,
          "warnings": list,
          "row_count": int,
          "null_summary": dict
        }
    """
    result = {
        "valid": True,
        "missing_cols": [],
        "warnings": [],
        "row_count": len(df),
        "null_summary": {},
    }

    # 1. Cek kolom wajib
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        result["valid"] = False
        result["missing_cols"] = missing

    # 2. Cek baris kosong di kolom kritis
    if "Waktu Pesanan Dibuat" in df.columns:
        null_dates = df["Waktu Pesanan Dibuat"].isna().sum()
        if null_dates > 0:
            result["warnings"].append(
                f"{null_dates} baris tidak punya tanggal valid — akan dibuang saat ETL."
            )

    if "No. Pesanan" in df.columns:
        null_orders = df["No. Pesanan"].isna().sum()
        if null_orders > 0:
            result["warnings"].append(
                f"{null_orders} baris tanpa No. Pesanan ditemukan."
            )

    # 3. Summary null per kolom
    for col in REQUIRED_COLUMNS:
        if col in df.columns:
            n = df[col].isna().sum()
            if n > 0:
                result["null_summary"][col] = n

    return result
