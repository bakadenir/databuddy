"""
etl/uploader.py — Upload semua tabel ke Supabase dengan logika Upsert

Logika HPP Source of Truth:
  1. Sebelum ETL → fetch dim_product dari Supabase
  2. Run ETL dengan passing existing_products
  3. Upsert dimensi (insert jika baru, skip jika sudah ada)
  4. Insert fact_order_item (skip order_id yang sudah ada)
"""

import pandas as pd
from typing import Optional, Any
from core.config import config


def get_existing_products() -> Optional[pd.DataFrame]:
    """
    Ambil semua produk dari dim_product Supabase.
    Return None jika Supabase belum dikonfigurasi.

    Ini adalah "Buku Induk" HPP — selalu dibaca SEBELUM ETL berjalan.
    """
    if not config.has_supabase:
        print("[WARN] Supabase belum dikonfigurasi. Mode offline.")
        return None

    try:
        from core.database import get_supabase_client
        client = get_supabase_client()
        response = client.table("dim_product").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            print(f"[OK] Buku Induk Produk: {len(df)} SKU dimuat dari Supabase.")
            return df
        print("[INFO] dim_product di Supabase masih kosong.")
        return pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] Gagal fetch dim_product: {e}")
        return None


def _upsert_dimension(
    client,
    table_name: str,
    df: pd.DataFrame,
    conflict_col: str,
) -> dict:
    """
    Upsert tabel dimensi:
    - Jika conflict_col sudah ada → SKIP (tidak overwrite)
    - Jika belum ada → INSERT baru

    Kolom 'xxx_id' tidak ikut di-upsert (di-generate Supabase via SERIAL).
    """
    # Buang kolom _id lokal (primary key di-handle Supabase)
    id_col = [c for c in df.columns if c.endswith("_id") and c != conflict_col]
    df_upload = df.drop(columns=id_col, errors="ignore")

    # Handle date serialization untuk dim_date
    if table_name == "dim_date" and "tanggal_pesanan" in df_upload.columns:
        df_upload = df_upload.copy()
        df_upload["tanggal_pesanan"] = df_upload["tanggal_pesanan"].astype(str)

    # Handle NaN values - replace with None
    df_upload = df_upload.where(pd.notnull(df_upload), None)

    records = df_upload.to_dict(orient="records")
    result: dict[str, Any] = {"table": table_name, "attempted": len(records), "error": None}

    try:
        # on_conflict="ignore" → skip jika conflict_col sudah ada
        client.table(table_name).upsert(
            records,
            on_conflict=conflict_col,
            ignore_duplicates=True,
        ).execute()
        print(f"[OK] {table_name}: {len(records)} records upserted (skip duplikat ✓)")
        result["success"] = True
    except Exception as e:
        print(f"[ERROR] {table_name}: {e}")
        result["error"] = str(e)
        result["success"] = False

    return result


