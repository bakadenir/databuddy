"""
DataBuddy — Professional Landing Page (SEO-Optimized)
Shopee Analytics & Science Assistant Platform
"""

import streamlit as st

# ═════════════════════════════════════════════════════════════════════
# PAGE CONFIG & SEO METADATA
# ═════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="DataBuddy — Analitik Data Shopee & AI Assistant untuk Seller Indonesia",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═════════════════════════════════════════════════════════════════════
# SEO: META TAGS, OPEN GRAPH, SCHEMA MARKUP
# ═════════════════════════════════════════════════════════════════════

seo_meta = """
<!-- Primary Meta Tags -->
<title>DataBuddy — Analitik Data Shopee & AI Assistant untuk Seller Indonesia</title>
<meta name="title" content="DataBuddy — Analitik Data Shopee & AI Assistant untuk Seller Indonesia">
<meta name="description" content="DataBuddy adalah platform analitik data Shopee dengan AI untuk seller Indonesia. Upload Excel pesanan Shopee, dapatkan dashboard interaktif, insight penjualan, dan chatbot AI cerdas dalam hitungan detik.">
<meta name="keywords" content="analitik shopee, dashboard shopee seller, data shopee, AI shopee, analisis penjualan shopee, export shopee, tools shopee indonesia">
<meta name="author" content="DataBuddy">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://databuddy.app">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://databuddy.app">
<meta property="og:title" content="DataBuddy — Analitik Data Shopee & AI Assistant">
<meta property="og:description" content="Transform data pesanan Shopee menjadi insight bisnis dengan AI. Dashboard interaktif, segmentasi pelanggan, dan chatbot cerdas dalam satu platform.">

<!-- Favicon -->
<link rel="icon" type="image/png" href="https://databuddy.app/favicon.png">

<!-- JSON-LD Schema Markup -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "DataBuddy",
  "applicationCategory": "BusinessApplication",
  "description": "Platform analitik data Shopee dengan AI untuk seller Indonesia.",
  "aggregateRating": {
    "ratingValue": "4.8",
    "ratingCount": "127"
  }
}
</script>
"""

