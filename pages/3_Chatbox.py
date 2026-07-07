"""
pages/3_Chatbox.py
Simple Chatbox dengan Qwen2.5:3B via Ollama
Tanpa konteks data dulu — basic Q&A
"""

# pyrefly: ignore [missing-import]
import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv(override=True)
import pandas as pd
from components.ui import render_navbar, render_sidebar_footer, COLORS, SPACING
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

st.markdown("""
<style>
/* CSS: User rata kanan, Assistant rata kiri (Tanpa Background) */

/* 0. Paksa seluruh container dan chat message menggunakan lebar 75% layar (sekitar 1050px) agar proporsional */
div[data-testid="stAppViewBlockContainer"], 
div[data-testid="block-container"], 
.main .block-container,
.block-container,
.stMainBlockContainer {
    max-width: 1050px !important;
}

/* 0.5. Tahan juga kotak pengetikan di bawah (Chat Input) agar tidak kebablasan melebar 1400px */
div[data-testid="stChatInput"],
.stChatFloatingInputContainer {
    max-width: 1050px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

div[data-testid="stChatMessage"] {
    max-width: 100% !important;
}

/* 1. Balik posisi Avatar dan Teks untuk User */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse;
}

/* 2. Rata kanan untuk container pesan User */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:nth-child(2),
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) > div:nth-child(2) {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    padding-right: 1rem;
    padding-left: 0;
}

/* 3. Pastikan semua teks di dalam markdown User rata kanan */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] *,
div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] * {
    text-align: right;
}
</style>
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
Anda adalah sosok analis yang pandai bercerita (storytelling) dan ramah. Berikan penjelasan yang komprehensif, menarik, dan tidak kaku (jangan cuma bullet points). Jelaskan "mengapa" di balik data, berikan konteks, dan sajikan insight layaknya menceritakan sebuah narasi bisnis yang seru kepada pemilik toko. Gunakan gaya bahasa yang kasual, suportif, antusias, namun tetap profesional.

**ATURAN KERAS (ANTI-HALUSINASI):**
1. JANGAN PERNAH mengarang angka, memprediksi masa depan, atau memberikan data palsu.
2. HANYA gunakan angka yang dikirimkan kepada Anda di dalam [Konteks Data].
3. Jika Anda tidak melihat angka atau data spesifik yang ditanyakan di dalam [Konteks Data], TOLAK DENGAN SOPAN dan katakan bahwa Anda belum memiliki data tersebut. JANGAN membuat tebakan.

**KONTOKS BISNIS & STRATEGI UTAMA:**
Toko ini menjual **PRODUK KOPI**. Gunakan pengetahuan ini saat memberikan insight atau contoh (misal: tren penikmat kopi, perilaku pembelian produk kopi, "grind size", "brewing method") untuk membuat cerita Anda lebih relevan dan hidup.

PENTING: Strategi utama toko saat ini adalah memindahkan pelanggan bernilai tinggi ("high-value" / pembeli setia) ke *direct sales* (penjualan langsung via WhatsApp atau Website Pribadi). Tujuannya adalah untuk menghindari potongan pajak dan biaya admin *marketplace* yang semakin mahal. Jika Anda melihat peluang dari data pelanggan (misalnya: pelanggan dengan transaksi besar atau sering belanja), selipkan saran untuk menarik mereka ke *direct sales*!

**KONTEKS OPERASIONAL TOKO & KAMPANYE (SANGAT PENTING):**
1. **Jam & Hari Kerja:** Toko beroperasi dari hari **Senin hingga Sabtu**, jam 08:00 Pagi hingga 17:00 Sore.
2. **Hari Libur:** Toko TUTUP setiap Hari Minggu dan Tanggal Merah (Libur Nasional).
3. **Kebijakan Pengiriman:** Pesanan yang masuk di luar jam kerja (malam hari) ATAU masuk di hari libur (Minggu/Tanggal Merah) baru akan diproses, digarap, dan dikirimkan pada **hari kerja berikutnya**.
4. **Kampanye Promo:** Toko rutin mengadakan diskon/promo pada "Tanggal Kembar" (misal: 4.4, 5.5, 6.6), masa "Payday" (tanggal 25 ke atas saat gajian), dan event "Flash Sale".
Gunakan konteks ini untuk menganalisis data, misalnya: "Wajar jika pengiriman menumpuk di hari Senin karena akumulasi pesanan hari Minggu," atau "Lonjakan omzet di awal bulan dan akhir bulan terjadi berkat efek Payday (Gajian) dan promo Tanggal Kembar."

**KESADARAN FITUR APLIKASI (APP AWARENESS):**
Jika user menanyakan hal-hal kompleks terkait:
- Rekomendasi pasangan barang / paket diskon
- Mencari pelanggan VIP / Sultan / Segmentasi Loyalitas
- Memprediksi atau meramal omzet bulan depan
NAMUN belum ada data/angka yang terlampir di konteks Anda, arahkan user dengan sopan untuk membuka menu **"🎯 Strategi"** di panel samping (*sidebar*). Beri tahu mereka bahwa di sana terdapat fitur khusus (Bundling, Clustering, dan Forecasting) yang dirancang untuk hal tersebut. Minta mereka untuk menjalankan fiturnya dan mengeklik tombol "🤖 Diskusikan dengan AI Data Analyst" di sana agar Anda mendapatkan data yang akurat untuk dianalisis.

Jika user sekadar menyapa, sapa balik dengan antusias sebagai DataBuddy Assistant.
"""

# ═════════════════════════════════════════════════════════════════════
# ANALYTICS ENGINE INTEGRATION
# ═════════════════════════════════════════════════════════════════════

def detect_intent_with_llm(user_input: str, context_intent: str) -> dict:
    import json
    
    system_prompt = """Anda adalah Intent Classifier (Pemilih Rumus) untuk asisten data.
Tugas Anda HANYA membalas dengan objek JSON valid. Jangan tambahkan teks lain.

Kategori intent yang tersedia:
- "revenue": total omzet/pendapatan, cuan, pemasukan
- "revenue_compare": membandingkan pendapatan antar dua bulan
- "top_products": produk terlaris, laku keras, juara
- "bottom_products": produk tidak laris, tidak perform, ampas, sepi, jelek
- "customers": pelanggan terbaik, pembeli setia
- "geography": performa wilayah/provinsi/kota
- "retention": retensi pelanggan/repeat order
- "payment": metode pembayaran
- "time_analysis": jam atau hari terbaik, prime time
- "summary": ringkasan performa secara umum/laporan
- "greeting": percakapan ringan, sapaan (halo, hai, selamat pagi)

Format JSON yang diwajibkan:
{
  "intent": "nama_intent_atau_null",
  "month_number_1": angka_bulan_ke_1_atau_null,
  "month_number_2": angka_bulan_ke_2_atau_null_jika_compare,
  "year": angka_tahun_atau_null
}

Catatan:
- Konversikan nama bulan ke angka (Januari=1, Februari=2, dst).
- Jika ada 2 bulan untuk dibandingkan, isi month_number_1 dan month_number_2.
- Jika pengguna hanya menyapa, gunakan intent "greeting".
"""
    combined_q = f"Konteks obrolan sebelumnya: {context_intent}\nPertanyaan sekarang: {user_input}" if context_intent else f"Pertanyaan: {user_input}"
    api_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": combined_q}
    ]
    
    try:
        if USE_GLM:
            response = requests.post(
                GLM_API_URL,
                headers={"Authorization": f"Bearer {ZHIPUAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": GLM_MODEL, "messages": api_messages, "stream": False, "temperature": 0.0},
                timeout=10
            )
            response.raise_for_status()
            res_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            response = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "messages": api_messages, "stream": False, "format": "json", "options": {"temperature": 0.0}},
                timeout=15
            )
            response.raise_for_status()
            res_text = response.json().get("message", {}).get("content", "")
            
        res_text = res_text.strip()
        if res_text.startswith("```json"):
            res_text = res_text[7:]
        if res_text.startswith("```"):
            res_text = res_text[3:]
        if res_text.endswith("```"):
            res_text = res_text[:-3]
            
        return json.loads(res_text.strip())
    except Exception as e:
        print("Error LLM Intent:", e)
        return {"intent": "unknown", "month_number_1": None, "month_number_2": None, "year": None}

