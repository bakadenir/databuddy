"""
pages/1_Dashboard.py — Dashboard Interaktif DataBuddy
Membaca data dari session state (hasil ETL) → visualisasi dengan Plotly
Modern Soft Design
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.ui import (
    render_navbar, render_sidebar_footer, section_header, COLORS, SPACING,
    BORDER_RADIUS, SHADOWS, empty_state
)

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard | DataBuddy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Render Top Navigation
render_navbar()

# ── Theme Colors (Light) ───────────────────────────────────────
C = {
    "teal":    "#0d9488",
    "sky":     "#0ea5e9",
    "orange":  "#f97316",
    "amber":   "#f59e0b",
    "purple":  "#8b5cf6",
    "indigo":  "#6366f1",
    "green":   "#16a34a",
    "red":     "#dc2626",
    "pink":    "#db2777",
}

# Plotly light theme — bersih, colorful
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.7)",
    font=dict(color=COLORS["text"], family="Inter"),
    hoverlabel=dict(align="left"),
)

DEFAULT_MARGIN = dict(l=20, r=20, t=40, b=20)
GRID_STYLE = dict(gridcolor="#f1f5f9", showgrid=True)

def apply_grid(fig):
    """Terapkan light grid ke semua axes."""
    fig.update_xaxes(**GRID_STYLE)
    fig.update_yaxes(**GRID_STYLE)
    return fig

COLOR_SEQ = [
    C["teal"], C["orange"], C["indigo"], C["green"],
    C["amber"], C["red"], C["sky"], C["pink"],
    "#0891b2", "#9333ea",
]

# ── Cek Data ────────────────────────────────────────────────────
from core.data_manager import (
    get_tables, build_master, kpi_overview, sales_trend,
    top_products, by_province, by_city, by_status,
    by_payment, order_heatmap, by_shipping, repeat_buyer_stats,
)

tables = get_tables()
if not tables:
    empty_state(
        "Belum ada data",
        "Upload file Shopee di halaman <b>📥 Upload & ETL</b> terlebih dahulu.",
        icon="📂",
        link_url="Home"
    )
    st.stop()

# ── Build Master ────────────────────────────────────────────────
def get_master(tables_dict):
    return build_master(tables_dict)

with st.spinner("🔄 Memuat data..."):
    df_master = get_master(tables)

# ── Header & Filter ──────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom: 0.25rem;">
    <h1 style="
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
    ">Dashboard Analytics</h1>
</div>
""", unsafe_allow_html=True)

col_sub, col_date = st.columns([1, 1], vertical_alignment="center")

col_sub_placeholder = col_sub.empty()

min_date = df_master["tanggal_pesanan"].min()
max_date = df_master["tanggal_pesanan"].max()

