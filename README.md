# DataBuddy — E-Commerce Analytics & Expert System 🛍️🤖

> **Rule-Based + LLM Hybrid Assistant** untuk memproses data e-commerce, mengidentifikasi pelanggan VIP, meramal omzet, dan memberikan *insight* operasional melalui *Local AI*.

---

## 🎯 Problem Statement
- **Konteks:** Penjual online/e-commerce saat ini menghadapi potongan biaya admin platform (marketplace) yang semakin besar (hingga 10-12%).
- **Masalah:** Penjual kesulitan mengidentifikasi pelanggan "Sultan" (B2B/Kafe/Pembeli Skala Besar) dari ratusan baris data transaksi harian, sehingga kehilangan kesempatan untuk menarik mereka ke jalur penjualan langsung (Direct Order via WhatsApp).
- **Dampak:** Margin keuntungan toko tergerus habis oleh pajak marketplace, padahal omzet besar disumbang oleh segelintir pelanggan VIP.
- **Solusi:** **DataBuddy**, sebuah aplikasi asisten cerdas yang memadukan **Rule-Based Expert System** (untuk deteksi VIP akurat) dan **Local LLM** (untuk menyusun pesan *copywriting* penawaran WhatsApp ke pelanggan secara personal).

## 🧠 AI System Approach (Rule-Based + ML + LLM)
Aplikasi ini tidak hanya menggunakan LLM buta, melainkan perpaduan hibrida:
1. **Rule-Based AI (Clustering):** Digunakan untuk segmentasi *Super VIP*, *Loyal*, dan *Reguler*. Aturan pasti (seperti frekuensi order > 5x dan nominal > Rp 3 Juta) jauh lebih akurat menggunakan *Rule-Based* daripada menebak menggunakan LLM.
2. **Traditional ML (Forecasting & Bundling):** Menggunakan **Apriori** (Market Basket Analysis) untuk rekomendasi paket barang dan **Holt-Winters ETS** untuk peramalan omzet bulan depan.
3. **Local LLM (Chat Assistant):** Membaca hasil *Rule-Based* dan *ML* di atas untuk menghasilkan narasi manusiawi, rekomendasi operasional, dan merangkai draf pesan promosi WhatsApp. (Menggunakan *Ollama* secara lokal).

---

## 💻 Instalasi & Menjalankan di Windows (Local PC)

Proyek ini dibangun menggunakan Python dan Streamlit. Berikut adalah cara menjalankannya di laptop Windows Anda.

### 1. Prasyarat (Prerequisites)
- **Python** (versi 3.10 atau 3.11 disarankan).
- **Ollama** (Unduh dari [ollama.com](https://ollama.com/) dan install di Windows).

### 2. Buka Terminal / Command Prompt
Buka terminal (CMD atau PowerShell) dan masuk ke folder proyek ini.

### 3. Buat Virtual Environment (Wajib)
Jalankan perintah berikut untuk mengisolasi instalasi library:
```cmd
python -m venv .venv
```
Aktifkan *environment* tersebut:
```cmd
.venv\Scripts\activate
```
*(Ciri berhasil: Akan ada tulisan `(.venv)` di sebelah kiri terminal Anda).*

### 4. Install Dependencies (Library)
```cmd
pip install -r requirements.txt
```

### 5. Setup LLM (Ollama)
Pastikan Ollama sudah berjalan di latar belakang Windows Anda. Lalu unduh model AI lokal (Llama 3 atau Llama 3.2):
```cmd
ollama run llama3.2
```
*(Tunggu hingga proses download 100% selesai. Jika sudah bisa mengetik prompt di terminal, ketik `/bye` untuk keluar).*

### 6. Jalankan Aplikasi Streamlit
Terakhir, jalankan aplikasi web dengan perintah:
```cmd
streamlit run app.py
```
Aplikasi akan otomatis terbuka di *browser* Anda pada alamat: `http://localhost:8501`.

---

## 🏗️ Architecture Design
1. **Input:** User mengunggah file `CSV`/`Excel` berisi data transaksi e-commerce.
2. **Proses (Pandas & ML):** Data dibersihkan dan dimasukkan ke dalam algoritma *Apriori* (Bundling), *Holt-Winters* (Forecasting), dan *Forward Chaining Rules* (Segmentasi).
3. **LLM Context Engine:** Hasil angka dan data dari langkah 2 diubah menjadi *Prompt* berstruktur (Konteks).
4. **Local AI (Ollama):** Menerima *Prompt Context* beserta *Guardrail* ketat, lalu memproses instruksi user.
5. **Output:** Tampilan *Dashboard* interaktif (Plotly) dan jendela *Chatbox* Asisten AI di Streamlit.

---

## 🛡️ Responsible AI & Guardrails
Aplikasi ini dilengkapi **System Prompt Guardrail** yang ketat di `pages/3_Chatbox.py`:
- **Anti-Hallucination:** AI dilarang keras memalsukan atau mengarang angka omzet. Jika data tidak ada di dalam konteks layar saat itu, AI dipaksa untuk menolak menjawab dengan sopan dan mengarahkan pengguna untuk menjalankan proses *Machine Learning* di halaman *Strategi* terlebih dahulu.
- **Privacy:** Sistem hanya memproses data agregat statistik, tidak membaca detail nomor telepon pengguna untuk dikirimkan ke model secara mentah.

---
*Dibuat untuk keperluan Tugas Akhir / UAS AI - 2025* 🎓
