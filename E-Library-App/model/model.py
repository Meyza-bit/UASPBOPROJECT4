from datetime import datetime
import os
import sqlite3


class Database:
    """Kelas Utama Mengelola DB dan Seluruh Operasi Model (Crud & Transaksi)"""

    def __init__(self, db_name="database/elibrary.db"):
        self.db_name = db_name
        db_dir = os.path.dirname(self.db_name)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
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

    # --- CRUD BUKU ---
    def tambah_buku(self, judul, pengarang, penerbit, tahun, kategori, stok):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO buku (judul, pengarang, penerbit, kategori, tahun, stok)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (judul, pengarang, penerbit, kategori, str(tahun), stok),
            )
            conn.commit()

    def tampilkan_buku(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM buku")
            return cursor.fetchall()

    def edit_buku(self, id_buku, data):
        # data = (judul, pengarang, penerbit, tahun, kategori, stok)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE buku 
                SET judul=?, pengarang=?, penerbit=?, tahun=?, kategori=?, stok=?
                WHERE id_buku=?
            """,
                (
                    data[0],
                    data[1],
                    data[2],
                    str(data[3]),
                    data[4],
                    data[5],
                    id_buku,
                ),
            )
            conn.commit()

    def hapus_buku(self, id_buku):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM buku WHERE id_buku=?", (id_buku,))
            conn.commit()

    # --- CRUD ANGGOTA ---
    def tambah_anggota(self, nama, email, telepon, alamat, tgl_daftar):
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

    def tampilkan_anggota(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM anggota")
            return cursor.fetchall()

    def edit_anggota(self, id_anggota, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE anggota 
                SET nama=?, email=?, telepon=?, alamat=?, tgl_daftar=?
                WHERE id_anggota=?
            """,
                (data[0], data[1], data[2], data[3], data[4], id_anggota),
            )
            conn.commit()

    def hapus_anggota(self, id_anggota):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM anggota WHERE id_anggota=?", (id_anggota,))
            conn.commit()

    # --- TRANSAKSI & DASHBOARD ---
    def get_statistik_summary(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(stok) FROM buku")
            tb = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM anggota")
            ta = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dipinjam'")
            ap = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT COUNT(*) FROM peminjaman WHERE status = 'Dikembalikan'"
            )
            sp = cursor.fetchone()[0] or 0

            return tb, ta, ap, sp

    def proses_peminjaman(self, id_buku, id_anggota, tgl_pinjam):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stok FROM buku WHERE id_buku = ?", (id_buku,))
            res = cursor.fetchone()
            if not res or res[0] <= 0:
                return False, "Stok buku tidak tersedia!"

            cursor.execute(
                "SELECT id_transaksi FROM peminjaman ORDER BY id_transaksi DESC LIMIT 1"
            )
            last_trx = cursor.fetchone()
            new_id = int(last_trx[0].split("-")[1]) + 1 if last_trx else 1
            id_transaksi = f"TRX-{new_id:03d}"

            # Jatuh tempo otomatis 7 hari
            dt_pinjam = datetime.strptime(tgl_pinjam, "%Y-%m-%d")
            jatuh_tempo = (dt_pinjam.replace(day=dt_pinjam.day + 7)).strftime(
                "%Y-%m-%d"
            )

            cursor.execute(
                "UPDATE buku SET stok = stok - 1 WHERE id_buku = ?", (id_buku,)
            )
            cursor.execute(
                """
                INSERT INTO peminjaman (id_transaksi, id_anggota, id_buku, tgl_pinjam, jatuh_tempo, status)
                VALUES (?, ?, ?, ?, ?, 'Dipinjam')
            """,
                (id_transaksi, id_anggota, id_buku, tgl_pinjam, jatuh_tempo),
            )
            conn.commit()
            return True, f"Peminjaman berhasil! Kode: {id_transaksi}"

    def proses_pengembalian(self, id_transaksi, tgl_kembali, denda):
        # Format ID transaksi di database adalah string 'TRX-001'
        if not id_transaksi.startswith("TRX-"):
            id_transaksi = f"TRX-{int(id_transaksi):03d}"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_buku, status FROM peminjaman WHERE id_transaksi = ?",
                (id_transaksi,),
            )
            row = cursor.fetchone()
            if not row:
                return False, "ID Transaksi tidak ditemukan!"

            id_buku, status = row
            if status == "Dikembalikan":
                return False, "Buku ini sudah dikembalikan!"

            cursor.execute(
                "UPDATE buku SET stok = stok + 1 WHERE id_buku = ?", (id_buku,)
            )
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
                f"Buku berhasil dikembalikan! Denda keterlambatan: Rp{denda:,}",
            )

    def tampilkan_transaksi(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    CAST(SUBSTR(p.id_transaksi, 5) AS INTEGER) AS id_num, 
                    a.nama AS nama_anggota, 
                    b.judul AS judul_buku, 
                    p.tgl_pinjam, 
                    p.jatuh_tempo, 
                    COALESCE(p.tgl_kembali, '-'), 
                    p.denda, 
                    p.status
                FROM peminjaman p
                JOIN anggota a ON p.id_anggota = a.id_anggota
                JOIN buku b ON p.id_buku = b.id_buku
                ORDER BY p.id_transaksi DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
