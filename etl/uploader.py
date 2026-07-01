"""
etl/uploader.py — Upload semua tabel ke Supabase dengan logika Upsert

Logika HPP Source of Truth:
  1. Sebelum ETL → fetch dim_product dari Supabase
  2. Run ETL dengan passing existing_products
  3. Upsert dimensi (insert jika baru, skip jika sudah ada)
  4. Insert fact_order_item (skip order_id yang sudah ada)
"""

import pandas as pd
from typing import Optional
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

    records = df_upload.to_dict(orient="records")
    result = {"table": table_name, "attempted": len(records), "error": None}

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
    result = {"table": "fact_order_item", "error": None}

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

        # 3. Insert batch (chunk 500 per request agar tidak timeout)
        CHUNK = 500
        for i in range(0, len(df_new), CHUNK):
            chunk = df_new.iloc[i:i + CHUNK]
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
    results.append(_upsert_dimension(client, "dim_location", tables["dim_location"], "city"))
    results.append(_upsert_dimension(client, "dim_date",     tables["dim_date"],     "date_id"))
    results.append(_upsert_dimension(client, "dim_payment",  tables["dim_payment"],  "payment_method"))
    results.append(_upsert_dimension(client, "dim_status",   tables["dim_status"],   "order_status"))
    results.append(_upsert_dimension(client, "dim_shipping", tables["dim_shipping"], "service_type"))

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

    # Re-join untuk overwrite local IDs dengan Supabase IDs
    # Kita perlu data join key dari tabel dimensi lokal
    dim_prod = tables["dim_product"][["sku", "product_id"]].rename(
        columns={"product_id": "product_id_local"}
    )
    # Karena fact sudah punya product_id lokal, kita pakai sku mapping
    # Lebih aman: merge via sku
    fact = fact.drop(columns=["product_id"], errors="ignore")
    # Kita tidak punya sku di fact langsung, ambil dari dim_product lokal
    fact = fact.merge(
        tables["dim_product"][["product_id", "sku"]].rename(
            columns={"product_id": "local_pid"}
        ),
        left_on="product_id" if "product_id" in fact.columns else None,
        right_on="local_pid", how="left"
    ) if "product_id" in tables["fact_order_item"].columns else fact

    # Simpler approach: just use Supabase IDs via lookup dicts
    prod_map     = dict(zip(sb_product["sku"],                sb_product["product_id"]))
    cust_map     = dict(zip(sb_customer["customer_username"], sb_customer["customer_id"]))
    pay_map      = dict(zip(sb_payment["payment_method"],     sb_payment["payment_id"]))
    status_map   = dict(zip(sb_status["order_status"],        sb_status["status_id"]))
    ship_map     = dict(zip(sb_shipping["service_type"],      sb_shipping["shipping_id"]))

    # Rebuild fact dengan local dimensions sebagai bridge untuk re-mapping
    local_fact = tables["fact_order_item"].copy()
    local_dim_prod = tables["dim_product"][["product_id", "sku"]]
    local_dim_cust = tables["dim_customer"]
    local_dim_pay  = tables["dim_payment"]
    local_dim_stat = tables["dim_status"]
    local_dim_ship = tables["dim_shipping"]
    local_dim_loc  = tables["dim_location"]

    # Merge lokal untuk mendapatkan nilai text (bridge ke Supabase ID)
    f = local_fact.merge(local_dim_prod, on="product_id", how="left")
    f = f.merge(local_dim_cust, on="customer_id", how="left")
    f = f.merge(local_dim_pay, on="payment_id", how="left")
    f = f.merge(local_dim_stat, on="status_id", how="left")
    f = f.merge(local_dim_ship, on="shipping_id", how="left")
    f = f.merge(local_dim_loc, on="location_id", how="left")

    loc_map = {}
    for _, row in sb_location.iterrows():
        loc_map[(row["city"], row["province"])] = row["location_id"]

    # Assign Supabase IDs
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
    ]]

    print("[OK] Foreign keys resolved dari Supabase ✓")
    tables_out = dict(tables)
    tables_out["fact_order_item"] = fact_final
    return tables_out