with col_date:
    st.markdown("""
    <style>
    /* Samakan tinggi date input */
    div[data-testid="stDateInput"] > div[data-baseweb="input"] {
        min-height: 36px !important;
        height: 36px !important;
    }
    
    /* Perkecil lebar kalender dan pentok ke ujung kanan */
    div[data-testid="stDateInput"] {
        max-width: 195px !important;
        margin-left: auto !important;
    }
    
    /* Center text inside */
    div[data-testid="stDateInput"] input {
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    date_range = st.date_input(
        "Filter Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter",
        label_visibility="collapsed"
    )

st.markdown(f'<div style="margin: {SPACING["md"]} 0;"></div>', unsafe_allow_html=True)

# ── TAB SYSTEM ────────────────────────────────────────────────────

    # ── Apply Filters ────────────────────────────────────────────────
df = df_master.copy()

if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[df["tanggal_pesanan"].between(start, end)]

col_sub_placeholder.markdown(f"""
    <div style="position: relative; top: -5px; height: 36px; display: flex; align-items: center; margin-bottom: -1rem;">
        <p style="color: #64748b; margin: 0; font-size: 1.15rem; font-weight: 400; line-height: 1;">
            {df['order_id'].nunique():,} orders · {df['customer_id'].nunique():,} customers · {df['tanggal_pesanan'].nunique()} hari
        </p>
    </div>
""", unsafe_allow_html=True)

assert isinstance(df, pd.DataFrame)

# ═════════════════════════════════════════════════════════════════════
# SECTION 1 — KPI CARDS
# ═════════════════════════════════════════════════════════════════════
kpi = kpi_overview(df)

def fmt_rp(val):
    if val >= 1_000_000_000:
        return f"Rp {val/1_000_000_000:.1f}M"
    elif val >= 1_000_000:
        return f"Rp {val/1_000_000:.1f}Jt"
    elif val >= 1_000:
        return f"Rp {val/1_000:.0f}rb"
    return f"Rp {val:,}"

# KPI Cards with enhanced styling
k1, k2, k3, k4, k5, k6 = st.columns(6)

kpi_configs = [
    ("💰 Total Revenue", fmt_rp(kpi["total_revenue"]), C["teal"], "#ecfdf5"),
    ("🧾 Total Orders", f"{kpi['total_orders']:,}", C["orange"], "#fff7ed"),
    ("✅ Completed", f"{kpi['completed_orders']:,}", C["green"], "#ecfdf5"),
    ("👥 Pelanggan", f"{kpi['total_customers']:,}", C["sky"], "#e0f2fe"),
    ("🎯 Completion Rate", f"{kpi['completion_rate']}%", C["purple"], "#f5f3ff"),
    ("💳 Avg Order Value", fmt_rp(kpi["aov"]), C["indigo"], "#eef2ff"),
]

for col, (label, value, color, bg) in zip([k1, k2, k3, k4, k5, k6], kpi_configs):
    with col:
        st.markdown(f"""
        <div style="
            background: {bg};
            border: 2px solid {color};
            border-radius: {BORDER_RADIUS['lg']};
            padding: 1.25rem;
            text-align: center;
            box-shadow: {SHADOWS['sm']};
            transition: all 0.2s ease;
            height: 100%;
        " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='{SHADOWS['md']}'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='{SHADOWS['sm']}'">
            <div style="color: {color}; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                {label}
            </div>
            <div style="color: {COLORS['text']}; font-size: 1.5rem; font-weight: 800; line-height: 1.2;">
                {value}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f'<div style="margin: {SPACING["lg"]} 0;"></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# SECTION 2 — SALES TREND
# ═════════════════════════════════════════════════════════════════════
trend_title = "Tren Penjualan"
if len(date_range) == 2:
    s_dt, e_dt = date_range
    m_id = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    if s_dt.month == e_dt.month and s_dt.year == e_dt.year:
        date_str = f"{s_dt.day} - {e_dt.day} {m_id[e_dt.month-1]} {e_dt.year}"
    elif s_dt.year == e_dt.year:
        date_str = f"{s_dt.day} {m_id[s_dt.month-1]} - {e_dt.day} {m_id[e_dt.month-1]} {e_dt.year}"
    else:
        date_str = f"{s_dt.day} {m_id[s_dt.month-1]} {s_dt.year} - {e_dt.day} {m_id[e_dt.month-1]} {e_dt.year}"
    trend_title = f"Tren Penjualan ({date_str})"

section_header(trend_title, "📈", "Analisis revenue dan orders over time")

freq_map = {"Harian": "D", "Mingguan": "W", "Bulanan": "ME"}
freq_label = st.radio(
    "Granularitas",
    options=list(freq_map.keys()),
    horizontal=True,
    key="trend_freq",
)
freq = freq_map[freq_label]

# Auto-adjust untuk 1 hari -> Jam-jaman, >1 hari -> Jangan tampilkan jam
unique_days = df["tanggal_pesanan"].nunique()
if unique_days == 1 and freq == "D":
    freq = "h"  # Paksa jadi jam-jaman jika cuma 1 hari

trend_df = sales_trend(df, freq=freq)

if not trend_df.empty:
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    fig_trend.add_trace(
        go.Bar(
            x=trend_df["tanggal"], y=trend_df["revenue"],
            name="Revenue", marker_color=C["teal"],
            opacity=0.85,
            hovertemplate="Revenue: <b>Rp %{y:,.0f}</b><extra></extra>"
        ),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Scatter(
            x=trend_df["tanggal"], y=trend_df["orders"],
            name="Orders", mode="lines+markers",
            line=dict(color=C["orange"], width=2.5),
            marker=dict(size=5),
            hovertemplate="Orders: <b>%{y}</b> pesanan<extra></extra>"
        ),
        secondary_y=True,
    )

    fig_trend.update_layout(
        **PLOTLY_THEME,
        height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    
    # Format sumbu X: Jika Harian (D), jangan tampilkan jam (paksa jarak 1 hari)
    if freq == "D":
        if unique_days <= 14:
            fig_trend.update_xaxes(
                **GRID_STYLE,
                tickformat="%d %b %Y",
                dtick=86400000, # 1 hari dalam milidetik
                tickmode="linear"
            )
        else:
            fig_trend.update_xaxes(
                **GRID_STYLE,
                tickformat="%d %b %Y",
            )
    elif freq == "h":
        fig_trend.update_xaxes(**GRID_STYLE, tickformat="%H:%M<br>%d %b")
    else:
        fig_trend.update_xaxes(**GRID_STYLE)

    fig_trend.update_yaxes(
        title_text="Revenue (Rp)", secondary_y=False,
        gridcolor="#f1f5f9", tickprefix="Rp ", color=COLORS["muted"],
    )
    fig_trend.update_yaxes(
        title_text="Jumlah Orders", secondary_y=True,
        gridcolor="#f1f5f9", color=COLORS["muted"],
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

st.markdown(f'<div style="margin: {SPACING["lg"]} 0;"></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# SECTION 3 — TOP PRODUK + STATUS
# ═════════════════════════════════════════════════════════════════════
col_prod, col_status = st.columns([3, 2])

with col_prod:
    section_header("Top Produk", "🏆", "Produk terbaik berdasarkan performa")

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
            color_continuous_scale=[[0, "#f0f9ff"], [0.5, C["teal"]], [1, C["indigo"]]],
            labels={"product_name": "", "revenue": "Revenue (Rp)", "qty": "Quantity"},
            text=sort_col,
        )
        fig_prod.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(size=10, color=COLORS["muted"]),
            hovertemplate="<b>%{y}</b><br>Total: <b>%{x:,.0f}</b><extra></extra>"
        )
        fig_prod.update_layout(
            **PLOTLY_THEME,
            height=420,
            margin=DEFAULT_MARGIN,
            showlegend=False,
            coloraxis_showscale=False,
        )
        apply_grid(fig_prod)
        fig_prod.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig_prod, use_container_width=True, config={'displayModeBar': False})

with col_status:
    section_header("Status Pesanan", "🏷️")

    status_df = by_status(df)
    if not status_df.empty:
        STATUS_COLORS = {
            "Selesai": C["green"],
            "Dibatalkan": C["red"],
            "Pengembalian Dana": C["amber"],
            "Dalam Pengiriman": C["sky"],
            "Diproses": C["indigo"],
            "Siap Dikirim": C["purple"],
        }
        colors = [
            STATUS_COLORS.get(s, COLORS["muted"])
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
            marker=dict(line=dict(color=COLORS["bg"], width=2)),
            hovertemplate="Status: <b>%{label}</b><br>Total: <b>%{value}</b> Pesanan<extra></extra>"
        )
        fig_status.update_layout(
            **PLOTLY_THEME,
            height=240,
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_status, use_container_width=True, config={'displayModeBar': False})

    # Repeat Buyer stats
    st.markdown(f'<div style="margin: {SPACING["md"]} 0;"></div>', unsafe_allow_html=True)
    section_header("Repeat Buyer", "🔁")

    rb = repeat_buyer_stats(df)

    rb_c1, rb_c2 = st.columns(2)
    with rb_c1:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: {BORDER_RADIUS['md']};
            padding: 1rem;
            text-align: center;
        ">
            <div style="color: {COLORS['muted']}; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Repeat Buyers</div>
            <div style="color: {COLORS['text']}; font-size: 1.25rem; font-weight: 800;">{rb['repeat_buyers']:,}</div>
            <div style="color: {C['green']}; font-size: 0.75rem; font-weight: 700;">{rb['repeat_rate']}%</div>
        </div>
        """, unsafe_allow_html=True)

    with rb_c2:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: {BORDER_RADIUS['md']};
            padding: 1rem;
            text-align: center;
        ">
            <div style="color: {COLORS['muted']}; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">One-time</div>
            <div style="color: {COLORS['text']}; font-size: 1.25rem; font-weight: 800;">{rb['one_time_buyers']:,}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f'<div style="margin: {SPACING["lg"]} 0;"></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# SECTION 4 — GEO: PROVINSI + KOTA
# ═════════════════════════════════════════════════════════════════════
section_header("Analisis Geografis", "📍", "Distribusi pelanggan dan revenue berdasarkan lokasi")

geo_col1, geo_col2 = st.columns(2)

with geo_col1:
    prov_df = by_province(df)
    if not prov_df.empty:
        fig_prov = px.bar(
            prov_df.head(15).sort_values("revenue"),
            x="revenue", y="province",
            orientation="h",
            color="revenue",
            color_continuous_scale=[[0, "#f0f9ff"], [0.5, C["sky"]], [1, C["indigo"]]],
            title="Revenue per Provinsi (Top 15)",
            labels={"province": "", "revenue": "Revenue (Rp)"},
        )
        fig_prov.update_layout(
            **PLOTLY_THEME,
            height=380,
            margin=DEFAULT_MARGIN,
            showlegend=False,
            coloraxis_showscale=False,
            title_font=dict(size=13, color=COLORS["muted"]),
        )
        fig_prov.update_traces(
            hovertemplate="Provinsi: <b>%{y}</b><br>Revenue: <b>Rp %{x:,.0f}</b><extra></extra>"
        )
        apply_grid(fig_prov)
        st.plotly_chart(fig_prov, use_container_width=True, config={'displayModeBar': False})

with geo_col2:
    city_df = by_city(df, top_n=15)
    if not city_df.empty:
        fig_city = px.treemap(
            city_df,
            path=["province", "city"],
            values="orders",
            color="revenue",
            color_continuous_scale=[[0, "#f5f3ff"], [0.5, C["indigo"]], [1, C["orange"]]],
            title="Distribusi Orders per Kota",
        )
        fig_city.update_layout(
            **PLOTLY_THEME,
            height=380,
            margin=DEFAULT_MARGIN,
            title_font=dict(size=13, color=COLORS["muted"]),
            coloraxis_colorbar=dict(
                title="Revenue",
                thickness=10,
                len=0.6,
            ),
        )
        fig_city.update_traces(
            textfont=dict(size=11),
            marker=dict(line=dict(width=1, color=COLORS["bg"])),
            hovertemplate="<b>%{label}</b><br>Total: <b>%{value}</b> Pesanan<extra></extra>"
        )
        st.plotly_chart(fig_city, use_container_width=True, config={'displayModeBar': False})

st.markdown(f'<div style="margin: {SPACING["lg"]} 0;"></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# SECTION 5 — HEATMAP + PAYMENT + SHIPPING
# ═════════════════════════════════════════════════════════════════════
heat_col, pay_col = st.columns([3, 2])

with heat_col:
    section_header("Pola Waktu Order", "⏰", "Jam × Hari heatmap")

    hm = order_heatmap(df)
    if not hm.empty:
        # Ubah jam jadi format string pendek agar muat di sumbu X (contoh: 00:00)
        hm.columns = [f"{int(c):02d}:00" for c in hm.columns]

        fig_hm = px.imshow(
            hm,
            color_continuous_scale=[[0, "#f0fdf4"], [0.4, C["teal"]], [0.8, C["indigo"]], [1, C["orange"]]],
            aspect="auto",
            labels=dict(x="Waktu", y="Hari", color="Pesanan"),
        )
        
        # Format popup tooltip
        fig_hm.update_traces(
            hovertemplate="Hari <b>%{y}</b><br>Pukul: %{x} WIB<br>Total: <b>%{z}</b> Pesanan<extra></extra>"
        )
        
        fig_hm.update_layout(
            **PLOTLY_THEME,
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_colorbar=dict(thickness=10, len=0.8),
        )
        # Tampilkan semua label jam, putar agar muat
        fig_hm.update_xaxes(title_text="", tickangle=-45, tickmode="linear", dtick=1)
        fig_hm.update_yaxes(title_text="")
        st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})

with pay_col:
    section_header("Metode Pembayaran", "💳")

    pay_df = by_payment(df)
    if not pay_df.empty:
        fig_pay = px.bar(
            pay_df.sort_values("orders"),
            x="orders", y="payment_method",
            orientation="h",
            color="revenue",
            color_continuous_scale=[[0, "#f0fdf4"], [0.5, C["green"]], [1, C["teal"]]],
            labels={"payment_method": "", "orders": "Orders"},
        )
        fig_pay.update_layout(
            **PLOTLY_THEME,
            height=280,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=10, t=10, b=10),
        )
        fig_pay.update_traces(
            hovertemplate="Metode: <b>%{y}</b><br>Total: <b>%{x}</b> Pesanan<extra></extra>"
        )
        apply_grid(fig_pay)
        fig_pay.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig_pay, use_container_width=True, config={'displayModeBar': False})

st.markdown(f'<div style="margin: {SPACING["lg"]} 0;"></div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# SECTION 6 — EKSPEDISI + TABEL RINGKASAN
# ═════════════════════════════════════════════════════════════════════
ship_col, tbl_col = st.columns([2, 3])

with ship_col:
    section_header("Ekspedisi", "🚚")

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
            marker=dict(line=dict(color=COLORS["bg"], width=2)),
            hovertemplate="Ekspedisi: <b>%{label}</b><br>Total: <b>%{value}</b> Pesanan<extra></extra>"
        )
        fig_ship.update_layout(
            **PLOTLY_THEME,
            height=300,
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig_ship, use_container_width=True, config={'displayModeBar': False})

with tbl_col:
    section_header("Ringkasan per Provinsi", "📋")

    prov_tbl = by_province(df).copy()
    assert isinstance(prov_tbl, pd.DataFrame)
    prov_tbl["revenue_fmt"] = prov_tbl["revenue"].apply(fmt_rp)
    prov_tbl = prov_tbl[["province", "orders", "customers", "revenue_fmt"]]
    assert isinstance(prov_tbl, pd.DataFrame)
    prov_tbl = prov_tbl.rename(
        columns={
            "province": "Provinsi",
            "orders": "Orders",
            "customers": "Pembeli",
            "revenue_fmt": "Revenue",
        }
    ).head(10)

    st.dataframe(
        prov_tbl,
        use_container_width=True,
        height=300,
        hide_index=True,
    )

    # ── Footer ──────────────────────────────────────────────────────
    st.markdown(f"""
<div style="
    margin-top: {SPACING['xl']};
    padding-top: {SPACING['lg']};
    border-top: 1px solid {COLORS['border']};
    text-align: center;
    color: {COLORS['muted']};
    font-size: 0.8rem;
">
    DataBuddy Dashboard · Data dari {str(min_date.date()) if min_date is not pd.NaT else "-"} s.d. {str(max_date.date()) if max_date is not pd.NaT else "-"}
    · {len(df):,} baris dianalisis
</div>
""", unsafe_allow_html=True)

render_sidebar_footer()

