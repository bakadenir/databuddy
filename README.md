# DataBuddy — E-Commerce Analytics Assistant 🛍️🤖

> **Hybrid AI System:** Rule-Based + ML + LLM in a single Streamlit dashboard — customer segmentation, revenue forecasting, bundle recommendations, and an AI analyst chatbot.

**🌐 Live Demo:** [databuddy.my.id](https://databuddy.my.id) | **Model:** `qwen2.5:1.5b` (Ollama) | **Deploy:** Docker Compose + Caddy + VPS

---

## 🎯 What It Solves

- **Context:** Shopee sellers in Indonesia face marketplace fee deductions (up to 10-12%) and struggle to analyze hundreds of daily transactions manually.
- **Problem:** Sellers don't know which products are profitable, which customers are VIPs, or when to run promotions — all raw data sits in Excel with zero insights.
- **Impact:** Eroded margins, intuition-based decisions, VIP customers not properly maintained.
- **Solution:** **DataBuddy** — upload a Shopee Excel file → automated ETL (8-table star schema) → interactive dashboard + AI chatbot that reads your store data.

---

## 🧠 AI System Architecture (Hybrid)

| Approach | Use Case | Implementation |
|----------|----------|:---:|
| **Rule-Based AI** | Customer segmentation (VIP/Loyal) | Forward chaining rules (frequency ≥5x + revenue ≥Rp3M) |
| **Traditional ML** | Bundling & Forecasting | Apriori (Market Basket) + Holt-Winters ETS |
| **Local LLM** | Chat Assistant & Narratives | `qwen2.5:1.5b` via Ollama (CPU inference) |
| **Cloud LLM** | Fast fallback | GLM-4-Plus via ZhipuAI API |

### ⚡ Ollama vs GLM Performance

| Metric | Ollama (qwen2.5:1.5b) | GLM-4-Plus (API) |
|--------|:---:|:---:|
| **Cold start** | 7-25 sec | <1 sec |
| **Inference speed** | ~5 sec (CPU) | <1 sec (GPU cluster) |
| **Keep-alive mode** | <1 sec | — |
| **Privacy** | ✅ Data stays local | ⚠️ Sent to cloud |

---

## 🏗️ Architecture

```
User Browser → Caddy (HTTPS) → Streamlit (port 8501)
                                    ├── Ollama (qwen2.5:1.5b, port 11434)
                                    ├── Supabase (8 tables, star schema)
                                    └── ETL Pipeline (Pandas)
```

Full architecture diagram: [`architecture.html`](architecture.html)

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/bakadenir/databuddy.git
cd databuddy

# Configure environment
cp .env.example .env
# Edit .env with your Supabase + ZhipuAI credentials

# Run with Docker
docker compose up -d

# Access at http://localhost:8501
```

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Frontend** | Streamlit, Plotly, Matplotlib |
| **Backend** | Python 3.11, Pandas, NumPy |
| **AI/ML** | scikit-learn, mlxtend (Apriori), statsmodels (Holt-Winters) |
| **LLM** | Ollama (qwen2.5:1.5b), GLM-4-Plus (ZhipuAI API) |
| **Database** | Supabase (PostgreSQL) |
| **Infrastructure** | Docker, Docker Compose, Caddy (Auto-SSL) |
| **Deployment** | Tencent Cloud VPS (2 vCPU, 7.4 GB RAM, 79 GB SSD) |

---

## 📊 Features

- **📥 ETL Pipeline** — Upload Shopee Excel → auto-transform to 8-table star schema
- **👥 Customer Segmentation** — Rule-based VIP/Loyal/Regular classification
- **📈 Revenue Forecasting** — Holt-Winters ETS time-series prediction
- **🎁 Bundle Recommendations** — Apriori market basket analysis
- **🤖 AI Chatbot** — Ask questions about your store data in natural language
- **📊 Interactive Dashboard** — Charts, tables, KPIs at a glance

---

## 📂 Project Structure

```
databuddy/
├── app.py              # Streamlit main entry point
├── etl/                # ETL pipeline (Excel → Supabase)
├── ai/                 # AI modules (segmentation, forecasting, bundling)
├── llm/                # LLM integration (Ollama + GLM-4)
├── supabase/           # Database schema & migrations
├── docker-compose.yml  # Multi-service orchestration
├── Caddyfile           # Reverse proxy + auto-SSL config
└── architecture.html   # Interactive architecture diagram
```

---

## 📝 License

MIT — built for academic and demonstration purposes.
