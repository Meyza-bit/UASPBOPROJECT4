from datetime import datetime
import os
import sqlite3


class Database:
    """Kelas dasar untuk mengelola koneksi dan pembuatan tabel SQLite."""

    def __init__(self, db_name="database/elibrary.db"):
        self.db_name = db_name

        # Memastikan folder 'database/' dibuat otomatis jika belum ada
        db_dir = os.path.dirname(self.db_name)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabel Buku
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS buku (
                    id_buku INTEGER PRIMARY KEY AUTOINCREMENT,
                    judul TEXT NOT NULL,
                    pengarang TEXT NOT NULL,
                    penerbit TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    tahun TEXT NOT NULL,
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

            # Tabel Peminjaman/Transaksi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS peminjaman (
                    id_transaksi TEXT PRIMARY KEY,
                    id_anggota INTEGER NOT NULL,
                    id_buku INTEGER NOT NULL,
                    tgl_pinjam TEXT NOT NULL,
                    jatuh_tempo TEXT NOT NULL,
                    tgl_kembali TEXT,
                    denda INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    FOREIGN KEY(id_anggota) REFERENCES anggota(id_anggota),
                    FOREIGN KEY(id_buku) REFERENCES buku(id_buku)
                )
            """)
            conn.commit()


class BukuModel(Database):
    """Model untuk pengelolaan data Buku."""

    def create(self, judul, pengarang, penerbit, kategori, tahun, stok):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO buku (judul, pengarang, penerbit, kategori, tahun, stok)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (judul, pengarang, penerbit, kategori, tahun, stok),
            )
            conn.commit()

    def read_all(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM buku")
            return cursor.fetchall()

    def update(
        self, id_buku, judul, pengarang, penerbit, kategori, tahun, stok
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE buku 
                SET judul=?, pengarang=?, penerbit=?, kategori=?, tahun=?, stok=?
                WHERE id_buku=?
            """,
                (judul, pengarang, penerbit, kategori, tahun, stok, id_buku),
            )
            conn.commit()

    def delete(self, id_buku):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM buku WHERE id_buku=?", (id_buku,)
            )
            conn.commit()


class AnggotaModel(Database):
    """Model untuk pengelolaan data Anggota (CRUD)."""

    def create(self, nama, email, telepon, alamat, tgl_daftar):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO anggota (nama, email, telepon, alamat, tgl_daftar)
                VALUES (?, ?, ?, ?, ?)
            """,
                (nama, email, telepon, alamat, tgl_daftar),
            )
            conn.commit()

    def read_all(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM anggota")
            return cursor.fetchall()

    def update(self, id_anggota, nama, email, telepon, alamat, tgl_daftar):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE anggota 
                SET nama=?, email=?, telepon=?, alamat=?, tgl_daftar=?
                WHERE id_anggota=?
            """,
                (nama, email, telepon, alamat, tgl_daftar, id_anggota),
            )
            conn.commit()

    def delete(self, id_anggota):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM anggota WHERE id_anggota=?", (id_anggota,)
            )
            conn.commit()


class PeminjamanModel(Database):
    """Model transaksi Peminjaman & Pengembalian dengan denda otomatis Rp1.000/hari."""

    def catat_pinjam(self, id_anggota, id_buku, tgl_pinjam, jatuh_tempo):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Cek ketersediaan stok
            cursor.execute(
                "SELECT stok FROM buku WHERE id_buku = ?", (id_buku,)
            )
            res = cursor.fetchone()
            if not res or res[0] <= 0:
                return False, "Stok buku tidak tersedia!"

            # Generate ID Transaksi Otomatis yang aman dari duplikasi
            cursor.execute(
                "SELECT id_transaksi FROM peminjaman ORDER BY id_transaksi DESC LIMIT 1"
            )
            last_trx = cursor.fetchone()
            if last_trx:
                # Mengambil nomor dari format 'TRX-001'
                last_id = int(last_trx[0].split("-")[1])
                new_id = last_id + 1
            else:
                new_id = 1

            id_transaksi = f"TRX-{new_id:03d}"

            # Kurangi stok buku
            cursor.execute(
                "UPDATE buku SET stok = stok - 1 WHERE id_buku = ?", (id_buku,)
            )

            # Catat transaksi peminjaman
            cursor.execute(
                """
                INSERT INTO peminjaman (id_transaksi, id_anggota, id_buku, tgl_pinjam, jatuh_tempo, status)
                VALUES (?, ?, ?, ?, ?, 'Dipinjam')
            """,
                (id_transaksi, id_anggota, id_buku, tgl_pinjam, jatuh_tempo),
            )
            conn.commit()
            return True, f"Peminjaman berhasil! Kode: {id_transaksi}"

    def hitung_denda_otomatis(
        self, tgl_jatuh_tempo, tgl_kembali, tarif_per_hari=1000
    ):
        """Menghitung denda otomatis Rp1.000 / hari keterlambatan."""
        try:
            fmt = "%Y-%m-%d"
            d_tempo = datetime.strptime(tgl_jatuh_tempo, fmt)
            d_kembali = datetime.strptime(tgl_kembali, fmt)

            hari_terlambat = (d_kembali - d_tempo).days
            if hari_terlambat > 0:
                return hari_terlambat * tarif_per_hari
            return 0
        except Exception:
            return 0

    def catat_kembali(self, id_transaksi, tgl_kembali):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id_buku, jatuh_tempo, status FROM peminjaman WHERE id_transaksi = ?",
                (id_transaksi,),
            )
            row = cursor.fetchone()

            if not row:
                return False, "ID Transaksi tidak ditemukan!"

            id_buku, jatuh_tempo, status = row
            if status == "Dikembalikan":
                return False, "Buku ini sudah dikembalikan!"

            # Hitung denda
            denda = self.hitung_denda_otomatis(
                jatuh_tempo, tgl_kembali, tarif_per_hari=1000
            )

            # Kembalikan stok buku (+1)
            cursor.execute(
                "UPDATE buku SET stok = stok + 1 WHERE id_buku = ?", (id_buku,)
            )

            # Update status transaksi
            cursor.execute(
                """
                UPDATE peminjaman 
                SET tgl_kembali = ?, denda = ?, status = 'Dikembalikan'
                WHERE id_transaksi = ?
            """,
                (tgl_kembali, denda, id_transaksi),
            )
            conn.commit()
            return (
                True,
                f"Buku dikembalikan! Denda keterlambatan: Rp{denda:,}",
            )

    def get_all_peminjaman_joined(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.id_transaksi, 
                    a.nama AS nama_anggota, 
                    b.judul AS judul_buku, 
                    p.tgl_pinjam, 
                    p.jatuh_tempo, 
                    COALESCE(p.tgl_kembali, '-'), 
                    'Rp ' || p.denda, 
                    p.status
                FROM peminjaman p
                JOIN anggota a ON p.id_anggota = a.id_anggota
                JOIN buku b ON p.id_buku = b.id_buku
                ORDER BY p.id_transaksi DESC
            """
            cursor.execute(query)
            return cursor.fetchall()

    def get_dashboard_summary(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(stok) FROM buku")
            total_buku = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM anggota")
            total_anggota = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT COUNT(*) FROM peminjaman WHERE status = 'Dipinjam'"
            )
            buku_dipinjam = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT COUNT(*) FROM peminjaman WHERE status = 'Dikembalikan'"
            )
            selesai_kembali = cursor.fetchone()[0] or 0

            return {
                "total_buku": total_buku,
                "total_anggota": total_anggota,
                "buku_dipinjam": buku_dipinjam,
                "selesai_kembali": selesai_kembali,
            }