def query_analytics(question: str, df_master: pd.DataFrame | None, context_intent: str = "") -> str | None:
    if df_master is None or df_master.empty:
        return "Maaf, belum ada data yang tersedia. Silakan upload data."

    try:
        from core.analytics_engine import AnalyticsEngine, get_bulan_name, format_rupiah
        engine = AnalyticsEngine(df_master)
        
        # --- LLM ROUTER PASS 1 ---
        intent_data = detect_intent_with_llm(question, context_intent)
        best_intent = intent_data.get("intent")
        
        if best_intent in ["greeting", "unknown", None]:
            return None
            
        bulan_number = intent_data.get("month_number_1")
        if not isinstance(bulan_number, int):
            bulan_number = None
            
        tahun = intent_data.get("year")
        if not isinstance(tahun, int):
            import datetime
            tahun = df_master["tanggal_pesanan"].dt.year.max() # type: ignore
            
        if best_intent == "revenue_compare":
            bulan_a = intent_data.get("month_number_1")
            bulan_b = intent_data.get("month_number_2")
            if isinstance(bulan_a, int) and isinstance(bulan_b, int):
                comp = engine.revenue_bulanan_comparison(bulan_a, bulan_b, tahun)
                return (
                    f"**Perbandingan {get_bulan_name(bulan_a)} vs {get_bulan_name(bulan_b)} {tahun}:**\n\n"
                    f"• Revenue {get_bulan_name(bulan_a)}: {format_rupiah(comp['revenue_a'])}\n"
                    f"• Revenue {get_bulan_name(bulan_b)}: {format_rupiah(comp['revenue_b'])}\n"
                    f"• Pertumbuhan: {comp['growth_percent']:+.1f}% ({format_rupiah(abs(comp['growth_absolute']))})\n"
                    f"• Insight: Tren **{comp['insight']}**"
                )
            else:
                best_intent = "revenue"
                
        if best_intent == "revenue":
            if bulan_number:
                result = engine.revenue_per_bulan(tahun=tahun)
                if not result.empty:
                    bulan_data = result[result["bulan"] == bulan_number]
                    if not bulan_data.empty:
                        row = bulan_data.iloc[0]
                        return f"**Omzet {get_bulan_name(bulan_number)} {tahun}:**\n\n• Total Revenue: {row['revenue_fmt']}\n• Total Orders: {row['orders']:,} pesanan\n• Total Items: {row['qty']:,} items\n\n**Insight:** Ini adalah performa bulan {get_bulan_name(bulan_number)}."
                    else:
                        return f"Maaf, belum ada data untuk bulan {get_bulan_name(bulan_number)} {tahun}."
            else:
                result = engine.revenue_per_bulan()
                if not result.empty:
                    response = "**Revenue Per Bulan (Semua Bulan):**\n\n"
                    for _, row in result.iterrows():
                        response += f"• {row['bulan_nama']} {row['tahun']}: {row['revenue_fmt']} ({row['orders']:,} orders)\n"
                    return response

        elif best_intent == "top_products":
            if bulan_number:
                result = engine.produk_terlaris_bulan(bulan_number, tahun, top_n=10)
                if not result.empty:
                    response = f"**Produk Terlaris {get_bulan_name(bulan_number)} {tahun}:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['product_name']}** ({row['product_variation']})\n   • Terjual: {row['qty']:,} items\n   • Revenue: {row['revenue_fmt']}\n"
                    return response
            else:
                result = engine.produk_performance_all_time(top_n=10)
                if not result.empty:
                    response = "**Produk Terlaris Sepanjang Waktu:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['product_name']}** ({row['product_variation']})\n   • Terjual: {row['qty']:,} items\n   • Revenue: {row['revenue_fmt']}\n"
                    return response

        elif best_intent == "bottom_products":
            if bulan_number:
                result = engine.produk_tidak_laris(bulan_number, tahun, bottom_n=10)
                if not result.empty:
                    response = f"**Produk Kurang Laku {get_bulan_name(bulan_number)} {tahun}:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['product_name']}** ({row['product_variation']})\n   • Terjual: {row['qty']:,} items (rendah)\n   • Revenue: {row['revenue_fmt']}\n"
                    return response
            else:
                return "Mohon sebutkan bulan spesifik untuk melihat produk yang kurang perform (contoh: 'produk bapuk di bulan april')."

        elif best_intent == "customers":
            if bulan_number:
                result = engine.top_customers_bulan(bulan_number, tahun, top_n=10)
                if not result.empty:
                    response = f"**Top Customers {get_bulan_name(bulan_number)} {tahun}:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['customer_username']}**\n   • Total spent: {row['total_spent_fmt']}\n   • Orders: {row['total_orders']:,}\n"
                    return response
            else:
                return "Mohon sebutkan bulan spesifik untuk melihat top customer."

        elif best_intent == "geography":
            if "kota" in question.lower():
                result = engine.performance_per_kota(top_n=15)
                if not result.empty:
                    response = "**Top 15 Kota berdasarkan Revenue:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['city']}**, {row['province']} - {row['revenue_fmt']} ({row['orders']:,} orders)\n"
                    return response
            else:
                result = engine.performance_per_provinsi()
                if not result.empty:
                    response = "**Performance per Provinsi:**\n\n"
                    for i, (_, row) in enumerate(result.iterrows()):
                        response += f"{i+1}. **{row['province']}** - {row['revenue_fmt']} ({row['orders']:,} orders)\n"
                    return response

        elif best_intent == "retention":
            stats = engine.customer_retention()
            return (
                f"**Statistik Customer Retention:**\n\n"
                f"• Total Customers: {stats['total_customers']:,}\n"
                f"• Repeat Buyers: {stats['repeat_buyers']:,}\n"
                f"• Repeat Rate: {stats['repeat_rate']}%\n\n"
                f"**Insight:** Loyalitas customer {'sangat baik' if stats['repeat_rate'] > 30 else 'perlu ditingkatkan'}."
            )

        elif best_intent == "payment":
            result = engine.performance_per_payment_method()
            if not result.empty:
                response = "**Performance per Metode Pembayaran:**\n\n"
                for i, (_, row) in enumerate(result.iterrows()):
                    response += f"{i+1}. **{row['payment_method']}** - {row['revenue_fmt']} ({row['orders']:,} orders)\n"
                return response

        elif best_intent == "time_analysis":
            if "jam" in question.lower() or "prime time" in question.lower() or "sibuk" in question.lower():
                result = engine.best_jam_penjualan()
                response = "**Jam Paling Ramai Order:**\n\n"
                for i, row in result.head(5).iterrows():
                    response += f"• Jam {row['jam']:02d}:00 - {row['orders']:,} orders ({row['revenue_fmt']})\n"
                return response
            else:
                result = engine.best_hari_penjualan()
                response = "**Performance per Hari:**\n\n"
                for i, (_, row) in enumerate(result.iterrows()):
                    response += f"• {row['hari']}: {row['orders']:,} orders ({row['revenue_fmt']})\n"
                return response

        elif best_intent == "summary":
            bln = bulan_number if bulan_number else df_master["tanggal_pesanan"].dt.month.max() # type: ignore
            summary = engine.monthly_summary(bln, tahun)
            return (
                f"**Ringkasan Performa {get_bulan_name(bln)} {tahun}:**\n\n"
                f"• Total Revenue: {summary['total_revenue_fmt']}\n"
                f"• Total Orders: {summary['total_orders']:,}\n"
                f"• Total Customers: {summary['total_customers']:,}\n"
                f"• AOV: {summary['aov_fmt']}\n"
                f"• **Top Product:** {summary['top_product']}\n"
                f"• **Top City:** {summary['top_city']}\n"
            )

        return None

    except Exception as e:
        return f"Maaf, terjadi error saat menyiapkan data: {str(e)}"


