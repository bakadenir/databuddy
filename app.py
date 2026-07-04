"""
DataBuddy — Landing Page (SEO & Seller Focus)
"""

import streamlit as st
from components.ui import render_navbar, section_header, COLORS, SPACING

st.set_page_config(
    page_title="DataBuddy — Shopee Analytics & SEO Optimizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_navbar()

# Hide sidebar entirely on Landing Page
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── 0. TOP BRANDING HEADER ────────────────────────────────────────
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; margin-bottom: 2.5rem;">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="width: 42px; height: 42px; background: linear-gradient(135deg, #0ea5e9, #6366f1); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.2rem; box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3);">DB</div>
        <div style="font-size: 1.6rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">Data<span style="color: #0ea5e9;">Buddy</span></div>
    </div>
    <div style="font-size: 0.95rem; font-weight: 600; color: #64748b; display: none; @media (min-width: 768px) { display: block; }">
        Shopee Analytics & Science Assistant
    </div>
</div>
""", unsafe_allow_html=True)

# ── 1. HERO SECTION ───────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 4rem 1rem; background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%); border-radius: 24px; margin-bottom: 3rem;">
    <div style="display: inline-block; padding: 0.5rem 1rem; background: #e0f2fe; color: #0284c7; border-radius: 50px; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; margin-bottom: 1.5rem;">
        🚀 SHOPEE SELLER DATA INTELLIGENCE
    </div>
    <h1 style="font-size: 3.5rem; font-weight: 900; color: #0f172a; line-height: 1.2; margin-bottom: 1.5rem; max-width: 800px; margin-left: auto; margin-right: auto;">
        Ubah Data <span style="color: #f97316;">Shopee</span> Menjadi <br>
        <span style="background: linear-gradient(135deg, #0ea5e9, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Keputusan Bisnis Strategis</span>
    </h1>
    <p style="font-size: 1.25rem; color: #475569; max-width: 700px; margin: 0 auto 2.5rem auto; line-height: 1.6;">
        <strong>DataBuddy</strong> adalah Asisten Data Analyst berteknologi AI yang dirancang khusus untuk Seller Shopee. Tidak perlu repot merekrut ahli data profesional—cukup unggah data pesanan, dan biarkan fitur interaktif AI Chatbot kami meracik strategi, membaca tren, dan menjawab semua pertanyaan bisnis Anda secara instan.
    </p>
</div>
""", unsafe_allow_html=True)

# Call to Action Button
st.markdown("""
<style>
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
    color: white !important;
    padding: 1.25rem 3rem !important;
    border-radius: 50px !important;
    font-weight: 800 !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(249, 115, 22, 0.4) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(249, 115, 22, 0.6) !important;
    color: white !important;
    border: none !important;
}
div[data-testid="stButton"] p {
    font-size: 1.25rem !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    if st.button("🚀 MULAI OPTIMASI TOKO SEKARANG", use_container_width=True):
        st.switch_page("pages/0_Home.py")
        
st.markdown("<br><br>", unsafe_allow_html=True)


# ── 2. VALUE PROPOSITION (Mengapa DataBuddy?) ─────────────────────
section_header("Mengapa DataBuddy?", "💡", "Keunggulan kompetitif untuk ekosistem bisnis Anda")

vp = [
    {"title": "Automated ETL", "icon": "⚡", "desc": "Tinggalkan rekap Excel manual. Sistem cerdas kami membersihkan, memvalidasi, dan merombak raw data Shopee Anda dalam hitungan detik."},
    {"title": "Actionable Insights", "icon": "📈", "desc": "Dashboard komprehensif yang menampilkan metrik paling krusial: Revenue, AOV, dan Conversion Rate secara real-time."},
    {"title": "AI & ML Powered", "icon": "🤖", "desc": "Lebih dari sekadar grafik. Dilengkapi algoritma Clustering (Segmentasi) dan LLM Chatbot cerdas layaknya analis pribadi."},
    {"title": "Enterprise Security", "icon": "🔒", "desc": "Arsitektur cloud-ready dengan Supabase memastikan data historis puluhan ribu order tersimpan aman dan terpusat."}
]

c1, c2, c3, c4 = st.columns(4)
for col, v in zip([c1, c2, c3, c4], vp):
    with col:
        st.markdown(f"""
        <div style="padding: 2rem 1.5rem; background: white; border: 1px solid #e2e8f0; border-radius: 20px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: transform 0.3s ease;" onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">{v['icon']}</div>
            <h3 style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 0.75rem;">{v['title']}</h3>
            <p style="color: #64748b; font-size: 0.95rem; line-height: 1.6;">{v['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)


# ── 3. Q&A / FAQ SECTION (SEO Optimized) ────────────────────────
section_header("Pertanyaan Seputar DataBuddy (Q&A)", "❓", "Jawaban untuk pertanyaan yang paling sering dicari Seller Shopee")

qna = [
    ("Apakah aplikasi ini aman untuk data rahasia toko saya?", "Sangat aman. Kami mengimplementasikan sistem yang terisolasi dan opsional terhubung dengan Supabase. Proses transformasi data (ETL) dilakukan secara terenkripsi dan tidak ada data penjualan yang dibagikan ke pihak ketiga tanpa izin."),
    ("Berapa lama waktu untuk melihat hasil optimasi analisis?", "Instan. Sejak Anda mengunggah laporan pesanan Excel dari Shopee Seller Center, DataBuddy hanya membutuhkan waktu kurang dari 5 detik untuk memproses ribuan baris data menjadi Dashboard Interaktif ala Top Seller."),
    ("Apakah aplikasi ini menggunakan Artificial Intelligence (AI)?", "Ya, DataBuddy selangkah lebih maju. Kami memiliki integrasi fitur Machine Learning untuk Segmentasi Pelanggan (RFM Analysis) dan Chatbot cerdas berbasis LLM yang memungkinkan Anda 'mengobrol' untuk merancang strategi pemasaran toko."),
    ("Apakah kami memerlukan ahli IT atau analis khusus?", "Sama sekali tidak. Interface DataBuddy dirancang seintuitif mungkin. Mulai dari pemula hingga Seller Star+ dapat mengoperasikannya cukup dengan metode Point-and-Click dan Drag-and-Drop file Excel pesanan."),
    ("Bagaimana dengan kemampuan memproses toko pesanan besar?", "Arsitektur database relasional kami sangat mendukung pengelolaan jutaan baris data pesanan dengan sangat cepat. Cocok untuk scale-up toko dari level menengah hingga level Mall.")
]

html_accordion = """
<style>
.faq-item {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    overflow: hidden;
    transition: all 0.2s ease;
}
.faq-item:hover {
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
.faq-item input[type="radio"] {
    display: none;
}
.faq-item label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    font-weight: 700;
    font-size: 1.05rem;
    color: #0f172a;
    cursor: pointer;
    margin: 0;
}
.faq-item label::after {
    content: '+';
    font-size: 1.5rem;
    font-weight: 400;
    color: #64748b;
    transition: transform 0.3s ease;
}
.faq-item input:checked ~ label::after {
    content: '−';
    transform: rotate(180deg);
}
.faq-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease-out, padding 0.4s ease;
    padding: 0 1.5rem;
}
.faq-item input:checked ~ .faq-content {
    max-height: 500px;
    padding-bottom: 1.5rem;
}
.faq-content p {
    margin: 0;
    color: #475569;
    line-height: 1.6;
    font-size: 0.95rem;
}
</style>
<div>
"""
for idx, (q, a) in enumerate(qna):
    html_accordion += f"""
<div class="faq-item">
    <input type="radio" name="faq_radio" id="faq_{idx}">
    <label for="faq_{idx}">{q}</label>
    <div class="faq-content">
        <p>{a}</p>
    </div>
</div>
"""
html_accordion += "</div>"

st.markdown(html_accordion, unsafe_allow_html=True)

# ── 4. FOOTER ───────────────────────────────────────────────────
st.markdown("""
<div style="margin-top: 5rem; padding: 2rem 0; border-top: 1px solid #e2e8f0; text-align: center; color: #94a3b8; font-size: 0.9rem;">
    <strong>DataBuddy</strong> © 2026. The Next-Gen Shopee Analytics Platform.<br>
    <span style="font-size: 0.8rem;">Didesain eksklusif untuk akselerasi performa penjualan dan optimasi toko e-commerce Anda.</span>
</div>
""", unsafe_allow_html=True)