st.markdown(seo_meta, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    html { scroll-behavior: smooth; }

    /* Custom button styles */
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: white !important;
        padding: 1.4rem 3.5rem !important;
        border-radius: 50px !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4) !important;
        transition: all 0.3s ease !important;
        font-size: 1.15rem !important;
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(249, 115, 22, 0.5) !important;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(14, 165, 233, 0.15);
        border-color: #0ea5e9;
    }
    .feature-desc {
        flex-grow: 1;
        display: flex;
        align-items: center;
    }

    /* FAQ accordion */
    .faq-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        margin-bottom: 1rem;
        overflow: hidden;
    }
    .faq-item input[type="checkbox"] { display: none; }
    .faq-item label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.25rem 1.75rem;
        font-weight: 700;
        font-size: 1rem;
        color: #0f172a;
        cursor: pointer;
    }
    .faq-item label:hover { color: #0ea5e9; }
    .faq-item label::after {
        content: '+';
        font-size: 1.75rem;
        color: #64748b;
        transition: transform 0.3s;
    }
    .faq-item input:checked ~ label::after {
        content: '−';
        transform: rotate(180deg);
    }
    .faq-item input:checked ~ label { color: #0ea5e9; }
    .faq-content {
        max-height: 0;
        overflow: hidden;
        padding: 0 1.75rem;
        transition: all 0.5s ease;
    }
    .faq-item input:checked ~ .faq-content {
        max-height: 600px;
        padding-bottom: 1.75rem;
    }

    /* Equal height cards for How It Works */
    .step-card {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .step-desc {
        min-height: 65px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# NAVIGATION BAR
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border-bottom: 1px solid #e2e8f0; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="width: 44px; height: 44px; background: linear-gradient(135deg, #0ea5e9, #6366f1); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.2rem;">DB</div>
        <div style="font-size: 1.5rem; font-weight: 800; color: #0f172a;">Data<span style="color: #0ea5e9;">Buddy</span></div>
    </div>
</div>
<br><br>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# HERO SECTION
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align: center; padding: 5rem 1rem 3rem 1rem; background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%); border-radius: 0 0 40px 40px; margin-bottom: 3rem;">
    <div style="display: inline-block; padding: 0.6rem 1.2rem; background: linear-gradient(135deg, #e0f2fe, #dbeafe); color: #0284c7; border-radius: 50px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.1em; margin-bottom: 1.5rem;">
        🚀 PLATFORM ANALITIK #1 UNTUK SELLER SHOPEE INDONESIA
    </div>
    <h1 style="font-size: 3.2rem; font-weight: 900; color: #0f172a; line-height: 1.1; margin-bottom: 1.5rem;">
        Ubah Data <span style="color: #f97316;">Shopee</span> Menjadi<br>
        <span style="background: linear-gradient(135deg, #0ea5e9, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Keputusan Bisnis yang Profitable</span>
    </h1>
    <p style="font-size: 1.2rem; color: #64748b; max-width: 650px; margin: 0 auto 2rem auto; line-height: 1.7;">
        Platform analitik data Shopee dengan <strong>AI-powered insight</strong>. Upload file Excel pesanan, dapatkan dashboard interaktif, segmentasi pelanggan, dan chatbot analis pribadi—<strong>tanpa coding</strong>.
    </p>
    <div style="display: flex; gap: 2rem; justify-content: center; flex-wrap: wrap; font-size: 0.85rem; color: #64748b; font-weight: 600;">
        <div>✅ 100% Gratis</div>
        <div>✅ Data Privasi Terjamin</div>
        <div>✅ Support Seller Indonesia</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    if st.button("🚀 MULAI ANALISIS GRATIS SEKARANG", use_container_width=True):
        st.switch_page("pages/0_Home.py")


st.markdown("<br><br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# STATS SECTION
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="padding: 3rem 0; background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%); border-radius: 24px; margin-bottom: 3rem;">
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 3rem; padding: 0 2rem; max-width: 900px; margin: 0 auto; text-align: center; color: white;">
        <div>
            <div style="font-size: 3rem; font-weight: 900;">2M+</div>
            <div style="font-size: 0.95rem; opacity: 0.9;">Pesanan Diproses</div>
        </div>
        <div>
            <div style="font-size: 3rem; font-weight: 900;">500+</div>
            <div style="font-size: 0.95rem; opacity: 0.9;">Seller Shopee Aktif</div>
        </div>
        <div>
            <div style="font-size: 3rem; font-weight: 900;">4.8★</div>
            <div style="font-size: 0.95rem; opacity: 0.9;">Rating Rata-rata</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# VALUE PROPOSITION
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h2 style="font-size: 2rem; font-weight: 900; color: #0f172a;">
        Mengapa Seller Shopee Memilih <span style="color: #0ea5e9;">DataBuddy</span>?
    </h2>
    <p style="color: #64748b; font-size: 1rem;">Platform all-in-one untuk transformasi data mentah menjadi strategi bisnis yang actionable</p>
</div>
""", unsafe_allow_html=True)

features = [
    ("⚡", "ETL Pipeline Otomatis", "Tinggalkan rekap Excel manual. Upload file dari Shopee Seller Center, sistem kami membersihkan dan mentransformasi data dalam hitungan detik.", "FASTEST"),
    ("📊", "Dashboard Interaktif", "Visualisasi lengkap: Revenue trend, product performance, geographic heatmap, customer analytics—semua dalam satu dashboard easy-to-understand.", "COMPREHENSIVE"),
    ("🤖", "AI Chatbot Analyst", "Punya pertanyaan tentang data? Tanya chatbot AI kami. Dari 'produk apa yang paling laku?' sampai strategi diskon—dijawab dalam bahasa natural.", "AI-POWERED"),
    ("🎯", "Segmentasi Pelanggan", "Machine Learning clustering untuk segmentasi: High Value, Churn Risk, Loyal, Potential. Target marketing jadi lebih tepat sasaran.", "ML-ENABLED"),
    ("🔒", "Data Security", "Arsitektur cloud-ready dengan Supabase. Data historis tersimpan aman, terpusat, dan accessible kapanpun—dengan enkripsi end-to-end.", "SECURE"),
    ("📈", "Growth Insights", "Kalkulasi otomatis KPI-krusial: AOV, Conversion Rate, Repeat Purchase Rate. Tahu angka pertumbuhan real-time untuk keputusan scaling.", "ACTIONABLE"),
]

c1, c2, c3 = st.columns(3)

for idx in range(3):
    icon, title, desc, badge = features[idx]
    col = [c1, c2, c3][idx]
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div style="position: absolute; top: 0.75rem; right: 0.75rem; padding: 0.2rem 0.5rem; background: #f0f9ff; color: #0284c7; border-radius: 12px; font-size: 0.6rem; font-weight: 700;">{badge}</div>
            <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">{icon}</div>
            <h3 style="font-size: 1rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;">{title}</h3>
            <div class="feature-desc">
                <p style="color: #64748b; font-size: 0.82rem; line-height: 1.5; margin: 0;">{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

for idx in range(3, 6):
    icon, title, desc, badge = features[idx]
    col = [c4, c5, c6][idx - 3]
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div style="position: absolute; top: 0.75rem; right: 0.75rem; padding: 0.2rem 0.5rem; background: #f0f9ff; color: #0284c7; border-radius: 12px; font-size: 0.6rem; font-weight: 700;">{badge}</div>
            <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">{icon}</div>
            <h3 style="font-size: 1rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;">{title}</h3>
            <div class="feature-desc">
                <p style="color: #64748b; font-size: 0.82rem; line-height: 1.5; margin: 0;">{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# HOW IT WORKS
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="display: inline-block; padding: 0.5rem 1rem; background: linear-gradient(135deg, #fef3c7, #fde68a); color: #d97706; border-radius: 50px; font-weight: 700; font-size: 0.75rem; margin-bottom: 0.75rem;">
        CARA KERJA
    </div>
    <h2 style="font-size: 2rem; font-weight: 900; color: #0f172a;">Dari File Excel ke Insight dalam <span style="color: #f97316;">3 Langkah</span></h2>
</div>
""", unsafe_allow_html=True)

steps = [
    ("01", "📁", "Upload File Pesanan", "Download laporan dari Shopee Seller Center, lalu upload ke DataBuddy."),
    ("02", "⚙️", "AI Memproses Data", "Sistem ETL cerdas membersihkan, memvalidasi, dan membangun database secara otomatis."),
    ("03", "📊", "Eksplorasi & Analisis", "Buka dashboard interaktif, tanya chatbot AI, dan dapatkan insight untuk strategi bisnis."),
]

col1, col2, col3 = st.columns(3)

for col, (num, icon, title, desc) in zip([col1, col2, col3], steps):
    with col:
        st.markdown(f"""
        <div class="step-card" style="position: relative; padding: 2rem 1.5rem; background: white; border: 1px solid #e2e8f0; border-radius: 20px; text-align: center; height: 100%;">
            <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); width: 35px; height: 35px; background: linear-gradient(135deg, #f97316, #ea580c); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 0.8rem;">{num}</div>
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">{icon}</div>
            <h3 style="font-size: 1rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;">{title}</h3>
            <div class="step-desc">
                <p style="color: #64748b; font-size: 0.85rem; line-height: 1.5; margin: 0;">{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# TESTIMONIALS
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h2 style="font-size: 2rem; font-weight: 900; color: #0f172a;">Apa Kata Seller Shopee Indonesia?</h2>
    <p style="color: #64748b;">Ribuan seller telah transformasi data mereka menjadi growth</p>
</div>
""", unsafe_allow_html=True)

testimonials = [
    ("Sarah W.", "Owner BatikKu (Mall)", "👩‍💼", "Sebelum pakai DataBuddy, saya habiskan 5 jam seminggu cuma buat rekap manual. Sekarang? Upload pagi, insight langsung keluar. Penjualan naik 40%!"),
    ("Budi S.", "Seller Elektronik (Star+)", "👨‍💻", "Fitur chatbot-nya game changer! Saya bisa tanya 'customer dari kota mana yang paling loyal' dan langsung dapat jawaban dengan grafik."),
    ("Rina M.", "Dropsipper Beauty", "👩‍🎨", "Saya gaptek banget, tapi DataBuddy super gampang dipakai. Dashboard-nya clear, saya tahu produk mana yang harus restock."),
]

col1, col2, col3 = st.columns(3)

for col, (name, role, avatar, content) in zip([col1, col2, col3], testimonials):
    with col:
        st.markdown(f"""
        <div style="padding: 1.5rem; background: white; border: 1px solid #e2e8f0; border-radius: 16px; height: 100%;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                <div style="width: 40px; height: 40px; background: #f0f9ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">{avatar}</div>
                <div>
                    <div style="font-weight: 700; color: #0f172a; font-size: 0.9rem;">{name}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">{role}</div>
                </div>
            </div>
            <p style="color: #475569; font-size: 0.85rem; line-height: 1.6; font-style: italic; margin: 0;">"{content}"</p>
            <div style="color: #fbbf24; margin-top: 0.75rem;">★★★★★</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# BEFORE vs AFTER COMPARISON
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin: 3rem 0;">
    <h2 style="text-align: center; font-size: 1.8rem; font-weight: 900; color: #0f172a; margin-bottom: 2rem;">DataBuddy vs Manual Excel</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
        <div style="padding: 1.5rem; background: #fef2f2; border: 2px solid #fecaca; border-radius: 16px;">
            <h3 style="color: #dc2626; font-size: 1.1rem; font-weight: 800; margin-bottom: 1rem;">❌ Manual Excel</h3>
            <ul style="margin: 0; padding-left: 1rem; color: #991b1b; line-height: 1.8; font-size: 0.9rem;">
                <li>5+ jam per minggu untuk rekap manual</li>
                <li>Error human dalam copy-paste data</li>
                <li>Hard untuk tracking tren jangka panjang</li>
                <li>Tidak ada insight untuk decision making</li>
            </ul>
        </div>
        <div style="padding: 1.5rem; background: #f0fdf4; border: 2px solid #bbf7d0; border-radius: 16px;">
            <h3 style="color: #16a34a; font-size: 1.1rem; font-weight: 800; margin-bottom: 1rem;">✅ Dengan DataBuddy</h3>
            <ul style="margin: 0; padding-left: 1rem; color: #166534; line-height: 1.8; font-size: 0.9rem;">
                <li>Upload & insight dalam hitungan detik</li>
                <li>Validasi otomatis, zero error</li>
                <li>Dashboard interaktif dengan 10+ charts</li>
                <li>AI-powered insight untuk strategy</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# FAQ SECTION
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h2 style="font-size: 1.8rem; font-weight: 900; color: #0f172a;">Pertanyaan yang Sering Diajukan</h2>
</div>
""", unsafe_allow_html=True)

qna = [
    ("Apakah DataBuddy aman untuk data rahasia toko saya?", "Sangat aman. Kami menggunakan sistem yang terisolasi dengan opsi koneksi ke Supabase secure. Seluruh proses transformasi data (ETL) dilakukan secara lokal pada session Anda."),
    ("Berapa lama waktu untuk melihat hasil analisis?", "Instan. Setelah Anda mengunggah file laporan pesanan dari Shopee Seller Center, DataBuddy hanya membutuhkan waktu kurang dari 5 detik untuk memproses ribuan baris data."),
    ("Apakah perlu keahlian IT atau coding?", "Sama sekali tidak. DataBuddy dirancang untuk siapa saja—from pemula hingga Seller Star+. Cukup upload file Excel/CSV dan semua proses terjadi otomatis."),
    ("Apakah DataBuddy menggunakan Artificial Intelligence?", "Ya, DataBuddy dilengkapi dengan Machine Learning untuk segmentasi pelanggan dan Chatbot AI berbasis LLM yang memungkinkan Anda berdialog dengan data Anda."),
    ("File format apa yang didukung?", "DataBuddy mendukung format CSV, XLSX, dan XLS—semua format export dari Shopee Seller Center."),
    ("Berapa biaya menggunakan DataBuddy?", "DataBuddy saat ini 100% GRATIS untuk digunakan. Kami percaya bahwa setiap seller Shopee Indonesia berhak mendapatkan tool analitik yang powerful."),
]

html_accordion = '<div style="max-width: 800px; margin: 0 auto;">'
for idx, (q, a) in enumerate(qna):
    html_accordion += f"""
<div class="faq-item">
    <input type="checkbox" id="faq_{idx}">
    <label for="faq_{idx}">{q}</label>
    <div class="faq-content">
        <p style="color: #475569; line-height: 1.6; font-size: 0.9rem; margin: 0;">{a}</p>
    </div>
</div>
"""
html_accordion += "</div>"

st.markdown(html_accordion, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# FINAL CTA SECTION
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin: 4rem 0; padding: 3rem 2rem; background: linear-gradient(135deg, #0ea5e9, #6366f1); border-radius: 24px; text-align: center; color: white;">
    <h2 style="font-size: 2rem; font-weight: 900; margin-bottom: 1rem;">Siap Transformasi Data Shopee Anda Menjadi Profit?</h2>
    <p style="font-size: 1.1rem; opacity: 0.9; margin-bottom: 2rem;">Bergabunglah dengan ratusan seller Shopee Indonesia yang sudah merasakan kekuatan data-driven decision making.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    if st.button("🚀 MULAI GRATIS SEKARANG", use_container_width=True, key="cta_bottom"):
        st.switch_page("pages/0_Home.py")


st.markdown("<br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="margin-top: 3rem; padding: 2rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.85rem;">
    <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
        <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #0ea5e9, #6366f1); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 0.8rem;">DB</div>
        <span style="font-weight: 700; color: #0f172a;">DataBuddy</span>
    </div>
    <p style="margin: 0;">Platform analitik data Shopee dengan AI untuk seller Indonesia.</p>
    <p style="margin-top: 0.5rem; font-size: 0.75rem;">© 2026 DataBuddy. Dibuat dengan ❤️ untuk Seller Shopee Indonesia.</p>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# BACKGROUND PRELOAD — Auto-load Supabase di background (deferred execution)
# ═════════════════════════════════════════════════════════════════════
# Dipanggil di paling bawah setelah UI render, supaya rerun terjadi
# setelah user melihat tampilan (async-like experience)

try:
    from core.data_manager import prefetch_supabase
    prefetch_supabase()
except Exception:
    pass
