# DataBuddy — Shopee Data Analytics & Science Assistant

> Aplikasi analitik data berbasis Streamlit khusus untuk data ekspor Shopee.

## 🚀 Quick Start

### 1. Buat Virtual Environment
```bash
# Dengan conda (rekomendasi):
conda create -n databuddy python=3.11 -y
conda activate databuddy

# Atau dengan venv:
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env dan isi nilai yang diperlukan
```

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```

App akan buka otomatis di browser: `http://localhost:8501`

---

## 📁 Struktur Project

```
databuddy/
├── app.py                  # Entry point Streamlit
├── requirements.txt
├── .env.example
├── core/                   # Config & database connections
├── etl/                    # ETL pipeline (CSV/Excel → DB)
├── pages/                  # Halaman-halaman Streamlit
├── components/             # Reusable UI components
├── ml/                     # Machine Learning models
├── llm/                    # LLM chatbox engine
├── data/                   # Data lokal (raw, processed, SQLite)
└── notebooks/              # Jupyter notebooks untuk eksplorasi
```

## 🗺️ Roadmap

| Phase | Status | Deskripsi |
|-------|--------|-----------|
| Phase 0 | ✅ | Environment Setup |
| Phase 1 | 🔄 | ETL Pipeline (CSV/Excel → SQLite → Supabase) |
| Phase 2 | 🔲 | Dashboard Interaktif |
| Phase 3 | 🔲 | ML Models (Clustering, Bundling) |
| Phase 4 | 🔲 | LLM Chatbox |