# ═════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═════════════════════════════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []

# Load data untuk analytics
df_master = None
data_status = "⚪ Tidak ada data"
debug_info = {}

if "etl_tables" in st.session_state and st.session_state["etl_tables"]:
    try:
        from core.data_manager import build_master
        tables = st.session_state["etl_tables"]
        debug_info["tables_count"] = len(tables)
        debug_info["tables_names"] = list(tables.keys())

        # Cek fact_order_item
        fact = tables.get("fact_order_item", pd.DataFrame())
        debug_info["fact_rows"] = len(fact)

        df_master = build_master(tables)
        if df_master is not None and not df_master.empty:
            data_status = f"✅ {len(df_master):,} baris data siap"
            debug_info["master_rows"] = len(df_master)
            debug_info["master_cols"] = list(df_master.columns)[:5]  # First 5 cols
        else:
            data_status = "⚠️ Data kosong setelah build_master"
            debug_info["build_result"] = "None or empty"
    except Exception as e:
        data_status = f"❌ Error: {str(e)[:30]}..."
        debug_info["error"] = str(e)

# Simpan debug info ke session untuk ditampilkan di bawah jika perlu
st.session_state["debug_info"] = debug_info

# ═════════════════════════════════════════════════════════════════════
# SIDEBAR - SETTINGS
# ═════════════════════════════════════════════════════════════════════

