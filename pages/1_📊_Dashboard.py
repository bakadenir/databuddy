"""
pages/1_📊_Dashboard.py — Dashboard Interaktif DataBuddy
Membaca data dari session state (hasil ETL) → visualisasi dengan Plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Dashboard | DataBuddy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme Colors ────────────────────────────────────────────────
C = {
    "orange":  "#f97316",
    "amber":   "#fbbf24",
    "purple":  "#8b5cf6",
    "cyan":    "#06b6d4",
    "green":   "#22c55e",
    "red":     "#f43f5e",
    "blue":    "#3b82f6",
    "bg":      "#0f172a",
    "card":    "#1e293b",
    "border":  "#334155",
    "text":    "#f8fafc",
    "muted":   "#94a3b8",
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C["text"], family="Inter"),
    xaxis=dict(gridcolor="#1e293b", showgrid=True),
    yaxis=dict(gridcolor="#1e293b", showgrid=True),
    margin=dict(l=20, r=20, t=40, b=20),
)

COLOR_SEQ = [
    C["orange"], C["purple"], C["cyan"], C["green"],
    C["amber"], C["red"], C["blue"],
    "#ec4899", "#14b8a6", "#a78bfa",
]

# ── CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
div[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
div[data-testid="metric-container"] label { color: #94a3b8 !important; font-size: 0.8rem !important; }
div[data-testid="metric-container"] [data-testid="metric-value"] { color: #f8fafc !important; font-size: 1.6rem !important; }
div[data-testid="metric-container"] [data-testid="metric-delta"] { font-size: 0.75rem !important; }
.section-header {
    color: #94a3b8; font-size: 0.75rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 1.5rem 0 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Cek Data ────────────────────────────────────────────────────
from core.data_manager import (
    get_tables, build_master, kpi_overview, sales_trend,
    top_products, by_province, by_city, by_status,
    by_payment, order_heatmap, by_shipping, repeat_buyer_stats,
)

tables = get_tables()
if not tables:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0;">
        <div style="font-size:4rem;">📂</div>
        <h3 style="color:#f8fafc;">Belum ada data</h3>
        <p style="color:#94a3b8;">Upload file Shopee di halaman <b>📥 Upload & ETL</b> terlebih dahulu.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Build Master ────────────────────────────────────────────────
@st.cache_data
def get_master(_tables_id):
    return build_master(st.session_state["etl_tables"])

with st.spinner("🔄 Memuat data..."):
    df_master = get_master(id(tables))

# ── Header ──────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.5rem;">
    <div>
        <h2 style="
            background:linear-gradient(135deg,{C['orange']},{C['amber']});
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text; margin:0;
        ">📊 Dashboard Analytics</h2>
        <p style="color:{C['muted']}; margin:0; font-size:0.9rem;">
            {df_master['order_id'].nunique():,} orders · {df_master['customer_id'].nunique():,} customers · {df_master['tanggal_pesanan'].nunique()} hari
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════
# SIDEBAR — FILTERS
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <h3 style="color:{C['orange']}; margin:0 0 1rem 0;">🎛️ Filter</h3>
    """, unsafe_allow_html=True)

    # Date range
    min_date = df_master["tanggal_pesanan"].min()
    max_date = df_master["tanggal_pesanan"].max()
    date_range = st.date_input(
        "📅 Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter",
    )

    # Status
    all_statuses = sorted(df_master["order_status"].dropna().unique().tolist())
    selected_statuses = st.multiselect(
        "🏷️ Status Pesanan",
        options=all_statuses,
        default=all_statuses,
        key="status_filter",
    )

    # Province
    all_provinces = sorted(df_master["province"].dropna().unique().tolist())
    selected_provinces = st.multiselect(
        "📍 Provinsi",
        options=all_provinces,
        default=all_provinces,
        key="province_filter",
    )

    st.divider()
    st.caption(f"Data: {len(df_master):,} baris total")

# ── Apply Filters ────────────────────────────────────────────────
df = df_master.copy()

if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[df["tanggal_pesanan"].between(start, end)]

if selected_statuses:
    df = df[df["order_status"].isin(selected_statuses)]

if selected_provinces:
    df = df[df["province"].isin(selected_provinces)]

# ══════════════════════════════════════════════
# SECTION 1 — KPI CARDS
# ══════════════════════════════════════════════
kpi = kpi_overview(df)

k1, k2, k3, k4, k5, k6 = st.columns(6)

def fmt_rp(val):
    if val >= 1_000_000_000:
        return f"Rp {val/1_000_000_000:.1f}M"
    elif val >= 1_000_000:
        return f"Rp {val/1_000_000:.1f}Jt"
    elif val >= 1_000:
        return f"Rp {val/1_000:.0f}rb"
    return f"Rp {val:,}"

