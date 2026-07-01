"""
core/models.py — SQLAlchemy ORM models
Merefleksikan star schema Supabase (PostgreSQL)
Digunakan untuk type hinting & validasi lokal
"""

from sqlalchemy import (
    Column, Integer, BigInteger, SmallInteger,
    String, Date, DateTime, ForeignKey, Index
)
from core.database import Base


# ── DIMENSION TABLES ──────────────────────────────────────────

class DimProduct(Base):
    __tablename__ = "dim_product"

    product_id       = Column(Integer, primary_key=True, autoincrement=True)
    sku              = Column(String(100), unique=True)
    product_name     = Column(String(255))
    product_variation = Column(String(255))
    hpp              = Column(BigInteger)


class DimShipping(Base):
    __tablename__ = "dim_shipping"

    shipping_id  = Column(Integer, primary_key=True, autoincrement=True)
    courier_name = Column(String(100))
    service_type = Column(String(100))


class DimCustomer(Base):
    __tablename__ = "dim_customer"

    customer_id       = Column(Integer, primary_key=True, autoincrement=True)
    customer_username = Column(String(100), unique=True)


class DimLocation(Base):
    __tablename__ = "dim_location"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    city        = Column(String(150))
    province    = Column(String(150))


class DimDate(Base):
    __tablename__ = "dim_date"

    date_id          = Column(Integer, primary_key=True)   # format YYYYMMDD
    order_created_at = Column(DateTime)
    tanggal_pesanan  = Column(Date)
    tahun            = Column(Integer)
    kuartal          = Column(Integer)
    bulan            = Column(Integer)
    nama_bulan       = Column(String(20))
    hari             = Column(String(20))
    jam              = Column(Integer)


class DimPayment(Base):
    __tablename__ = "dim_payment"

    payment_id     = Column(Integer, primary_key=True, autoincrement=True)
    payment_method = Column(String(100))


class DimStatus(Base):
    __tablename__ = "dim_status"

    status_id    = Column(Integer, primary_key=True, autoincrement=True)
    order_status = Column(String(100))


# ── FACT TABLE ────────────────────────────────────────────────

class FactOrderItem(Base):
    __tablename__ = "fact_order_item"

    fact_order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id           = Column(String(100), nullable=False)

    # Foreign Keys
    date_id     = Column(Integer, ForeignKey("dim_date.date_id"))
    product_id  = Column(Integer, ForeignKey("dim_product.product_id"))
    customer_id = Column(Integer, ForeignKey("dim_customer.customer_id"))
    payment_id  = Column(Integer, ForeignKey("dim_payment.payment_id"))
    location_id = Column(Integer, ForeignKey("dim_location.location_id"))
    status_id   = Column(Integer, ForeignKey("dim_status.status_id"))
    shipping_id = Column(Integer, ForeignKey("dim_shipping.shipping_id"))

    # Measures
    quantity           = Column(Integer, default=0)
    original_price     = Column(BigInteger, default=0)
    discounted_price   = Column(BigInteger, default=0)
    total_discount     = Column(BigInteger, default=0)
    valid_item_revenue = Column(BigInteger, default=0)

    # Flags
    is_completed = Column(SmallInteger, default=0)
    is_cancelled = Column(SmallInteger, default=0)

    # Indexes
    __table_args__ = (
        Index("idx_fact_order_id",   "order_id"),
        Index("idx_fact_date_id",    "date_id"),
        Index("idx_fact_product_id", "product_id"),
    )