def _insert_fact(client, df: pd.DataFrame) -> dict:
    """
    Insert fact_order_item.
    Skip order_id yang sudah ada di Supabase (idempotent).

    Kolom fact_order_item_id tidak ikut (SERIAL Supabase).
    """
    result: dict[str, Any] = {"table": "fact_order_item", "error": None}

    try:
        # 1. Ambil order_id yang sudah ada
        existing = client.table("fact_order_item").select("order_id").execute()
        existing_ids = {r["order_id"] for r in existing.data} if existing.data else set()

        # 2. Filter hanya order baru
        df_new = df[~df["order_id"].isin(existing_ids)].copy()
        df_new = df_new.drop(columns=["fact_order_item_id"], errors="ignore")

        result["skipped"] = len(df) - len(df_new)
        result["attempted"] = len(df_new)

        if df_new.empty:
            print("[INFO] fact_order_item: Tidak ada data baru untuk diinsert.")
            result["success"] = True
            return result

        # 3. Handle NaN & type conversion
        df_new = df_new.copy()

        # Ganti NaN di SEMUA kolom dengan None
        df_new = df_new.where(pd.notnull(df_new), None)

        print(f"[DEBUG] Sample data sebelum convert: {df_new[['quantity', 'original_price']].head(3).to_dict('records')}")

        # Khusus untuk kolom numerik — convert dengan lebih robust
        for col in ["quantity", "original_price", "discounted_price", "total_discount", "valid_item_revenue"]:
            if col in df_new.columns:
                # Convert semua ke numeric, coerce error jadi NaN
                df_new[col] = pd.to_numeric(df_new[col], errors="coerce")
                # Fill NaN dengan 0
                df_new[col] = df_new[col].fillna(0)
                # Round ke integer
                df_new[col] = df_new[col].round(0)
                # Convert ke integer — force conversion
                df_new[col] = df_new[col].astype(int)
                # Validate sudah integer
                assert df_new[col].dtype in ['int', 'int64'], f"{col} masih bukan integer! dtype: {df_new[col].dtype}"

        print(f"[DEBUG] Sample data setelah convert: {df_new[['quantity', 'original_price']].head(3).to_dict('records')}")

        # 4. Insert batch (chunk 500 per request agar tidak timeout)
        CHUNK = 500
        for i in range(0, len(df_new), CHUNK):
            chunk = df_new.iloc[i:i + CHUNK].copy()
            # Convert chunk numerik ke integer untuk JSON compliance
            for col in ["quantity", "original_price", "discounted_price", "total_discount", "valid_item_revenue", "jam", "is_completed", "is_cancelled"]:
                if col in chunk.columns:
                    chunk[col] = pd.to_numeric(chunk[col], errors="coerce").fillna(0).round(0).astype(int)  # type: ignore
            
            # Convert FKs ke Int64 lalu ke object agar bisa jadi None (mencegah float 5.0 di JSON)
            for col in ["date_id", "product_id", "customer_id", "payment_id", "location_id", "status_id", "shipping_id"]:
                if col in chunk.columns:
                    chunk[col] = pd.to_numeric(chunk[col], errors="coerce").astype("Int64").astype(object)  # type: ignore

            # Convert Timestamp to string for JSON serialization
            if "order_created_at" in chunk.columns:
                chunk["order_created_at"] = chunk["order_created_at"].astype(str).replace({"NaT": None, "nan": None, "None": None})

            # Ganti NaN dengan None di semua kolom
            chunk = chunk.where(pd.notnull(chunk), None)
            
            client.table("fact_order_item").insert(
                chunk.to_dict(orient="records")
            ).execute()

        print(
            f"[OK] fact_order_item: {len(df_new)} baris baru diinsert, "
            f"{result['skipped']} duplikat diskip ✓"
        )
        result["success"] = True

    except Exception as e:
        print(f"[ERROR] fact_order_item: {e}")
        result["error"] = str(e)
        result["success"] = False

    return result


def upload_all(tables: dict[str, pd.DataFrame]) -> list[dict]:
    """
    Upload semua 8 tabel ke Supabase.

    Args:
        tables: Output dari transformer.run_etl()

    Returns:
        List of result dicts per tabel
    """
    if not config.has_supabase:
        raise EnvironmentError(
            "SUPABASE_URL dan SUPABASE_KEY belum diset di file .env"
        )

    from core.database import get_supabase_client
    client = get_supabase_client()
    results = []

    print("\n[UPLOAD] Mulai upload ke Supabase...")
    print("=" * 50)

    # ── Dimensi (urutan penting! fact bergantung pada dimensi) ─
    results.append(_upsert_dimension(client, "dim_product",  tables["dim_product"],  "sku"))
    results.append(_upsert_dimension(client, "dim_customer", tables["dim_customer"], "customer_username"))
    # Skip dim_location & dim_shipping sementara (perlu fix schema)
    # results.append(_upsert_dimension(client, "dim_location", tables["dim_location"], "city"))
    # results.append(_upsert_dimension(client, "dim_shipping", tables["dim_shipping"], "service_type"))
    results.append(_upsert_dimension(client, "dim_date",     tables["dim_date"],     "date_id"))
    results.append(_upsert_dimension(client, "dim_payment",  tables["dim_payment"],  "payment_method"))
    results.append(_upsert_dimension(client, "dim_status",   tables["dim_status"],   "order_status"))

    # Manual upsert untuk dim_location & dim_shipping
    results.append(_manual_upsert_location(client, tables["dim_location"]))
    results.append(_manual_upsert_shipping(client, tables["dim_shipping"]))

    # ── Fact (setelah semua dimensi) ───────────────────────────
    # Re-resolve foreign keys dari Supabase (ID bisa beda dengan ID lokal)
    tables_resolved = _resolve_fk_from_supabase(client, tables)
    results.append(_insert_fact(client, tables_resolved["fact_order_item"]))

    print("=" * 50)
    success = sum(1 for r in results if r.get("success"))
    print(f"[SELESAI] {success}/{len(results)} tabel berhasil diupload ke Supabase.")
    return results