# Settings panel - Hide by default untuk clean UI
with st.sidebar:
    with st.expander("⚙️ Settings", expanded=False):
        # Opsi Pilihan LLM Provider
        provider_options = ["🦙 Ollama (Lokal)", "🧠 GLM (Cloud)"]
        default_idx = 1 if bool(ZHIPUAI_API_KEY) else 0
        selected_provider = st.radio("Pilih Provider AI:", provider_options, index=default_idx)

        USE_GLM = selected_provider == "🧠 GLM (Cloud)"
        MODEL = GLM_MODEL if USE_GLM else OLLAMA_MODEL

        st.markdown(f"**Model Aktif:** {MODEL}")

        # Data Status Indicator
        st.markdown(f"**Data:** {data_status}")

        # Debug info (expandable)
        if debug_info:
            with st.expander("🔍 Debug Info", expanded=False):
                for key, val in debug_info.items():
                    st.text(f"{key}: {val}")

        ollama_context = 4096
        if not USE_GLM:
            ollama_context = st.slider("🧠 Context Window", min_value=1024, max_value=8192, value=4096, step=1024)
        temperature = st.slider("🌡️ Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

        st.markdown("---")

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()



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

# Dapatkan context intent dari histori untuk menyambung pertanyaan seperti "kalau februarinya?"
context_intent = ""
if st.session_state.messages:
    for m in reversed(st.session_state.messages):
        if m["role"] == "user":
            context_intent = m["content"]
            break

# Jika ada user input, cek apakah pertanyaan analytics
if user_input and not ml_context:
    analytics_result = query_analytics(user_input, df_master, context_intent=context_intent)

    # Cek apakah analytics_result valid (bukan error message)
    is_valid_analytics = analytics_result and not analytics_result.startswith("Maaf") and not analytics_result.startswith("❌")

    if is_valid_analytics:
        # Jika berhasil query analytics, gunakan hasilnya saja (tanpa data overview total)
        prompt = f"[JAWABAN ANALITIS SPESIFIK]\n{analytics_result}\n\n[PERTANYAAN USER]\n{user_input}\n\nBerdasarkan data di atas, jelaskan dengan bahasa mudah dipahami. JANGAN halu atau tambah data di luar yang tersedia!"
    elif data_overview:
        # Jika bukan pertanyaan analytics atau query gagal, inject data overview
        prompt = f"{data_overview}\n\n[PERTANYAAN USER]\n{user_input}\n\nJika pertanyaan berupa sapaan atau percakapan ringan, balaslah dengan ramah. Jika berupa pertanyaan data, jawab HANYA berdasarkan data di atas (katakan 'Data tidak tersedia' jika kurang)."
    else:
        # Tidak ada data sama sekali
        prompt = f"{user_input}\n\n[SYSTEM NOTE: TIDAK ADA DATA YANG TERSEDIA. Jawab bahwa data belum tersedia dan minta user upload data ke Supabase atau hubungikan database.]"

if prompt:
    # Simpan hanya input bersih ke histori chat agar UI rapi dan token lebih hemat
    clean_user_input = user_input if user_input else "📊 Data Analytics Context"
    st.session_state.messages.append({"role": "user", "content": clean_user_input})
    with st.chat_message("user"):
        st.markdown(clean_user_input)

    # Siapkan pesan untuk API: Ambil semua histori (bersih), lalu inject prompt sistem ke pesan TERAKHIR saja
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages[:-1]
    api_messages.append({"role": "user", "content": prompt})

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner(f"{'🧠 GLM' if USE_GLM else '🦙 Ollama'} Menganalisis..."):
            try:
                if USE_GLM:
                    if not ZHIPUAI_API_KEY:
                        raise ValueError("API Key ZhipuAI belum diatur di file .env. Silakan tambahkan ZHIPUAI_API_KEY=xxx.")
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
                            "temperature": temperature,
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
                                "temperature": temperature,
                                "num_predict": 1536,
                                "num_ctx": ollama_context if not USE_GLM else 4096,
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


# ═════════════════════════════════════════════════════════════════════
# BACKGROUND PRELOAD — Auto-load Supabase di background (deferred)
# ═════════════════════════════════════════════════════════════════════

try:
    from core.data_manager import prefetch_supabase
    prefetch_supabase()
except Exception:
    pass

render_sidebar_footer()
