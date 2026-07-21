# E-Library - Aplikasi Perpustakaan Digital

Aplikasi desktop manajemen perpustakaan berbasis **Python + Tkinter**,
dibangun dengan arsitektur **Model-View-Controller (MVC)** dan database
**SQLite**. Proyek Akhir mata kuliah Pemrograman Berbasis Objek (PBO).

## Fitur
- Manajemen katalog buku (CRUD)
- Manajemen anggota perpustakaan (CRUD)
- Transaksi peminjaman & pengembalian
- Penghitungan denda keterlambatan otomatis

## Struktur Proyek
```
E-Library-App/
├── database/
│   └── elibrary.db      # Basis data SQLite (dibuat otomatis saat aplikasi jalan)
├── model.py             # Layer Model  : koneksi & query SQLite
├── view.py              # Layer View   : komponen antarmuka Tkinter
├── main.py              # Layer Controller : Root App, navigasi & event handler
└── README.md
```

## Cara Menjalankan
1. Pastikan Python 3 sudah terpasang.
2. Buka terminal di folder proyek.
3. Jalankan:
   ```
   python main.py
   ```
   Database `elibrary.db` akan otomatis dibuat pada folder `database/`
   saat aplikasi pertama kali dijalankan.

## Anggota Kelompok
| Nama | NIM | Tugas |
|------|-----|-------|
| Mey  | ... | Controller (main.py) |
| Ayu  | ... | Model Buku + View Dashboard & Buku |
| Kia  | ... | Model Anggota & Peminjaman + View terkait |
| Ema  | ... | Mockup & Laporan |