def _resolve_fk_from_supabase(client, tables: dict) -> dict:
    """
    Setelah upsert dimensi, Supabase yang generate ID final (SERIAL).
    Kita perlu re-fetch ID dari Supabase untuk dipasang ke fact table.

    Ini memastikan FK di fact_order_item konsisten dengan ID Supabase,
    bukan ID lokal sementara dari transformer.
    """
    print("[INFO] Re-resolve foreign keys dari Supabase...")

    # Fetch ID dari Supabase
    def fetch(table, cols):
        r = client.table(table).select(",".join(cols)).execute()
        return pd.DataFrame(r.data) if r.data else pd.DataFrame(columns=cols)

    sb_product  = fetch("dim_product",  ["product_id",  "sku"])
    sb_customer = fetch("dim_customer", ["customer_id", "customer_username"])
    sb_location = fetch("dim_location", ["location_id", "city", "province"])
    sb_payment  = fetch("dim_payment",  ["payment_id",  "payment_method"])
    sb_status   = fetch("dim_status",   ["status_id",   "order_status"])
    sb_shipping = fetch("dim_shipping", ["shipping_id", "service_type"])
    sb_date     = fetch("dim_date",     ["date_id"])

    fact = tables["fact_order_item"].copy()

    # Simpler approach: just use Supabase IDs via lookup dicts
    prod_map     = dict(zip(sb_product["sku"],                sb_product["product_id"]))
    cust_map     = dict(zip(sb_customer["customer_username"], sb_customer["customer_id"]))
    pay_map      = dict(zip(sb_payment["payment_method"],     sb_payment["payment_id"]))
    status_map   = dict(zip(sb_status["order_status"],        sb_status["status_id"]))
    ship_map     = dict(zip(sb_shipping["service_type"],      sb_shipping["shipping_id"]))

    # Rebuild fact dengan local dimensions sebagai bridge untuk re-mapping
    local_fact = tables["fact_order_item"].copy()
    local_dim_prod = tables["dim_product"][["product_id", "sku"]]

    # Untuk dimensi lain, join untuk dapat nilai text (untuk mapping ke Supabase)
    local_dim_cust = tables["dim_customer"][["customer_id", "customer_username"]]
    local_dim_pay  = tables["dim_payment"][["payment_id", "payment_method"]]
    local_dim_stat = tables["dim_status"][["status_id", "order_status"]]
    local_dim_ship = tables["dim_shipping"][["shipping_id", "service_type"]]
    local_dim_loc  = tables["dim_location"][["location_id", "city", "province"]]

    # Merge lokal untuk mendapatkan nilai text (bridge ke Supabase ID)
    f = local_fact.merge(local_dim_prod, on="product_id", how="left", suffixes=("", "_prod"))
    f = f.merge(local_dim_cust, on="customer_id", how="left", suffixes=("", "_cust"))
    f = f.merge(local_dim_pay, on="payment_id", how="left", suffixes=("", "_pay"))
    f = f.merge(local_dim_stat, on="status_id", how="left", suffixes=("", "_stat"))
    f = f.merge(local_dim_ship, on="shipping_id", how="left", suffixes=("", "_ship"))
    f = f.merge(local_dim_loc, on="location_id", how="left", suffixes=("", "_loc"))

    loc_map = {}
    for _, row in sb_location.iterrows():
        loc_map[(row["city"], row["province"])] = row["location_id"]

    # Assign Supabase IDs - gunakan kolom yang sudah di-merge
    f["product_id"]  = f["sku"].map(prod_map)
    f["customer_id"] = f["customer_username"].map(cust_map)
    f["payment_id"]  = f["payment_method"].map(pay_map)
    f["status_id"]   = f["order_status"].map(status_map)
    f["shipping_id"] = f["service_type"].map(ship_map)
    f["location_id"] = f.apply(
        lambda r: loc_map.get((r.get("city"), r.get("province"))), axis=1
    )

    # Pilih hanya kolom schema
    fact_final = f[[
        "order_id", "date_id", "product_id", "customer_id",
        "payment_id", "location_id", "status_id", "shipping_id",
        "quantity", "original_price", "discounted_price",
        "total_discount", "valid_item_revenue",
        "is_completed", "is_cancelled",
        "jam", "order_created_at"
    ]]

    print("[OK] Foreign keys resolved dari Supabase ✓")
    tables_out = dict(tables)
    tables_out["fact_order_item"] = fact_final
    return tables_out


