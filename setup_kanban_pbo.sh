#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  Generator Kanban UAS PBO — E-Library (Python Tkinter, MVC)
#  Bikin semua label + 27 issue GitHub sekaligus pakai gh CLI
# ============================================================

# --- KONFIGURASI (isi kalau perlu) --------------------------
# Kosongkan REPO kalau kamu jalanin script ini DI DALAM folder repo-nya.
# Kalau nggak, isi: "username/nama-repo"  (contoh: "mkato/uas-pbo-elibrary")
REPO=""

# GitHub username tiap anggota (buat auto-assign issue).
# Kosongkan aja kalau belum tahu / mau assign manual nanti.
USER_MEY=""
USER_KIA=""
USER_AYU=""
USER_EMA=""
# ------------------------------------------------------------

# 1) Cek gh kepasang & sudah login
command -v gh >/dev/null || { echo "gh CLI belum kepasang. Install dulu: https://cli.github.com"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Belum login. Jalanin dulu: gh auth login"; exit 1; }

REPO_FLAG=()
[ -n "$REPO" ] && REPO_FLAG=(-R "$REPO")

# 2) Bikin label
echo "==> Bikin label..."
mklabel() { gh label create "$1" --color "$2" --description "$3" "${REPO_FLAG[@]}" --force; }
mklabel perancangan 0E8A16 "Analisis & perancangan sistem"
mklabel code-mey    1D76DB "Coding - Mey"
mklabel code-kia    0052CC "Coding - Kia"
mklabel figma       8250DF "Figma / mockup - Ayu"
mklabel laporan     D4A017 "Penulisan laporan - Ema"

# 3) Bikin issue
echo "==> Bikin issue..."
# mkissue "judul" "deskripsi" "label" "assignee"
mkissue() {
  local title="$1" body="$2" label="$3" assignee="$4"
  local args=(issue create "${REPO_FLAG[@]}" --title "$title" --body "$body" --label "$label")
  [ -n "$assignee" ] && args+=(--assignee "$assignee")
  gh "${args[@]}"
}

# --- PERANCANGAN (bareng semua) ---
mkissue "Perancangan: finalisasi diagram alur MVC" \
  "Gambar diagram alur interaksi View -> Controller -> Model -> SQLite untuk Bab II poin 2.1." \
  perancangan ""
mkissue "Perancangan: ERD / skema database" \
  "Rancang tabel buku, anggota, dan peminjaman beserta relasinya (Bab II poin 2.2)." \
  perancangan ""
mkissue "Perancangan: Class Diagram + letak pilar OOP" \
  "Buat class diagram dan tandai letak Encapsulation, Inheritance, dan Polymorphism (Bab II poin 2.3)." \
  perancangan ""

# --- CODING: MEY ---
mkissue "Setup repo & struktur folder" \
  "Inisialisasi repo, buat file kosong main.py, view.py, model.py, README.md, dan .gitignore untuk *.db dan __pycache__." \
  code-mey "$USER_MEY"
mkissue "model.py: class Database + skema 3 tabel" \
  "Buat class Database sebagai satu-satunya tempat koneksi SQLite (DRY), sembunyikan koneksi pakai atribut privat, dan buat 3 tabel otomatis saat pertama dijalankan." \
  code-mey "$USER_MEY"
mkissue "model.py: CRUD data Buku" \
  "Buat class BukuModel dengan method create, read_all, update, delete untuk tabel buku." \
  code-mey "$USER_MEY"
mkissue "view.py: BaseFrame + halaman Dashboard" \
  "Buat class induk BaseFrame sebagai template halaman (Inheritance), dan DashboardView berisi ringkasan total buku, anggota, dan buku dipinjam." \
  code-mey "$USER_MEY"
mkissue "view.py: halaman Kelola Buku" \
  "Buat BukuView berisi form input, Treeview daftar buku, dan tombol Simpan/Ubah/Hapus/Bersih." \
  code-mey "$USER_MEY"
mkissue "main.py: App, routing & Menu Bar" \
  "Buat class App(tk.Tk), tumpuk semua halaman di grid yang sama, ganti halaman pakai .tkraise(), dan buat Menu Bar (File, Navigasi, Bantuan)." \
  code-mey "$USER_MEY"
mkissue "README.md GitHub" \
  "Tulis README menarik: deskripsi aplikasi, cara install dan menjalankan, serta screenshot antarmuka." \
  code-mey "$USER_MEY"

# --- CODING: KIA ---
mkissue "model.py: CRUD data Anggota" \
  "Buat class AnggotaModel dengan method create, read_all, update, delete untuk tabel anggota." \
  code-kia "$USER_KIA"
mkissue "model.py: Peminjaman + hitung denda otomatis" \
  "Buat class PeminjamanModel untuk catat pinjam/kembali, kurangi stok saat dipinjam, dan hitung denda otomatis Rp1.000 x jumlah hari telat saat pengembalian." \
  code-kia "$USER_KIA"
mkissue "view.py: halaman Kelola Anggota" \
  "Buat AnggotaView berisi form input, Treeview daftar anggota, dan tombol aksi." \
  code-kia "$USER_KIA"
mkissue "view.py: halaman Peminjaman" \
  "Buat PeminjamanView dengan dropdown pilih anggota dan buku, tanggal otomatis, tombol Pinjam dan Kembalikan, serta Treeview status dan denda." \
  code-kia "$USER_KIA"
mkissue "Exception handling & messagebox di semua aksi" \
  "Bungkus semua proses database dan konversi tipe data dengan try-except-finally, dan tampilkan messagebox untuk Sukses/Gagal/Peringatan/Konfirmasi." \
  code-kia "$USER_KIA"
mkissue "Testing CRUD end-to-end" \
  "Uji seluruh alur Create-Read-Update-Delete di tiap halaman, pastikan aplikasi tidak crash saat input salah (misal huruf di kolom angka)." \
  code-kia "$USER_KIA"

# --- FIGMA: AYU ---
mkissue "Wireframe low-fi 4 halaman" \
  "Sketsa kasar tata letak Dashboard, Buku, Anggota, dan Peminjaman sebagai acuan awal." \
  figma "$USER_AYU"
mkissue "Mockup halaman Dashboard" \
  "Desain final Dashboard dengan kartu ringkasan data." \
  figma "$USER_AYU"
mkissue "Mockup halaman Buku & Anggota" \
  "Desain final layout form input dan tabel data untuk halaman Buku dan Anggota." \
  figma "$USER_AYU"
mkissue "Mockup halaman Peminjaman" \
  "Desain final halaman Peminjaman: dropdown, tombol pinjam/kembali, dan tabel status." \
  figma "$USER_AYU"
mkissue "Style guide (warna, font, Menu Bar)" \
  "Tentukan palet warna, jenis font, dan bentuk Menu Bar biar konsisten di semua halaman." \
  figma "$USER_AYU"
mkissue "Export mockup untuk laporan" \
  "Export semua mockup jadi PNG dan kirim ke Ema untuk dimasukkan ke Bab II poin 2.4." \
  figma "$USER_AYU"

# --- LAPORAN: EMA ---
mkissue "Setup dokumen + halaman sampul" \
  "Atur format A4, Times New Roman 12pt, spasi 1.5, margin 4-3-3-3. Buat sampul, kata pengantar, daftar isi, daftar gambar, dan daftar tabel." \
  laporan "$USER_EMA"
mkissue "BAB I: Pendahuluan" \
  "Tulis latar belakang, analisis kebutuhan sistem, dan batasan masalah." \
  laporan "$USER_EMA"
mkissue "BAB II: Perancangan Sistem" \
  "Masukkan diagram alur MVC, skema database, class diagram, dan mockup dari Ayu." \
  laporan "$USER_EMA"
mkissue "BAB III: Implementasi & Pengujian" \
  "Tulis struktur direktori, potongan kode inti dari Mey dan Kia, pembahasan pilar OOP, dan screenshot hasil pengujian CRUD." \
  laporan "$USER_EMA"
mkissue "BAB IV: Penutup + daftar pustaka & lampiran" \
  "Tulis kesimpulan dan saran, daftar pustaka format APA, serta lampiran link repo GitHub dan tabel kontribusi anggota." \
  laporan "$USER_EMA"

echo ""
echo "==> SELESAI. 5 label + 27 issue berhasil dibuat."
echo "Cek di: https://github.com  (tab Issues repo kamu)"
