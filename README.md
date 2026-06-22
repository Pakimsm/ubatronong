# SoundOn Bot CLI

SoundOn Bot CLI adalah aplikasi otomatisasi berbasis Python dan Playwright yang dirancang untuk mengelola rilis lagu di platform SoundOn Global secara massal. Bot ini membantu proses pembuatan draf lagu tunggal (Single Song), album, penarikan analitik, hingga manajemen multi-akun.

## Fitur Utama

- **Otomatisasi Penuh Alur Rilis Lagu**: Mengisi data lagu (Step 1-4) seperti Judul, Artis Utama, Kontributor (Vokalis), Produser, Penulis Lagu/Lirik, Genre, Lirik, Status Eksplisit, serta Lisensi secara dinamis.
- **Manajemen Multi-Akun**: Menyimpan akun, memantau status login (`Berhasil Login`, `Gagal Login`), serta melakukan aksi massal pada akun-akun aktif.
- **Unggah File Massal**: Mengunggah file audio `.wav`/`.mp3` beserta *cover art* yang dibuat otomatis dari teks metadata menggunakan library PIL.
- **Bypass Popup & Modal**: Menangani dan menutup popup pengumuman, modal survei, serta menekan modal validasi (*"kesalahan terdeteksi"*) untuk melanjutkan penyimpanan draf.
- **Penarikan Data & Analitik**: Fitur untuk mengekstrak data rilis, penghasilan, dan statistik performa lagu.

## Struktur Project

```
├── config/
│   └── accounts.json         # Penyimpanan database akun lokal
├── src/
│   ├── cli/                  # Logika antarmuka CLI dan prompt menu
│   ├── core/                 # Browser wrapper (Playwright), runner, dan utilitas
│   ├── models/               # Dataclass payload dan status model
│   ├── pages/                # Page Object Model untuk halaman SoundOn
│   └── tasks/                # Implementasi task otomatisasi (Login, Upload, dll)
├── main.py                   # Entry point aplikasi CLI
├── requirements.txt          # File dependensi Python
└── README.md                 # Dokumentasi ini
```

## Prasyarat Instalasi

1. **Python**: Pastikan Anda telah menginstal Python versi `3.10` ke atas.
2. **Google Chrome / Chromium**: Dibutuhkan untuk menjalankan automasi browser.

## Cara Instalasi

1. Kloning repositori ini (atau unduh source code-nya):
   ```bash
   git clone https://github.com/Pakimsm/ubatronong.git
   cd ubatronong
   ```

2. Buat dan aktifkan virtual environment (opsional namun direkomendasikan):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instal dependensi Python:
   ```bash
   pip install -r requirements.txt
   ```

4. Instal browser driver Playwright:
   ```bash
   playwright install chromium
   ```

## Konfigurasi Akun

Buat atau edit file `config/accounts.json` di dalam direktori project. Struktur datanya adalah sebagai berikut:

```json
[
  {
    "id": 1,
    "email": "contoh.email@gmail.com",
    "password": "password_akun_anda",
    "active": true,
    "status": "Baru Ditambahkan"
  }
]
```

## Cara Menjalankan

Jalankan perintah berikut di terminal Anda untuk membuka antarmuka menu interaktif:

```bash
python main.py
```

Anda akan disambut dengan menu CLI interaktif:
1. **Tampilkan List Akun**: Melihat semua akun terdaftar beserta status login aktifnya.
2. **Tambah Akun**: Memasukkan akun baru langsung dari terminal.
3. **Hapus Akun**: Menghapus akun yang sudah terdaftar.
4. **Test Login**: Menguji kredensial login multi-akun secara headless.
5. **Upload Lagu**: Melakukan upload single song dengan metadata lengkap.
6. **Upload Album**: Mengunggah album dari direktori folder lokal.
7. **Tarik Data / Tarik Analitik**: Mengunduh laporan performa lagu dari pustaka akun.