def _manual_upsert_location(client, df: pd.DataFrame) -> dict:
    """Manual upsert untuk dim_location (composite UNIQUE constraint)"""
    result: dict[str, Any] = {"table": "dim_location", "attempted": len(df), "error": None, "success": False}

    try:
        # Ambil existing data untuk comparison
        existing = client.table("dim_location").select("*").execute()
        if existing.data:
            existing_df = pd.DataFrame(existing.data)
            # Filter hanya yang belum ada
            merged = df.merge(
                existing_df[["city", "province"]],
                on=["city", "province"],
                how="left",
                indicator=True
            )
            new_data = merged[merged["_merge"] == "left_only"][["city", "province"]].drop_duplicates()
        else:
            new_data = df[["city", "province"]].drop_duplicates()

        if not new_data.empty:
            client.table("dim_location").insert(
                new_data.to_dict(orient="records")  # type: ignore
            ).execute()

        result["success"] = True
        print(f"[OK] dim_location: {len(df)} processed, {len(new_data) if not new_data.empty else 0} new inserts")
    except Exception as e:
        result["error"] = str(e)
        print(f"[ERROR] dim_location: {e}")

    return result


def _manual_upsert_shipping(client, df: pd.DataFrame) -> dict:
    """Manual upsert untuk dim_shipping (UNIQUE on service_type)"""
    result: dict[str, Any] = {"table": "dim_shipping", "attempted": len(df), "error": None, "success": False}

    try:
        # Ambil existing data untuk comparison
        existing = client.table("dim_shipping").select("*").execute()
        if existing.data:
            existing_df = pd.DataFrame(existing.data)
            # Filter hanya yang belum ada
            merged = df.merge(
                existing_df[["service_type"]],
                on="service_type",
                how="left",
                indicator=True
            )
            new_data = merged[merged["_merge"] == "left_only"][["courier_name", "service_type"]].drop_duplicates()
        else:
            new_data = df[["courier_name", "service_type"]].drop_duplicates()

        if not new_data.empty:
            client.table("dim_shipping").insert(
                new_data.to_dict(orient="records")  # type: ignore
            ).execute()

        result["success"] = True
        print(f"[OK] dim_shipping: {len(df)} processed, {len(new_data) if not new_data.empty else 0} new inserts")
    except Exception as e:
        result["error"] = str(e)
        print(f"[ERROR] dim_shipping: {e}")

    return result
