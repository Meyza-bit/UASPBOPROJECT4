"""
model.py - Lapisan Data (Model) aplikasi E-Library.

Isi file ini:
  - Konstanta konfigurasi aplikasi
  - class Database         : satu-satunya pintu koneksi ke SQLite (prinsip DRY)
  - class BukuModel        : CRUD data buku
  - class AnggotaModel     : CRUD data anggota
  - class PeminjamanModel  : transaksi pinjam/kembali + hitung denda otomatis

Aturan MVC:
  Semua perintah SQL (sqlite3) HANYA boleh ada di file ini.
  view.py dilarang keras menyentuh database secara langsung.
"""

import sqlite3
from datetime import date, timedelta

# ============================================================
#  KONSTANTA  (ubah di sini kalau aturannya berubah)
# ============================================================
DB_NAME = "database/elibrary.db"     # nama file database SQLite
MASA_PINJAM_HARI = 7        # lama pinjam default (hari)
DENDA_PER_HARI = 1000       # denda keterlambatan per hari (Rupiah)


class Database:
    """
    Mengelola koneksi ke SQLite dan pembuatan tabel.

    Semua Model lain (Buku, Anggota, Peminjaman) memakai SATU objek
    Database ini, jadi kode koneksi tidak ditulis berulang-ulang
    -> memenuhi prinsip DRY (Don't Repeat Yourself).
    """

    def __init__(self, db_name=DB_NAME):
        # Awalan dua garis bawah (__) membuat atribut ini PRIVAT.
        # Inilah contoh Encapsulation: nama database tidak bisa diubah
        # sembarangan dari luar class.
        self.__db_name = db_name
        self.__buat_tabel()

    def koneksi(self):
        """Membuka koneksi baru dan mengaktifkan dukungan Foreign Key."""
        conn = sqlite3.connect(self.__db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def __buat_tabel(self):
        """Membuat 3 tabel bila belum ada (otomatis saat aplikasi pertama jalan)."""
        with self.koneksi() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS buku (
                    id_buku    INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul      TEXT    NOT NULL,
                    pengarang  TEXT,
                    penerbit   TEXT,
                    tahun      INTEGER,
                    kategori   TEXT,
                    stok       INTEGER NOT NULL DEFAULT 1
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS anggota (
                    id_anggota INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama       TEXT    NOT NULL,
                    email      TEXT,
                    telepon    TEXT,
                    alamat     TEXT,
                    tgl_daftar TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS peminjaman (
                    id_pinjam       INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_buku         INTEGER NOT NULL,
                    id_anggota      INTEGER NOT NULL,
                    tgl_pinjam      TEXT    NOT NULL,
                    tgl_jatuh_tempo TEXT    NOT NULL,
                    tgl_kembali     TEXT,
                    status          TEXT    NOT NULL DEFAULT 'Dipinjam',
                    denda           INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (id_buku)    REFERENCES buku(id_buku),
                    FOREIGN KEY (id_anggota) REFERENCES anggota(id_anggota)
                )
            """)
            conn.commit()


class BukuModel:
    """CRUD (Create-Read-Update-Delete) untuk tabel buku."""

    def __init__(self, db):
        self.__db = db  # simpan objek Database (atribut privat -> Encapsulation)

    def __validasi(self, judul, tahun, stok):
        """Validasi integritas data SEBELUM disimpan ke database."""
        if not judul or not judul.strip():
            raise ValueError("Judul buku wajib diisi.")
        try:
            tahun = int(tahun)
            stok = int(stok)
        except (ValueError, TypeError):
            raise ValueError("Tahun dan stok harus berupa angka.")
        if stok < 0:
            raise ValueError("Stok tidak boleh bernilai negatif.")
        return tahun, stok

    # ---------- CREATE ----------
    def tambah(self, judul, pengarang, penerbit, tahun, kategori, stok):
        tahun, stok = self.__validasi(judul, tahun, stok)
        with self.__db.koneksi() as conn:
            conn.execute(
                """INSERT INTO buku (judul, pengarang, penerbit, tahun, kategori, stok)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (judul.strip(), pengarang, penerbit, tahun, kategori, stok),
            )
            conn.commit()

    # ---------- READ ----------
    def ambil_semua(self):
        with self.__db.koneksi() as conn:
            return conn.execute("SELECT * FROM buku ORDER BY id_buku").fetchall()

    def ambil_by_id(self, id_buku):
        with self.__db.koneksi() as conn:
            return conn.execute(
                "SELECT * FROM buku WHERE id_buku = ?", (id_buku,)
            ).fetchone()

    # ---------- UPDATE ----------
    def ubah(self, id_buku, judul, pengarang, penerbit, tahun, kategori, stok):
        tahun, stok = self.__validasi(judul, tahun, stok)
        with self.__db.koneksi() as conn:
            conn.execute(
                """UPDATE buku
                   SET judul=?, pengarang=?, penerbit=?, tahun=?, kategori=?, stok=?
                   WHERE id_buku=?""",
                (judul.strip(), pengarang, penerbit, tahun, kategori, stok, id_buku),
            )
            conn.commit()

    # ---------- DELETE ----------
    def hapus(self, id_buku):
        with self.__db.koneksi() as conn:
            conn.execute("DELETE FROM buku WHERE id_buku = ?", (id_buku,))
            conn.commit()

    def total(self):
        """Jumlah judul buku (dipakai di Dashboard)."""
        with self.__db.koneksi() as conn:
            return conn.execute("SELECT COUNT(*) FROM buku").fetchone()[0]


class AnggotaModel:
    """CRUD untuk tabel anggota."""

    def __init__(self, db):
        self.__db = db

    def __validasi(self, nama):
        if not nama or not nama.strip():
            raise ValueError("Nama anggota wajib diisi.")

    # ---------- CREATE ----------
    def tambah(self, nama, email, telepon, alamat):
        self.__validasi(nama)
        with self.__db.koneksi() as conn:
            conn.execute(
                """INSERT INTO anggota (nama, email, telepon, alamat, tgl_daftar)
                   VALUES (?, ?, ?, ?, ?)""",
                (nama.strip(), email, telepon, alamat, date.today().isoformat()),
            )
            conn.commit()

    # ---------- READ ----------
    def ambil_semua(self):
        with self.__db.koneksi() as conn:
            return conn.execute(
                "SELECT * FROM anggota ORDER BY id_anggota"
            ).fetchall()

    def ambil_by_id(self, id_anggota):
        with self.__db.koneksi() as conn:
            return conn.execute(
                "SELECT * FROM anggota WHERE id_anggota = ?", (id_anggota,)
            ).fetchone()

    # ---------- UPDATE ----------
    def ubah(self, id_anggota, nama, email, telepon, alamat):
        self.__validasi(nama)
        with self.__db.koneksi() as conn:
            conn.execute(
                """UPDATE anggota SET nama=?, email=?, telepon=?, alamat=?
                   WHERE id_anggota=?""",
                (nama.strip(), email, telepon, alamat, id_anggota),
            )
            conn.commit()

    # ---------- DELETE ----------
    def hapus(self, id_anggota):
        with self.__db.koneksi() as conn:
            conn.execute("DELETE FROM anggota WHERE id_anggota = ?", (id_anggota,))
            conn.commit()

    def total(self):
        with self.__db.koneksi() as conn:
            return conn.execute("SELECT COUNT(*) FROM anggota").fetchone()[0]


class PeminjamanModel:
    """Transaksi peminjaman & pengembalian buku + hitung denda otomatis."""

    def __init__(self, db):
        self.__db = db

    # ---------- CREATE: pinjam buku ----------
    def pinjam(self, id_buku, id_anggota):
        with self.__db.koneksi() as conn:
            # cek dulu stok bukunya masih ada atau tidak
            row = conn.execute(
                "SELECT stok FROM buku WHERE id_buku = ?", (id_buku,)
            ).fetchone()
            if row is None:
                raise ValueError("Buku tidak ditemukan.")
            if row[0] <= 0:
                raise ValueError("Stok buku habis, tidak bisa dipinjam.")

            tgl_pinjam = date.today()
            tgl_tempo = tgl_pinjam + timedelta(days=MASA_PINJAM_HARI)

            conn.execute(
                """INSERT INTO peminjaman
                   (id_buku, id_anggota, tgl_pinjam, tgl_jatuh_tempo, status, denda)
                   VALUES (?, ?, ?, ?, 'Dipinjam', 0)""",
                (id_buku, id_anggota, tgl_pinjam.isoformat(), tgl_tempo.isoformat()),
            )
            # stok berkurang 1 karena satu eksemplar sedang dipinjam
            conn.execute(
                "UPDATE buku SET stok = stok - 1 WHERE id_buku = ?", (id_buku,)
            )
            conn.commit()

    # ---------- UPDATE: kembalikan buku ----------
    def kembalikan(self, id_pinjam):
        with self.__db.koneksi() as conn:
            row = conn.execute(
                """SELECT id_buku, tgl_jatuh_tempo, status
                   FROM peminjaman WHERE id_pinjam = ?""",
                (id_pinjam,),
            ).fetchone()
            if row is None:
                raise ValueError("Data peminjaman tidak ditemukan.")

            id_buku, tgl_tempo_str, status = row
            if status == "Kembali":
                raise ValueError("Buku ini sudah dikembalikan sebelumnya.")

            tgl_kembali = date.today()
            denda = self.hitung_denda(tgl_tempo_str, tgl_kembali)

            conn.execute(
                """UPDATE peminjaman
                   SET tgl_kembali=?, status='Kembali', denda=?
                   WHERE id_pinjam=?""",
                (tgl_kembali.isoformat(), denda, id_pinjam),
            )
            # stok bertambah 1 lagi karena buku sudah kembali
            conn.execute(
                "UPDATE buku SET stok = stok + 1 WHERE id_buku = ?", (id_buku,)
            )
            conn.commit()
            return denda  # dikembalikan agar Controller bisa tampilkan di messagebox

    @staticmethod
    def hitung_denda(tgl_jatuh_tempo, tgl_kembali):
        """
        Denda = jumlah hari telat x DENDA_PER_HARI.
        Kalau tidak telat (kembali tepat waktu / lebih awal), denda = 0.
        """
        jatuh_tempo = date.fromisoformat(tgl_jatuh_tempo)
        selisih_hari = (tgl_kembali - jatuh_tempo).days
        return selisih_hari * DENDA_PER_HARI if selisih_hari > 0 else 0

    # ---------- READ (pakai JOIN agar tampil nama buku & nama anggota) ----------
    def ambil_semua(self):
        with self.__db.koneksi() as conn:
            return conn.execute("""
                SELECT  p.id_pinjam, b.judul, a.nama,
                        p.tgl_pinjam, p.tgl_jatuh_tempo,
                        p.tgl_kembali, p.status, p.denda
                FROM peminjaman p
                JOIN buku    b ON p.id_buku    = b.id_buku
                JOIN anggota a ON p.id_anggota = a.id_anggota
                ORDER BY p.id_pinjam DESC
            """).fetchall()

    def total_dipinjam(self):
        """Jumlah buku yang statusnya masih 'Dipinjam' (dipakai di Dashboard)."""
        with self.__db.koneksi() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM peminjaman WHERE status = 'Dipinjam'"
            ).fetchone()[0]


# ============================================================
#  UJI CEPAT LAPISAN MODEL (tanpa GUI)
#  Jalankan file ini langsung:  python model.py
# ============================================================
if __name__ == "__main__":
    db = Database("uji_elibrary.db")
    buku = BukuModel(db)
    anggota = AnggotaModel(db)
    peminjaman = PeminjamanModel(db)

    buku.tambah("Laskar Pelangi", "Andrea Hirata", "Bentang", 2005, "Novel", 3)
    anggota.tambah("Budi Santoso", "budi@mail.com", "081200000000", "Pontianak")

    print("Total buku    :", buku.total())
    print("Total anggota :", anggota.total())

    peminjaman.pinjam(1, 1)
    print("Sedang dipinjam:", peminjaman.total_dipinjam())

    denda = peminjaman.kembalikan(1)
    print("Denda saat kembali:", denda)
    print("Uji Model selesai tanpa error.")
