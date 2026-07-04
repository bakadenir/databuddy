# DataBuddy — Database Schema Documentation

## Star Schema Overview

```
              dim_date ◄───────────────────────────────────────┐
              dim_product ◄────────────────────────────────────┤
              dim_customer ◄───────────────────────────────────┤
dim_payment ►─────────────────── fact_order_item ──────────────┤
dim_location ►────────────────────────────────────────────────►┤
dim_status ►──────────────────────────────────────────────────►┤
dim_shipping ►────────────────────────────────────────────────►┘
```

---

## Tabel Dimensi

### `dim_date`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `date_id` | INTEGER PK | Format YYYYMMDD (e.g., 20240115) |
| `tanggal_pesanan` | DATE | Tanggal saja (tanpa jam) |
| `tahun` | INTEGER | e.g., 2024 |
| `kuartal` | INTEGER | 1–4 |
| `bulan` | INTEGER | 1–12 |
| `nama_bulan` | VARCHAR | "Januari", "Februari", ... |
| `hari` | VARCHAR | "Senin", "Selasa", ... |

### `dim_product`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `product_id` | SERIAL PK | |
| `sku` | VARCHAR UNIQUE | Kode SKU produk |
| `product_name` | VARCHAR | Nama produk |
| `product_variation` | VARCHAR | Variasi (warna, ukuran, dll.) |
| `hpp` | BIGINT | Harga Pokok Penjualan (manual input) |

### `dim_customer`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `customer_id` | SERIAL PK | |
| `customer_username` | VARCHAR UNIQUE | Username Shopee buyer |

### `dim_location`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `location_id` | SERIAL PK | |
| `city` | VARCHAR | Kota tujuan pengiriman |
| `province` | VARCHAR | Provinsi tujuan pengiriman |

### `dim_payment`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `payment_id` | SERIAL PK | |
| `payment_method` | VARCHAR | e.g., "SPayLater", "Transfer Bank", "COD" |

### `dim_status`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `status_id` | SERIAL PK | |
| `order_status` | VARCHAR | e.g., "Selesai", "Dibatalkan", "Dalam Pengiriman" |

### `dim_shipping`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `shipping_id` | SERIAL PK | |
| `courier_name` | VARCHAR | e.g., "J&T", "JNE", "SiCepat" |
| `service_type` | VARCHAR | e.g., "REG", "EXPRESS" |

---

## Tabel Fakta

### `fact_order_item`
| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `fact_order_item_id` | SERIAL PK | |
| `order_id` | VARCHAR | No. pesanan Shopee |
| `date_id` | INTEGER FK | → dim_date |
| `product_id` | INTEGER FK | → dim_product |
| `customer_id` | INTEGER FK | → dim_customer |
| `payment_id` | INTEGER FK | → dim_payment |
| `location_id` | INTEGER FK | → dim_location |
| `status_id` | INTEGER FK | → dim_status |
| `shipping_id` | INTEGER FK | → dim_shipping |
| `quantity` | INTEGER | Jumlah item |
| `original_price` | BIGINT | Harga sebelum diskon |
| `discounted_price` | BIGINT | Harga setelah diskon |
| `total_discount` | BIGINT | Total potongan harga |
| `valid_item_revenue` | BIGINT | Revenue valid (non-cancelled) |
| `is_completed` | SMALLINT | 1 = selesai, 0 = tidak |
| `is_cancelled` | SMALLINT | 1 = dibatalkan, 0 = tidak |
| `order_created_at` | TIMESTAMP | Waktu transaksi spesifik item ini |
| `jam` | INTEGER | Jam transaksi spesifik (0-23) |

---

## Mapping: Kolom Shopee CSV → Schema

| Kolom CSV Shopee | Target Tabel | Target Kolom | Catatan |
|------------------|-------------|--------------|---------|
| `No. Pesanan` | fact_order_item | order_id | |
| `Waktu Pesanan Dibuat` | dim_date | order_created_at | Parsed ke datetime |
| `Nama Produk` | dim_product | product_name | |
| `Nama Variasi` | dim_product | product_variation | |
| `Nama Produk` + `Nama Variasi` | dim_product | sku | SKU Sintetis (sementara) |
| `Username (Pembeli)` | dim_customer | customer_username | |
| `Kota/Kabupaten` | dim_location | city | |
| `Provinsi` | dim_location | province | |
| `Metode Pembayaran` | dim_payment | payment_method | |
| `Status Pesanan` | dim_status | order_status | |
| `Opsi Pengiriman` | dim_shipping | service_type | Full string |
| `Opsi Pengiriman` (split `-`) | dim_shipping | courier_name | Nama kurir saja |
| `Jumlah` | fact_order_item | quantity | |
| `Harga Awal` | fact_order_item | original_price | |
| `Harga Setelah Diskon` | fact_order_item | discounted_price | |
| `Total Diskon` | fact_order_item | total_discount | |
| Kalkulasi: qty × discounted | fact_order_item | valid_item_revenue | |
| Status = "selesai" | fact_order_item | is_completed | Flag 1/0 |
| Status = "batal/pengembalian" | fact_order_item | is_cancelled | Flag 1/0 |

## Catatan Penting

### HPP Source of Truth
- HPP **tidak ada** di file ekspor Shopee
- Nilai default = `0` untuk produk baru (jelas "belum diisi")
- Setelah upload, isi HPP manual di tabel `dim_product` di Supabase
- Upload berikutnya: HPP dari Supabase dipertahankan, **tidak tertimpa**

### dim_date — Baris = Hari Unik (bukan Transaksi)
- `dim_date` adalah **kalender harian** → 1 baris = 1 hari
- Data 6 bulan → ±180 baris = **BENAR** ✓
- `fact_order_item` yang menyimpan semua 8000+ baris transaksi

---

## Index

```sql
CREATE INDEX idx_fact_order_id   ON fact_order_item(order_id);
CREATE INDEX idx_fact_date_id    ON fact_order_item(date_id);
CREATE INDEX idx_fact_product_id ON fact_order_item(product_id);
```