k1.metric("💰 Total Revenue",    fmt_rp(kpi["total_revenue"]))
k2.metric("🧾 Total Orders",     f"{kpi['total_orders']:,}")
k3.metric("✅ Completed",        f"{kpi['completed_orders']:,}")
k4.metric("👥 Pelanggan",        f"{kpi['total_customers']:,}")
k5.metric("🎯 Completion Rate",  f"{kpi['completion_rate']}%")
k6.metric("💳 Avg Order Value",  fmt_rp(kpi["aov"]))

st.divider()

# ══════════════════════════════════════════════
# SECTION 2 — SALES TREND
# ══════════════════════════════════════════════
st.markdown('<p class="section-header">📈 Tren Penjualan</p>', unsafe_allow_html=True)

freq_map = {"Harian": "D", "Mingguan": "W", "Bulanan": "ME"}
freq_label = st.radio(
    "Granularitas",
    options=list(freq_map.keys()),
    index=0,
    horizontal=True,
    key="trend_freq",
)
freq = freq_map[freq_label]
trend_df = sales_trend(df, freq=freq)

if not trend_df.empty:
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    fig_trend.add_trace(
        go.Bar(
            x=trend_df["tanggal"], y=trend_df["revenue"],
            name="Revenue", marker_color=C["orange"],
            opacity=0.85,
        ),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Scatter(
            x=trend_df["tanggal"], y=trend_df["orders"],
            name="Orders", mode="lines+markers",
            line=dict(color=C["cyan"], width=2),
            marker=dict(size=4),
        ),
        secondary_y=True,
    )

    fig_trend.update_layout(
        **PLOTLY_THEME,
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig_trend.update_yaxes(
        title_text="Revenue (Rp)", secondary_y=False,
        gridcolor=C["border"], tickprefix="Rp ",
    )
    fig_trend.update_yaxes(
        title_text="Jumlah Orders", secondary_y=True,
        gridcolor=C["border"],
    )
    st.plotly_chart(fig_trend, width="stretch")

st.divider()

# ══════════════════════════════════════════════
# SECTION 3 — TOP PRODUK + STATUS
# ══════════════════════════════════════════════
col_prod, col_status = st.columns([3, 2])

with col_prod:
    st.markdown('<p class="section-header">🏆 Top Produk</p>', unsafe_allow_html=True)

    top_by = st.radio(
        "Urutkan by",
        ["Revenue", "Quantity"],
        horizontal=True,
        key="top_by",
    )
    prod_df = top_products(df, n=12, by=top_by.lower())

    if not prod_df.empty:
        sort_col = "revenue" if top_by == "Revenue" else "qty"
        fig_prod = px.bar(
            prod_df.sort_values(sort_col),
            x=sort_col,
            y="product_name",
            orientation="h",
            color=sort_col,
            color_continuous_scale=[[0, "#1e293b"], [0.5, C["orange"]], [1, C["amber"]]],
            labels={"product_name": "", "revenue": "Revenue (Rp)", "qty": "Quantity"},
            text=sort_col,
        )
        fig_prod.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(size=10, color=C["muted"]),
        )
        fig_prod.update_layout(
            **PLOTLY_THEME,
            height=420,
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_prod, width="stretch")

with col_status:
    st.markdown('<p class="section-header">🏷️ Status Pesanan</p>', unsafe_allow_html=True)

    status_df = by_status(df)
    if not status_df.empty:
        STATUS_COLORS = {
            "Selesai": C["green"],
            "Dibatalkan": C["red"],
            "Pengembalian Dana": C["amber"],
            "Dalam Pengiriman": C["cyan"],
            "Diproses": C["blue"],
            "Siap Dikirim": C["purple"],
        }
        colors = [
            STATUS_COLORS.get(s, C["muted"])
            for s in status_df["order_status"]
        ]

        fig_status = px.pie(
            status_df,
            names="order_status",
            values="orders",
            hole=0.55,
            color_discrete_sequence=COLOR_SEQ,
        )
        fig_status.update_traces(
            textinfo="percent+label",
            textfont=dict(size=11),
            marker=dict(line=dict(color=C["bg"], width=2)),
        )
        fig_status.update_layout(
            **PLOTLY_THEME,
            height=220,
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_status, width="stretch")

    # Repeat Buyer stats
    st.markdown('<p class="section-header">🔁 Repeat Buyer</p>', unsafe_allow_html=True)
    rb = repeat_buyer_stats(df)

    rb_c1, rb_c2 = st.columns(2)
    rb_c1.metric("Repeat Buyers", f"{rb['repeat_buyers']:,}", f"{rb['repeat_rate']}%")
    rb_c2.metric("One-time",      f"{rb['one_time_buyers']:,}")

st.divider()

# ══════════════════════════════════════════════
# SECTION 4 — GEO: PROVINSI + KOTA
# ══════════════════════════════════════════════
st.markdown('<p class="section-header">📍 Analisis Geografis</p>', unsafe_allow_html=True)

geo_col1, geo_col2 = st.columns(2)

