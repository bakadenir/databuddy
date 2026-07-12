# DataBuddy — E-Commerce Analytics Assistant 🛍️🤖

> **Rule-Based + ML + LLM Hybrid Assistant** untuk analitik data Shopee: segmentasi pelanggan, forecasting omzet, rekomendasi bundling, dan chatbot AI analis dalam satu dashboard.

**🌐 Live Demo:** [databuddy.my.id](https://databuddy.my.id) | **Model:** `qwen2.5:1.5b` (Ollama) | **Deploy:** Docker Compose + Caddy + VPS

---

## 🎯 Problem Statement

- **Konteks:** Seller Shopee di Indonesia menghadapi potongan biaya marketplace (hingga 10-12%) dan kesulitan menganalisis ratusan transaksi harian secara manual.
- **Masalah:** Penjual tidak tahu produk mana yang profit, pelanggan mana yang VIP, dan kapan waktu terbaik untuk promosi — semua data mentah di Excel tanpa insight.
- **Dampak:** Margin tergerus, keputusan bisnis berdasarkan intuisi, pelanggan VIP tidak di-maintain dengan baik.
- **Solusi:** **DataBuddy** — upload file Excel Shopee → ETL otomatis (8 tabel star schema) → Dashboard interaktif + Chatbot AI analis yang membaca data toko.

---

## 🧠 AI System Approach (Hybrid: Rule-Based + ML + LLM)

| Approach | Use Case | Implementasi |
|----------|----------|:---:|
| **Rule-Based AI** | Segmentasi pelanggan VIP/Loyal | Forward chaining rules (frekuensi ≥5x + revenue ≥Rp3M) |
| **Traditional ML** | Bundling & Forecasting | Apriori (Market Basket) + Holt-Winters ETS |
| **Local LLM** | Chat Assistant & Narasi | `qwen2.5:1.5b` via Ollama (CPU inference) |
| **Cloud LLM** | Fallback cepat | GLM-4-Plus via ZhipuAI API |

### ⚡ Ollama vs GLM Performance (Real Measurement)
| Metric | Ollama (qwen2.5:1.5b) | GLM-4-Plus (API) |
|--------|:---:|:---:|
| **Cold start** | 7-25 detik | <1 detik |
| **Inference speed** | ~5 detik (CPU) | <1 detik (GPU cluster) |
| **With keep_alive** | <1 detik | — |
| **Privacy** | ✅ Data stays local | ⚠️ Data sent to cloud |

---

## 🏗️ Architecture

```
User Browser → Caddy (HTTPS) → Streamlit (port 8501)
                                    ├── Ollama (qwen2.5:1.5b, port 11434)
                                    ├── Supabase (8 tables, star schema)
                                    └── ETL Pipeline (Pandas)
```

Diagram arsitektur lengkap: [`architecture.html`](architecture.html)

---

## 🚀 Deployment (Docker Compose + VPS)

### Prasyarat
- Docker + Docker Compose
- Domain dengan DNS pointing ke VPS (Caddy auto-HTTPS)

### Quick Start
```bash
git clone https://github.com/bakadenir/databuddy.git
cd databuddy
cp .env.example .env  # edit SUPABASE_URL, SUPABASE_KEY, ZHIPUAI_API_KEY
docker compose up -d
```

Aplikasi tersedia di `https://<domain-anda>`.

### Container
| Service | Deskripsi | Port |
|---------|-----------|:---:|
| `web` | Streamlit app | 8501 (internal) |
| `ollama` | qwen2.5:1.5b local LLM | 11434 (internal) |
| `caddy` | Auto-HTTPS reverse proxy | 80, 443 |

### Environment Variables (`.env`)
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGci...
ZHIPUAI_API_KEY=xxx  # opsional, untuk GLM fallback
OLLAMA_KEEP_ALIVE=-1  # model stay di RAM, hilangkan cold start
```

---

## ⚡ Optimizations

1. **`OLLAMA_KEEP_ALIVE=-1`** — model `qwen2.5:1.5b` stay di RAM sepanjang container hidup, cold start dari 25s → <1s
2. **`build_master()` caching** — join 8 tabel hanya sekali via `st.session_state`, ganti tab tanpa query ulang
3. **2-step chat render** — pesan user langsung muncul di UI tanpa nunggu LLM selesai
4. **Default to Ollama** — sidebar default ke LLM lokal, GLM sebagai fallback

---

## 💻 Local Development (Windows)

```cmd
# 1. Virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan Ollama & download model
ollama run qwen2.5:1.5b

# 4. Run Streamlit
streamlit run app.py
```

---

## 🛡️ Responsible AI & Guardrails

Sistem prompt guardrail di `pages/3_Chatbox.py`:
- **Anti-Hallucination:** AI dilarang mengarang angka. Jika data tidak di konteks, tolak dengan sopan.
- **Privacy:** Data pelanggan diproses lokal via Ollama, tidak dikirim ke cloud.
- **Academic Integrity:** AI mengenali prompt cheating dan menolak.
- **Bahasa Indonesia:** Wajib menjawab dalam Bahasa Indonesia.
- **Overreliance:** AI mengarahkan user ke halaman Strategi untuk analisis ML yang akurat.

---

## 📊 Fitur

| Halaman | Fitur |
|---------|-------|
| **🏠 Home** | Landing page, SEO metadata |
| **📥 Upload & ETL** | Upload CSV/Excel Shopee → 8 tabel star schema |
| **📊 Dashboard** | Revenue trend, top produk, heatmap, geo analysis, AOV |
| **🎯 Strategi** | Bundling (Apriori), Clustering VIP, Forecasting (Holt-Winters) |
| **💬 Chatbox** | AI Data Analyst — tanya apapun tentang performa toko |

---

## 📂 Project Structure

```
databuddy/
├── app.py                 # Landing page
├── pages/
│   ├── 0_Home.py          # Upload & ETL
│   ├── 1_Dashboard.py     # Dashboard analytics
│   ├── 2_Strategi.py      # ML: Bundling, Clustering, Forecasting
│   └── 3_Chatbox.py       # AI Chatbot (Ollama + GLM)
├── core/
│   ├── analytics_engine.py
│   ├── data_manager.py    # build_master() + caching
│   ├── database.py
│   ├── ml_context.py
│   ├── ml_engine.py
│   └── models.py
├── components/ui.py
├── etl/                   # ETL pipeline
├── docker-compose.yml
├── Dockerfile
├── Caddyfile
└── requirements.txt
```

---

*Dibuat untuk UAS AI04 — Artificial Intelligence, Universitas Cakrawala, 2025/2026 Genap* 🎓
