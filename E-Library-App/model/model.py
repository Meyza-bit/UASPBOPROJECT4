import sqlite3
from datetime import datetime, timedelta


class DatabaseModel:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self._init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        """Membuat tabel jika belum ada di database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabel Buku
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS buku (
                    id_buku INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul TEXT NOT NULL,
                    pengarang TEXT NOT NULL,
                    penerbit TEXT NOT NULL,
                    tahun INTEGER NOT NULL,
                    kategori TEXT NOT NULL,
                    stok INTEGER NOT NULL
                )
            """)

            # Tabel Anggota
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anggota (
                    id_anggota INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telepon TEXT NOT NULL,
                    alamat TEXT NOT NULL,
                    tgl_daftar TEXT NOT NULL
                )
            """)

            # Tabel Peminjaman
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS peminjaman (
                    id_pinjam INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_buku INTEGER NOT NULL,
                    id_anggota INTEGER NOT NULL,
                    tgl_pinjam TEXT NOT NULL,
                    tgl_jatuh_tempo TEXT NOT NULL,
                    tgl_kembali TEXT DEFAULT '-',
                    denda INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    FOREIGN KEY (id_buku) REFERENCES buku (id_buku),
                    FOREIGN KEY (id_anggota) REFERENCES anggota (id_anggota)
                )
            """)
            conn.commit()

    def _parse_date(self, date_str):
        """Mendukung parsing tanggal dengan prioritas format DD/MM/YYYY"""
        date_str = str(date_str).strip()
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%Y/%m/%d",
            "%Y-%m-%d",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        return datetime.now()

    # --- METODE BUKU ---
    def tambah_buku(self, judul, pengarang, penerbit, tahun, kategori, stok):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO buku (judul, pengarang, penerbit, tahun, kategori, stok)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (judul, pengarang, penerbit, tahun, kategori, stok),
            )
            conn.commit()

    def edit_buku(self, id_buku, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE buku SET judul=?, pengarang=?, penerbit=?, tahun=?, kategori=?, stok=?
                WHERE id_buku=?
            """,
                (*data, id_buku),
            )
            conn.commit()

    def hapus_buku(self, id_buku):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM buku WHERE id_buku=?", (id_buku,))
            conn.commit()

    def tampilkan_buku(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_buku, judul, pengarang, penerbit, kategori, tahun, stok FROM buku"
            )
            return cursor.fetchall()

    # --- METODE ANGGOTA ---
    def tambah_anggota(self, nama, email, telepon, alamat, tgl_daftar):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            dt = self._parse_date(tgl_daftar)
            cursor.execute(
                """
                INSERT INTO anggota (nama, email, telepon, alamat, tgl_daftar)
                VALUES (?, ?, ?, ?, ?)
            """,
                (nama, email, telepon, alamat, dt.strftime("%d/%m/%Y")),
            )
            conn.commit()

    def edit_anggota(self, id_anggota, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            nama, email, telepon, alamat, tgl_daftar = data
            dt = self._parse_date(tgl_daftar)
            cursor.execute(
                """
                UPDATE anggota SET nama=?, email=?, telepon=?, alamat=?, tgl_daftar=?
                WHERE id_anggota=?
            """,
                (nama, email, telepon, alamat, dt.strftime("%d/%m/%Y"), id_anggota),
            )
            conn.commit()

    def hapus_anggota(self, id_anggota):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM anggota WHERE id_anggota=?", (id_anggota,))
            conn.commit()

    def tampilkan_anggota(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_anggota, nama, email, telepon, alamat, tgl_daftar FROM anggota"
            )
            return cursor.fetchall()

    # --- METODE TRANSAKSI ---
    def proses_peminjaman(self, id_buku, id_anggota, tgl_pinjam):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Cek stok buku
            cursor.execute("SELECT stok FROM buku WHERE id_buku=?", (id_buku,))
            res = cursor.fetchone()
            if not res or res[0] <= 0:
                return False, "Stok buku tidak mencukupi!"

            # Hitung jatuh tempo (+7 Hari) format DD/MM/YYYY
            dt_pinjam = self._parse_date(tgl_pinjam)
            tgl_tempo = (dt_pinjam + timedelta(days=7)).strftime("%d/%m/%Y")

            # Kurangi Stok Buku
            cursor.execute(
                "UPDATE buku SET stok = stok - 1 WHERE id_buku=?", (id_buku,)
            )

            # Catat Transaksi
            cursor.execute(
                """
                INSERT INTO peminjaman (id_buku, id_anggota, tgl_pinjam, tgl_jatuh_tempo, tgl_kembali, denda, status)
                VALUES (?, ?, ?, ?, '-', 0, 'Dipinjam')
            """,
                (id_buku, id_anggota, dt_pinjam.strftime("%d/%m/%Y"), tgl_tempo),
            )
            conn.commit()
            return True, "Peminjaman berhasil dicatat!"

    def proses_pengembalian(self, id_pinjam, tgl_kembali, denda):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Ambil ID buku untuk dikembalikan stoknya
            cursor.execute(
                "SELECT id_buku, status FROM peminjaman WHERE id_pinjam=?", (id_pinjam,)
            )
            res = cursor.fetchone()
            if not res:
                return False, "ID Transaksi tidak ditemukan!"
            if res[1] == "Dikembalikan":
                return False, "Transaksi ini sudah dikembalikan!"

            id_buku = res[0]
            dt_kembali = self._parse_date(tgl_kembali)

            # Tambah Stok Buku Kembali
            cursor.execute(
                "UPDATE buku SET stok = stok + 1 WHERE id_buku=?", (id_buku,)
            )

            # Update Transaksi
            cursor.execute(
                """
                UPDATE peminjaman SET tgl_kembali=?, denda=?, status='Dikembalikan'
                WHERE id_pinjam=?
            """,
                (dt_kembali.strftime("%d/%m/%Y"), denda, id_pinjam),
            )
            conn.commit()
            return True, "Buku berhasil dikembalikan!"

    def tampilkan_transaksi(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id_pinjam, a.nama, b.judul, p.tgl_pinjam, p.tgl_jatuh_tempo, p.tgl_kembali, p.denda, p.status
                FROM peminjaman p
                JOIN anggota a ON p.id_anggota = a.id_anggota
                JOIN buku b ON p.id_buku = b.id_buku
                ORDER BY p.id_pinjam DESC
            """)
            return cursor.fetchall()

    def get_statistik_summary(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM buku")
            tot_buku = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM anggota")
            tot_anggota = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status='Dipinjam'")
            tot_pinjam = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM peminjaman WHERE status='Dikembalikan'"
            )
            tot_kembali = cursor.fetchone()[0]

            return tot_buku, tot_anggota, tot_pinjam, tot_kembali
