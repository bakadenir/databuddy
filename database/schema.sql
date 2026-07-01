-- ==========================================
-- DataBuddy — Shopee Data Warehouse Schema
-- Star Schema Design
-- Submitted & active di Supabase (PostgreSQL)
-- ==========================================

-- ==========================================
-- 1. TABEL DIMENSI (DIMENSION TABLES)
-- ==========================================

-- Tabel Produk
CREATE TABLE dim_product (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE,
    product_name VARCHAR(255),
    product_variation VARCHAR(255),
    hpp BIGINT
);

-- Tabel Pengiriman/Ekspedisi
CREATE TABLE dim_shipping (
    shipping_id SERIAL PRIMARY KEY,
    courier_name VARCHAR(100),
    service_type VARCHAR(100)
);

-- Tabel Pelanggan
CREATE TABLE dim_customer (
    customer_id SERIAL PRIMARY KEY,
    customer_username VARCHAR(100) UNIQUE
);

-- Tabel Lokasi
CREATE TABLE dim_location (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(150),
    province VARCHAR(150)
);

-- Tabel Waktu (date_id = format YYYYMMDD)
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    order_created_at TIMESTAMP,
    tanggal_pesanan DATE,
    tahun INTEGER,
    kuartal INTEGER,
    bulan INTEGER,
    nama_bulan VARCHAR(20),
    hari VARCHAR(20),
    jam INTEGER
);

-- Tabel Pembayaran
CREATE TABLE dim_payment (
    payment_id SERIAL PRIMARY KEY,
    payment_method VARCHAR(100)
);

-- Tabel Status
CREATE TABLE dim_status (
    status_id SERIAL PRIMARY KEY,
    order_status VARCHAR(100)
);

-- ==========================================
-- 2. TABEL FAKTA (FACT TABLE)
-- ==========================================

CREATE TABLE fact_order_item (
    fact_order_item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) NOT NULL,

    -- Foreign Keys
    date_id INTEGER REFERENCES dim_date(date_id),
    product_id INTEGER REFERENCES dim_product(product_id),
    customer_id INTEGER REFERENCES dim_customer(customer_id),
    payment_id INTEGER REFERENCES dim_payment(payment_id),
    location_id INTEGER REFERENCES dim_location(location_id),
    status_id INTEGER REFERENCES dim_status(status_id),
    shipping_id INTEGER REFERENCES dim_shipping(shipping_id),

    -- Measures (Metrik)
    quantity INTEGER DEFAULT 0,
    original_price BIGINT DEFAULT 0,
    discounted_price BIGINT DEFAULT 0,
    total_discount BIGINT DEFAULT 0,
    valid_item_revenue BIGINT DEFAULT 0,

    -- Flags
    is_completed SMALLINT DEFAULT 0,
    is_cancelled SMALLINT DEFAULT 0
);

-- ==========================================
-- 3. INDEX
-- ==========================================

CREATE INDEX idx_fact_order_id   ON fact_order_item(order_id);
CREATE INDEX idx_fact_date_id    ON fact_order_item(date_id);
CREATE INDEX idx_fact_product_id ON fact_order_item(product_id);