with geo_col1:
    prov_df = by_province(df)
    if not prov_df.empty:
        fig_prov = px.bar(
            prov_df.head(15).sort_values("revenue"),
            x="revenue", y="province",
            orientation="h",
            color="revenue",
            color_continuous_scale=[[0, "#1e293b"], [0.5, C["cyan"]], [1, C["blue"]]],
            title="Revenue per Provinsi (Top 15)",
            labels={"province": "", "revenue": "Revenue (Rp)"},
        )
        fig_prov.update_layout(
            **PLOTLY_THEME,
            height=380,
            showlegend=False,
            coloraxis_showscale=False,
            title_font=dict(size=13, color=C["muted"]),
        )
        st.plotly_chart(fig_prov, width="stretch")

with geo_col2:
    city_df = by_city(df, top_n=15)
    if not city_df.empty:
        fig_city = px.treemap(
            city_df,
            path=["province", "city"],
            values="orders",
            color="revenue",
            color_continuous_scale=[[0, C["card"]], [0.5, C["purple"]], [1, C["orange"]]],
            title="Distribusi Orders per Kota",
        )
        fig_city.update_layout(
            **PLOTLY_THEME,
            height=380,
            title_font=dict(size=13, color=C["muted"]),
            coloraxis_colorbar=dict(
                title="Revenue",
                thickness=10,
                len=0.6,
            ),
        )
        fig_city.update_traces(
            textfont=dict(size=11),
            marker=dict(line=dict(width=1, color=C["bg"])),
        )
        st.plotly_chart(fig_city, width="stretch")

st.divider()

# ══════════════════════════════════════════════
# SECTION 5 — HEATMAP + PAYMENT + SHIPPING
# ══════════════════════════════════════════════
heat_col, pay_col = st.columns([3, 2])

with heat_col:
    st.markdown('<p class="section-header">⏰ Pola Waktu Order (Jam × Hari)</p>', unsafe_allow_html=True)

    hm = order_heatmap(df)
    if not hm.empty:
        fig_hm = px.imshow(
            hm,
            color_continuous_scale=[[0, C["card"]], [0.4, C["purple"]], [0.8, C["orange"]], [1, C["amber"]]],
            aspect="auto",
            labels=dict(x="Jam", y="Hari", color="Orders"),
        )
        fig_hm.update_layout(
            **PLOTLY_THEME,
            height=260,
            xaxis=dict(title="Jam (0-23)", tickmode="linear", dtick=2),
            yaxis=dict(title=""),
            coloraxis_colorbar=dict(thickness=10, len=0.8),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_hm, width="stretch")

with pay_col:
    st.markdown('<p class="section-header">💳 Metode Pembayaran</p>', unsafe_allow_html=True)

    pay_df = by_payment(df)
    if not pay_df.empty:
        fig_pay = px.bar(
            pay_df.sort_values("orders"),
            x="orders", y="payment_method",
            orientation="h",
            color="revenue",
            color_continuous_scale=[[0, "#1e293b"], [0.5, C["green"]], [1, C["cyan"]]],
            labels={"payment_method": "", "orders": "Orders"},
        )
        fig_pay.update_layout(
            **PLOTLY_THEME,
            height=260,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=10, t=10, b=10),
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_pay, width="stretch")

st.divider()

# ══════════════════════════════════════════════
# SECTION 6 — EKSPEDISI + TABEL RINGKASAN
# ══════════════════════════════════════════════
ship_col, tbl_col = st.columns([2, 3])

with ship_col:
    st.markdown('<p class="section-header">🚚 Ekspedisi</p>', unsafe_allow_html=True)

    ship_df = by_shipping(df)
    if not ship_df.empty:
        fig_ship = px.pie(
            ship_df,
            names="courier_name",
            values="orders",
            hole=0.45,
            color_discrete_sequence=COLOR_SEQ,
        )
        fig_ship.update_traces(
            textinfo="percent+label",
            textfont=dict(size=10),
            marker=dict(line=dict(color=C["bg"], width=2)),
        )
        fig_ship.update_layout(
            **PLOTLY_THEME,
            height=280,
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig_ship, width="stretch")

with tbl_col:
    st.markdown('<p class="section-header">📋 Ringkasan per Provinsi</p>', unsafe_allow_html=True)

    prov_tbl = by_province(df).copy()
    prov_tbl["revenue_fmt"] = prov_tbl["revenue"].apply(fmt_rp)
    prov_tbl = prov_tbl[["province", "orders", "customers", "revenue_fmt"]].rename(
        columns={
            "province": "Provinsi",
            "orders": "Orders",
            "customers": "Pembeli",
            "revenue_fmt": "Revenue",
        }
    ).head(10)

    st.dataframe(
        prov_tbl,
        width="stretch",
        height=280,
        hide_index=True,
    )

# ── Footer ──────────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="text-align:center; color:{C['muted']}; font-size:0.8rem; padding:0.5rem 0;">
    DataBuddy Dashboard · Data dari {str(min_date.date()) if min_date is not pd.NaT else "-"} s.d. {str(max_date.date()) if max_date is not pd.NaT else "-"}
    · {len(df):,} baris dianalisis
</div>
""", unsafe_allow_html=True)
