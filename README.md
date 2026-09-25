# 🎯 Canvassing Controller & Automated Lead Scraper

Aplikasi Web modern, minimalis, dan clean berbasis **Streamlit** untuk pencarian calon pelanggan (*lead generation / canvassing*) presisi berbasis wilayah **Kalimantan Selatan** menggunakan Google Maps dan sinkronisasi real-time ke **Google Sheets**.

---

## 🌟 Fitur Utama

1. **Canvassing Controller**:
   - Tampilan antarmuka ringkas, modern, dan minimalis sesuai acuan desain.
   - **Kata Kunci Usaha**: input fleksibel dengan tombol pilihan cepat (*Quick Preset Chips*: warung makan, toko bangunan, bengkel motor, showroom mobil, dll.).
   - **Target Kontak Baru**: pembatasan otomatis jumlah kontak unik yang dicari.
   - **Saring Wilayah Presisi**: mencakup seluruh kecamatan & kota di Kalimantan Selatan (Banjarmasin, Banjarbaru, Martapura, Pelaihari, Batulicin, Tanjung, dll.) dengan pengacakan otomatis agar hasil merata.

2. **Dukungan Dua Mode Otomasi**:
   - **Mode Manual (Langsung)**: Klik tombol hijau **Mulai Cari Data** untuk memulai pencarian instan dari antarmuka web.
   - **Mode Background Listener**: Menjalankan polling otomatis di latar belakang yang memantau perintah `JALANKAN` dari panel Google Sheets Apps Script.

3. **Live Dashboard & Monitoring Real-time**:
   - **KPI Metrik Cepat**: Target Kontak, Kontak Baru Tersimpan (Sesi), Total Database di Google Sheets, dan Status Mesin.
   - **Feed Kontak Interaktif**: Menampilkan nama bisnis, nomor telepon format internasional (+62), alamat lengkap, tombol langsung **WhatsApp** (`wa.me`), dan tombol tautan **Google Maps**.
   - **Tabel Data & Ekspor CSV**: Pratinjau tabel interaktif dan unduhan berkas CSV kapan saja.
   - **Terminal Aktivitas Real-time**: Log berwarna (`[INFO]`, `[SEARCH]`, `[SUCCESS]`, `[SKIP]`, `[WARN]`) untuk memantau proses scraping tanpa perlu membuka konsol server.

4. **Integrasi Google Sheets Teruji**:
   - Pencegahan duplikasi otomatis (membandingkan dengan database nomor yang sudah tersimpan).
   - Pengiriman progres langsung (`update_progress`) ke Google Sheets WebApp.
   - Penyimpanan data lead lengkap (`insert_lead`).

---

## 🚀 Cara Menjalankan Aplikasi

Jalankan perintah berikut pada terminal:

```bash
streamlit run app.py --server.port 8505
```

Aplikasi dapat langsung diakses di browser pada:
👉 **`http://localhost:8505`**

---

## 📁 Struktur Berkas

```
Scrape2Lead/
├── app.py                 # Antarmuka web Streamlit (Modern & Minimalist)
├── config.py              # Konfigurasi wilayah Kalsel, preset kategori, dan URL WebApp
├── scraper_engine.py      # Mesin scraping Playwright dan pengontrol state thread-safe
├── sheets_service.py      # Layanan API integrasi Google Sheets Apps Script
└── requirements.txt       # Daftar dependensi Python
```
