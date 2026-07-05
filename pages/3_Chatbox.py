"""
pages/3_Chatbox.py
Simple Chatbox dengan Qwen2.5:3B via Ollama
Tanpa konteks data dulu — basic Q&A
"""

# pyrefly: ignore [missing-import]
import streamlit as st
import requests
import os
import pandas as pd
from components.ui import render_navbar, COLORS, SPACING
from core.analytics_engine import AnalyticsEngine, get_bulan_name, format_rupiah

st.set_page_config(page_title="AI Chatbox | DataBuddy", page_icon="💬", layout="wide")

render_navbar()

st.markdown(f"""
<div style="margin-bottom: {SPACING['lg']};">
    <h1 style="
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        line-height: 1.2;
        letter-spacing: -0.02em;
    ">💬 Konsultan Data Pribadi</h1>
    <p style="color: #64748b; margin-top: 0.5rem; font-size: 1.15rem; font-weight: 400; line-height: 1.6;">
        Ngobrol santai seputar performa toko Anda dengan Senior Data Analyst AI 👨‍💻📈
    </p>
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# CONFIG
# ═════════════════════════════════════════════════════════════════════

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = "qwen2.5:3b"

# ZhipuAI / GLM
ZHIPUAI_API_KEY = os.environ.get("ZHIPUAI_API_KEY", "")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_MODEL = "glm-4-plus"

# Auto-detect: pake GLM kalau ada API key
USE_GLM = bool(ZHIPUAI_API_KEY)
MODEL = GLM_MODEL if USE_GLM else OLLAMA_MODEL

SYSTEM_PROMPT = """Anda Senior Data Analyst di DataBuddy (platform analitik Shopee Indonesia).
Bahasa Indonesia, jawab singkat-padat-actionable, poin-poin.

**Data SUDAH tersedia** — revenue, produk, pelanggan, lokasi, payment. Jangan minta data tambahan.

Aturan:
1. Jawab data-driven, bahasa awam
2. Beri insight bisnis actionable
3. Jika di luar topik (politik/sejarah/dll), tolak sopan
4. Siapa kamu? "Senior Data Analyst & Konsultan Bisnis AI di DataBuddy"
5. Siapa pembuat DataBuddy? "**Deni Romadhon**, S4 Ilmu Komputer, Universitas Cakrawala"
"""

# ═════════════════════════════════════════════════════════════════════
# ANALYTICS ENGINE INTEGRATION
# ═════════════════════════════════════════════════════════════════════

def query_analytics(question: str, df_master: pd.DataFrame | None) -> str | None:
    """
    Parse pertanyaan user dan jalankan query AnalyticsEngine yang sesuai.
    Return hasil dalam format yang mudah dibaca.
    """
    if df_master is None or df_master.empty:
        return "Maaf, belum ada data yang tersedia. Silakan upload data atau hubungikan ke Supabase terlebih dahulu."

    engine = AnalyticsEngine(df_master)
    q_lower = question.lower()

    try:
        # Mapping nama bulan ke angka (priority: nama lengkap dulu)
        bulan_map = {
            "januari": 1, "jan": 1, "1": 1,
            "februari": 2, "feb": 2, "2": 2,
            "maret": 3, "mar": 3, "3": 3,
            "april": 4, "apr": 4, "4": 4,
            "mei": 5, "may": 5, "5": 5,
            "juni": 6, "jun": 6, "6": 6,
            "juli": 7, "jul": 7, "7": 7,
            "agustus": 8, "aug": 8, "8": 8,
            "september": 9, "sep": 9, "9": 9,
            "oktober": 10, "oct": 10, "okt": 10, "10": 10,
            "november": 11, "nov": 11, "11": 11,
            "desember": 12, "dec": 12, "12": 12
        }

        # Detect bulan dari pertanyaan (check nama lengkap dulu, baru singkatan)
        bulan_number = None
        # Prioritaskan nama lengkap
        for bulan_name, bulan_num in bulan_map.items():
            if bulan_name in q_lower and len(bulan_name) > 3:  # Hanya match nama lengkap
                bulan_number = bulan_num
                break
        # Kalau tidak ada nama lengkap, cek singkatan
        if bulan_number is None:
            for bulan_name, bulan_num in bulan_map.items():
                if bulan_name in q_lower:
                    bulan_number = bulan_num
                    break

        # Revenue & Omzet
        if any(keyword in q_lower for keyword in ["omzet", "revenue", "pendapatan", "hasil", "cara", "jualan", "income", "pemasukan"]):
            # Jika ada spesifikasi bulan
            if bulan_number:
                tahun = df_master["tanggal_pesanan"].dt.year.max()  # type: ignore
                result = engine.revenue_per_bulan(tahun=tahun)

                if not result.empty:
                    bulan_data = result[result["bulan"] == bulan_number]
                    if not bulan_data.empty:
                        row = bulan_data.iloc[0]
                        response = f"""**Omset {get_bulan_name(bulan_number)} {tahun}:**

• Total Revenue: {row['revenue_fmt']}
• Total Orders: {row['orders']:,} pesanan
• Total Items: {row['qty']:,} items

**Insight:**
Ini adalah performa bulan {get_bulan_name(bulan_number)} dari total {len(result)} bulan yang ada di data. """
                        return response
                    else:
                        return f"Maaf, belum ada data untuk bulan {get_bulan_name(bulan_number)} {tahun}."

            # Jika tanya "per bulan" atau "bulanan" tanpa spesifik
            if any(keyword in q_lower for keyword in ["bulan", "per bulan", "bulanan", "tiap bulan"]):
                result = engine.revenue_per_bulan()
                if not result.empty:
                    response = "**Revenue Per Bulan (Semua Bulan):**\n\n"
                    for _, row in result.iterrows():
                        response += f"• {row['bulan_nama']} {row['tahun']}: {row['revenue_fmt']} ({row['orders']:,} orders, {row['qty']:,} items)\n"
                    response += f"\n**Total:** {len(result)} bulan tercatat dalam data."
                    return response

            if any(keyword in q_lower for keyword in ["vs", "banding", "bandingkan", "comparison", "compare"]):
                # Cari angka bulan (misal: "April vs Mei", "bulan 4 vs 5")
                import re
                numbers = re.findall(r'\b(\d+)\b', question)
                if len(numbers) >= 2:
                    bulan_a, bulan_b = int(numbers[0]), int(numbers[1])
                    # Detect tahun
                    tahun_match = re.search(r'20\d{2}', question)
                    tahun = int(tahun_match.group()) if tahun_match else df_master["tanggal_pesanan"].dt.year.max()  # type: ignore

                    comp = engine.revenue_bulanan_comparison(bulan_a, bulan_b, tahun)
                    return (
                        f"**Perbandingan {get_bulan_name(bulan_a)} vs {get_bulan_name(bulan_b)} {tahun}:**\n\n"
                        f"• Revenue {get_bulan_name(bulan_a)}: {format_rupiah(comp['revenue_a'])}\n"
                        f"• Revenue {get_bulan_name(bulan_b)}: {format_rupiah(comp['revenue_b'])}\n"
                        f"• Pertumbuhan: {comp['growth_percent']:+.1f}% ({format_rupiah(abs(comp['growth_absolute']))})\n"
                        f"• Insight: Tren **{comp['insight']}**"
                    )

        # Produk Terlaris
        if any(keyword in q_lower for keyword in ["produk laris", "produk paling laku", "best seller", "top produk", "produk terbaik", "apa yang laku"]):
            # Detect bulan
            import re
            bulan_match = re.search(r'(bulan|bulan ke|bln)\s*(\d+)', question)
            tahun_match = re.search(r'20\d{2}', question)

            if bulan_match:
                bulan = int(bulan_match.group(2))
                tahun = int(tahun_match.group()) if tahun_match else df_master["tanggal_pesanan"].dt.year.max()  # type: ignore

                result = engine.produk_terlaris_bulan(bulan, tahun, top_n=10)
                if not result.empty:
                    response = f"**Produk Terlaris {get_bulan_name(bulan)} {tahun}:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['product_name']}** ({row['product_variation']})\n"
                        response += f"   • Terjual: {row['qty']:,} items\n"
                        response += f"   • Revenue: {row['revenue_fmt']}\n"
                        response += f"   • Orders: {row['orders']:,}\n\n"
                    return response
            else:
                # All time
                result = engine.produk_performance_all_time(top_n=10)
                if not result.empty:
                    response = "**Produk Terlaris Sepanjang Waktu:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['product_name']}** ({row['product_variation']})\n"
                        response += f"   • Terjual: {row['qty']:,} items\n"
                        response += f"   • Revenue: {row['revenue_fmt']}\n\n"
                    return response

        # Produk Tidak Laris
        if any(keyword in q_lower for keyword in ["produk tidak laris", "produk ga laris", "produk sepi", "produk kurang laku", "butuh promo"]):
            import re
            bulan_match = re.search(r'(bulan|bulan ke|bln)\s*(\d+)', question)
            tahun_match = re.search(r'20\d{2}', question)

            if bulan_match:
                bulan = int(bulan_match.group(2))
                tahun = int(tahun_match.group()) if tahun_match else df_master["tanggal_pesanan"].dt.year.max()  # type: ignore

                result = engine.produk_tidak_laris(bulan, tahun, bottom_n=10)
                if not result.empty:
                    response = f"**Produk Kurang Laku {get_bulan_name(bulan)} {tahun}:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['product_name']}** ({row['product_variation']})\n"
                        response += f"   • Terjual: {row['qty']:,} items (rendah)\n"
                        response += f"   • Revenue: {row['revenue_fmt']}\n"
                        response += f"   • Butuh strategi promo untuk boost penjualan\n\n"
                    return response

        # Customer Analytics
        if any(keyword in q_lower for keyword in ["customer", "pelanggan", "top customer", "customer terbaik"]):
            import re
            bulan_match = re.search(r'(bulan|bulan ke|bln)\s*(\d+)', question)
            tahun_match = re.search(r'20\d{2}', question)

            if bulan_match:
                bulan = int(bulan_match.group(2))
                tahun = int(tahun_match.group()) if tahun_match else df_master["tanggal_pesanan"].dt.year.max()  # type: ignore

                result = engine.top_customers_bulan(bulan, tahun, top_n=10)
                if not result.empty:
                    response = f"**Top Customers {get_bulan_name(bulan)} {tahun}:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['customer_username']}**\n"
                        response += f"   • Total spent: {row['total_spent_fmt']}\n"
                        response += f"   • Orders: {row['total_orders']:,}\n"
                        response += f"   • Items: {row['total_items']:,}\n\n"
                    return response

        # Geographic Performance
        if any(keyword in q_lower for keyword in ["provinsi", "daerah", "kota", "wilayah", "area"]):
            if "provinsi" in q_lower:
                result = engine.performance_per_provinsi()
                if not result.empty:
                    response = "**Performance per Provinsi:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['province']}**\n"
                        response += f"   • Revenue: {row['revenue_fmt']}\n"
                        response += f"   • Orders: {row['orders']:,}\n"
                        response += f"   • Customers: {row['customers']:,}\n\n"
                    return response

            if "kota" in q_lower:
                result = engine.performance_per_kota(top_n=15)
                if not result.empty:
                    response = "**Top 15 Kota berdasarkan Revenue:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['city']}**, {row['province']}\n"
                        response += f"   • Revenue: {row['revenue_fmt']}\n"
                        response += f"   • Orders: {row['orders']:,}\n\n"
                    return response

        # Customer Retention
        if any(keyword in q_lower for keyword in ["retensi", "retention", "balik lagi", "repeat", "kembali"]):
            stats = engine.customer_retention()
            return (
                "**Statistik Customer Retention:**\n\n"
                f"• Total Customers: {stats['total_customers']:,}\n"
                f"• Repeat Buyers: {stats['repeat_buyers']:,}\n"
                f"• One-time Buyers: {stats['one_time_buyers']:,}\n"
                f"• Repeat Rate: {stats['repeat_rate']}%\n\n"
                f"**Insight:** Dari {stats['total_customers']:,} customer, {stats['repeat_buyers']:,} "
                f"({stats['repeat_rate']}%) sudah belanja lagi. Ini menunjukkan loyalitas customer yang "
                f"{'sangat baik' if stats['repeat_rate'] > 30 else 'perlu ditingkatkan' if stats['repeat_rate'] > 15 else 'perlu perhatian serius'}."
            )

        # Payment Method Performance
        if any(keyword in q_lower for keyword in ["metode pembayaran", "payment", "cod", "transfer", "shopeepay"]):
            result = engine.performance_per_payment_method()
            if not result.empty:
                response = "**Performance per Metode Pembayaran:**\n\n"
                for i, (_, row) in enumerate(result.iterrows()):
                    response += f"{i+1}. **{row['payment_method']}**\n"
                    response += f"   • Orders: {row['orders']:,}\n"
                    response += f"   • Revenue: {row['revenue_fmt']}\n"
                    response += f"   • AOV: {row['aov_fmt']}\n\n"
                return response

        # Best Jam & Hari
        if any(keyword in q_lower for keyword in ["jam", "prime time", "paling ramai", "peak hour"]):
            result = engine.best_jam_penjualan()
            if not result.empty:
                response = "**Jam Paling Ramai Order:**\n\n"
                for i, row in result.head(5).iterrows():
                    response += f"• Jam {row['jam']:02d}:00 - {row['orders']:,} orders ({row['revenue_fmt']})\n"
                response += "\n**Insight:** Fokuskan promo & flash sale di jam-jam ramai ini untuk maksimalkan konversi."
                return response

        if any(keyword in q_lower for keyword in ["hari", "weekday", "weekend"]):
            result = engine.best_hari_penjualan()
            if not result.empty:
                response = "**Performance per Hari:**\n\n"
                for i, (_, row) in enumerate(result.iterrows()):
                    response += f"• {row['hari']}: {row['orders']:,} orders ({row['revenue_fmt']})\n"

                max_day = result.loc[result['orders'].idxmax()]['hari']
                response += f"\n**Insight:** Hari **{max_day}** adalah hari paling ramai. Pertimbangkan untuk schedule promo di hari ini."
                return response

        # Monthly Summary
        if any(keyword in q_lower for keyword in ["summary", "ringkasan", "performa bulan", "gimana bulan"]):
            import re
            bulan_match = re.search(r'(bulan|bulan ke|bln)\s*(\d+)', question)
            tahun_match = re.search(r'20\d{2}', question)

            if bulan_match:
                bulan = int(bulan_match.group(2))
                tahun = int(tahun_match.group()) if tahun_match else df_master["tanggal_pesanan"].dt.year.max()  # type: ignore

                summary = engine.monthly_summary(bulan, tahun)
                return (
                    f"**Ringkasan Performa {get_bulan_name(bulan)} {tahun}:**\n\n"
                    f"• Total Revenue: {summary['total_revenue_fmt']}\n"
                    f"• Total Orders: {summary['total_orders']:,}\n"
                    f"• Total Customers: {summary['total_customers']:,}\n"
                    f"• Total Items Sold: {summary['total_qty']:,}\n"
                    f"• Average Order Value (AOV): {summary['aov_fmt']}\n\n"
                    f"• **Top Product:** {summary['top_product']}\n"
                    f"• **Top City:** {summary['top_city']}\n\n"
                    f"**Payment Distribution:**\n"
                + "\n".join([f"   • {method}: {count} orders" for method, count in summary['payment_distribution'].items()])
                )

        # Jika tidak match dengan query manapun
        return None

    except Exception as e:
        return f"Maaf, terjadi error saat menjawab pertanyaan: {str(e)}\n\nCoba tanya dengan cara yang berbeda atau lebih spesifik."

# ═════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []

# Load data untuk analytics
df_master = None
if "etl_tables" in st.session_state and st.session_state["etl_tables"]:
    try:
        from core.data_manager import build_master
        tables = st.session_state["etl_tables"]
        df_master = build_master(tables)
    except:
        pass

# ═════════════════════════════════════════════════════════════════════
# SIDEBAR - SETTINGS
# ═════════════════════════════════════════════════════════════════════

# Settings panel - Hide by default untuk clean UI
with st.sidebar:
    with st.expander("⚙️ Settings", expanded=False):
        provider = "🧠 GLM (cloud)" if USE_GLM else "🦙 Ollama (lokal)"
        st.markdown(f"**Provider:** {provider}")
        st.markdown(f"**Model:** {MODEL}")
        if not USE_GLM:
            st.markdown(f"🧠 **Context:** 4K (optimasi)")
        st.markdown(f"🎯 **Max Response:** 1.536 tokens")
        st.markdown(f"🌡️ **Temperature:** 0.7")

        st.markdown("---")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.markdown("""
        ### 📝 Tips
        - Tanya spesifik seputar data toko
        - Contoh: "berapa revenue bulan Juni?"
        - "produk apa yang paling laku?"
        - Chat history tersimpan selama session
        """)

# ═════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ═════════════════════════════════════════════════════════════════════

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ═════════════════════════════════════════════════════════════════════
# USER INPUT & ML CONTEXT
# ═════════════════════════════════════════════════════════════════════

ml_context = st.session_state.pop("ai_ml_context", None)
user_input = st.chat_input("Tanya apa saja seputar data toko Anda...")

# Build system info about available data
data_overview = ""
if df_master is not None and not df_master.empty:
    min_date = df_master["tanggal_pesanan"].min()
    max_date = df_master["tanggal_pesanan"].max()
    total_orders = df_master["order_id"].nunique()
    total_customers = df_master["customer_id"].nunique()
    total_revenue = df_master[df_master["is_completed"] == 1]["valid_item_revenue"].sum()

    data_overview = f"""
**DATA YANG TERSEDIA:**
• Periode: {min_date.strftime('%d %B %Y')} s.d. {max_date.strftime('%d %B %Y')}
• Total Orders: {total_orders:,}
• Total Customers: {total_customers:,}
• Total Revenue: Rp {total_revenue:,.0f}

Data ini SUDAH LENGKAP dan SIAP Dianalisis. Anda tidak perlu minta data tambahan - cukup tanya spesifik metrik/bulan/produk yang ingin dilihat.
"""

# Prioritaskan ML context, lalu cek apakah user input pertanyaan analytics
prompt = ml_context or user_input

# Jika ada user input, cek apakah pertanyaan analytics
if user_input and not ml_context:
    analytics_result = query_analytics(user_input, df_master)
    if analytics_result:
        # Jika berhasil query analytics, gunakan hasilnya saja (tanpa data overview total)
        prompt = f"[JAWABAN ANALITICS SPESIFIK]\n{analytics_result}\n\n[PERTANYAAN USER]\n{user_input}\n\nBerdasarkan data spesifik di atas, tolong jelaskan dengan bahasa yang mudah dipahami dan berikan insight bisnis yang actionable. JANGAN tambahkan data lain di luar yang sudah disediakan."
    else:
        # Jika bukan pertanyaan analytics atau query gagal, baru inject data overview
        if data_overview:
            prompt = f"{data_overview}\n\n[PERTANYAAN USER]\n{user_input}"
        else:
            prompt = user_input

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(user_input if user_input else "📊 Data Analytics Context")

    # Prepare messages for Ollama API
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner(f"{'🧠 GLM' if USE_GLM else '🦙 Ollama'} Menganalisis..."):
            try:
                if USE_GLM:
                    # ── GLM (ZhipuAI) ────────────────────────────────
                    response = requests.post(
                        GLM_API_URL,
                        headers={
                            "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": GLM_MODEL,
                            "messages": api_messages,
                            "stream": False,
                            "max_tokens": 1536,
                            "temperature": 0.7,
                        },
                        timeout=60
                    )
                    response.raise_for_status()
                    result = response.json()
                    assistant_message = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    # ── Ollama (lokal) ────────────────────────────────
                    response = requests.post(
                        OLLAMA_URL,
                        json={
                            "model": OLLAMA_MODEL,
                            "messages": api_messages,
                            "stream": False,
                            "options": {
                                "temperature": 0.7,
                                "num_predict": 1536,
                                "num_ctx": 4096,
                            }
                        },
                        timeout=300
                    )
                    response.raise_for_status()
                    result = response.json()
                    assistant_message = result.get("message", {}).get("content", "Maaf, ada error saat membaca response dari model.")

            except requests.exceptions.ConnectionError:
                if USE_GLM:
                    assistant_message = "❌ **GLM API tidak terkoneksi.** Cek koneksi internet VPS."
                else:
                    assistant_message = "❌ **Ollama tidak terkoneksi.** Pastikan Ollama service jalan."

            except Exception as e:
                assistant_message = f"❌ **Error:** {e}"

        st.markdown(assistant_message)

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
