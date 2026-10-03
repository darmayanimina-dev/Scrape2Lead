# ⚡ FLEXI-GEN

> **Fast Leads Extraction & Exploration Engine for Automated Retention Generation**  
> *(Alternatif Resmi: Fast-Leads Extraction & Intelligence Generator / Fast-Leads Exploration & Interactive Retention Generator)*

**Tagline:**  
*“Web-Based Google Maps Lead Scraper & Real-Time Sync for Retention Canvassing Productivity”*

**Slogan:**  
*“Generating Quality Leads, Accelerating Retention Canvassing.”*

**Live Deployment URL:**  
👉 **[https://scrape2lead.streamlit.app/](https://scrape2lead.streamlit.app/)**

---

## 🌟 Identitas & Fitur Utama

**FLEXI-GEN** adalah platform otomasi pencarian calon pelanggan (*lead generation / canvassing*) presisi berbasis web Google Maps dengan sinkronisasi langsung (*real-time sync*) ke master spreadsheet **Google Sheets**.

1. **⚡ FLEXI-GEN Controller**:
   - Tampilan antarmuka modern, minimalis, dan responsif (ramah tampilan smartphone / mobile touch).
   - **Kata Kunci Usaha**: input fleksibel dengan tombol pilihan cepat (*Quick Preset Chips*: warung makan, toko bangunan, bengkel motor, showroom mobil, toko listrik, distributor sembako, dll.).
   - **Target Kontak Baru**: pembatasan otomatis jumlah kontak unik yang dicari.
   - **Pengaturan Wilayah Target Fleksibel**:
     - *Semua Kalsel*: Menyisir 35+ kecamatan & kota secara acak presisi.
     - *Pilih Kota / Kab*: Memilih kabupaten/kota (Banjarmasin, Banjarbaru, Martapura, Pelaihari, dll.).
     - *Pilih Kecamatan*: Menargetkan kecamatan spesifik dengan fitur autocomplete.
     - *Kustom / Kota Lain*: Mengetikkan nama kota/daerah manapun di Indonesia (Balikpapan, Samarinda, Jakarta Selatan, Surabaya, dll.).

2. **Dukungan Dua Mode Otomasi**:
   - **Mode Manual (Langsung)**: Klik tombol hijau **Mulai Cari Data** untuk memulai pencarian instan dari antarmuka web.
   - **Mode Background Listener**: Menjalankan polling otomatis di latar belakang yang memantau perintah `JALANKAN` dari panel Google Sheets Apps Script.

3. **Live Dashboard & Monitoring Real-time**:
   - **KPI Metrik Cepat**: Target Kontak, Kontak Baru Tersimpan (Sesi), Total Database di Google Sheets, dan Status Mesin.
   - **Feed Kontak Interaktif**: Menampilkan nama bisnis, nomor telepon terstandarisasi (`+62`), alamat lengkap, tombol langsung **WhatsApp** (`wa.me`), dan tombol tautan **Google Maps**.
   - **Tabel Data & Ekspor CSV**: Pratinjau tabel interaktif dan unduhan berkas CSV kapan saja.
   - **Terminal Aktivitas Real-time**: Log berwarna (`[INFO]`, `[SEARCH]`, `[SUCCESS]`, `[SKIP]`, `[WARN]`) untuk memantau proses scraping secara langsung.

4. **Integrasi Google Sheets & Pencegahan Duplikasi**:
   - Pencegahan duplikasi otomatis (membandingkan dengan database nomor yang sudah tersimpan).
   - Pengiriman progres langsung (`update_progress`) ke Google Sheets WebApp.
   - Penyimpanan data lead lengkap (`insert_lead`).
   - Penyimpanan lokal otomatis (`leads_history.json`) sehingga data tidak akan pernah hilang meskipun halaman di-refresh.

---

## 🚀 Cara Menjalankan Aplikasi Secara Lokal

Jalankan perintah berikut pada terminal:

```bash
streamlit run app.py --server.port 8505
```

Aplikasi dapat diakses di browser pada:
👉 **`http://localhost:8505`**

---

## 📁 Struktur Berkas

```
Scrape2Lead/
├── app.py                 # Antarmuka web Streamlit FLEXI-GEN (Responsive & Pure Light Mode)
├── config.py              # Konfigurasi wilayah Kalsel, preset kategori, dan URL WebApp
├── scraper_engine.py      # Mesin scraping Playwright dan pengontrol state thread-safe
├── sheets_service.py      # Layanan API integrasi Google Sheets Apps Script
├── packages.txt           # Dependensi sistem Linux untuk Streamlit Community Cloud
├── requirements.txt       # Daftar dependensi Python
└── README.md              # Dokumentasi lengkap proyek
```
