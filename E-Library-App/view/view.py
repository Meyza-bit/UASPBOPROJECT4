import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class BaseFrame(tk.Frame):
    """Kelas Induk (Base) untuk seluruh Halaman/Frame"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

    def refresh_data(self):
        pass


class DashboardPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        lbl_title = tk.Label(self, text="Dashboard Overview (DashboardPage)", font=("Segoe UI", 16, "bold"), bg="#f4f6f9")
        lbl_title.pack(anchor="w", padx=20, pady=(20, 10))

        card_frame = tk.Frame(self, bg="#f4f6f9")
        card_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_buku = self._create_card(card_frame, "TOTAL BUKU", "0 Judul", "#0284c7")
        self.lbl_anggota = self._create_card(card_frame, "TOTAL ANGGOTA", "0 Orang", "#7c3aed")
        self.lbl_pinjam = self._create_card(card_frame, "BUKU DIPINJAM", "0 Transaksi", "#d97706")
        self.lbl_kembali = self._create_card(card_frame, "SELESAI KEMBALI", "0 Transaksi", "#059669")

        lbl_sub = tk.Label(self, text="Aktivitas Transaksi Terbaru (tabel_summary)", font=("Segoe UI", 12, "bold"), bg="#f4f6f9")
        lbl_sub.pack(anchor="w", padx=20, pady=(20, 10))

        columns = ("id", "anggota", "buku", "pinjam", "tempo", "status")
        self.tabel_summary = ttk.Treeview(self, columns=columns, show="headings", height=8)
        self.tabel_summary.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        headers = [("id", "ID Pinjam"), ("anggota", "Nama Anggota"), ("buku", "Judul Buku"), 
                   ("pinjam", "Tgl Pinjam"), ("tempo", "Jatuh Tempo"), ("status", "Status")]
        for col, heading in headers:
            self.tabel_summary.heading(col, text=heading)
            self.tabel_summary.column(col, anchor="center")

    def _create_card(self, parent, title, value, color):
        f = tk.Frame(parent, bg="white", highlightbackground=color, highlightthickness=2, bd=0)
        f.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(f, text=title, font=("Segoe UI", 9, "bold"), fg="#64748b", bg="white").pack(anchor="w", padx=15, pady=(15, 5))
        lbl_val = tk.Label(f, text=value, font=("Segoe UI", 16, "bold"), fg="#0f172a", bg="white")
        lbl_val.pack(anchor="w", padx=15, pady=(0, 15))
        return lbl_val

    def refresh_data(self):
        tb, ta, ap, sp = self.controller.model.get_statistik_summary()
        self.lbl_buku.config(text=f"{tb} Judul")
        self.lbl_anggota.config(text=f"{ta} Orang")
        self.lbl_pinjam.config(text=f"{ap} Transaksi")
        self.lbl_kembali.config(text=f"{sp} Transaksi")

        for item in self.tabel_summary.get_children():
            self.tabel_summary.delete(item)
        for row in self.controller.model.tampilkan_transaksi()[:5]:
            self.tabel_summary.insert("", "end", values=(f"TRX-{row[0]:03d}", row[1], row[2], row[3], row[4], row[7]))


class BukuPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_id = None

        tk.Label(self, text="Kelola Katalog Buku (BukuPage)", font=("Segoe UI", 16, "bold"), bg="#f4f6f9").pack(anchor="w", padx=20, pady=(20, 10))

        form = tk.LabelFrame(self, text=" Form Data Buku ", bg="white", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Judul Buku", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.input_judul = ttk.Entry(form, width=35)
        self.input_judul.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Pengarang", bg="white").grid(row=0, column=2, sticky="w", pady=5)
        self.input_pengarang = ttk.Entry(form, width=35)
        self.input_pengarang.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(form, text="Penerbit", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.input_penerbit = ttk.Entry(form, width=35)
        self.input_penerbit.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form, text="Kategori", bg="white").grid(row=1, column=2, sticky="w", pady=5)
        self.input_kategori = ttk.Combobox(form, values=["Pemrograman", "Database", "Jaringan", "Umum"], width=33)
        self.input_kategori.grid(row=1, column=3, padx=10, pady=5)

        tk.Label(form, text="Tahun Terbit", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.input_tahun = ttk.Entry(form, width=35)
        self.input_tahun.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(form, text="Jumlah Stok", bg="white").grid(row=2, column=2, sticky="w", pady=5)
        self.input_stok = ttk.Entry(form, width=35)
        self.input_stok.grid(row=2, column=3, padx=10, pady=5)

        btn_box = tk.Frame(self, bg="#f4f6f9")
        btn_box.pack(fill="x", padx=20, pady=5)

        tk.Button(btn_box, text="+ Tambah Buku", bg="#10b981", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.simpan_aksi).pack(side="left", padx=5)
        tk.Button(btn_box, text="Edit Buku", bg="#f59e0b", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.edit_aksi).pack(side="left", padx=5)
        tk.Button(btn_box, text="Hapus Buku", bg="#ef4444", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.hapus_aksi).pack(side="left", padx=5)
        tk.Button(btn_box, text="Reset Form", bg="#6b7280", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.reset_form).pack(side="left", padx=5)

        cols = ("id", "judul", "pengarang", "penerbit", "kategori", "tahun", "stok")
        self.tabel_buku = ttk.Treeview(self, columns=cols, show="headings")
        self.tabel_buku.pack(fill="both", expand=True, padx=20, pady=15)

        for c, h in [("id", "ID"), ("judul", "Judul Buku"), ("pengarang", "Pengarang"), ("penerbit", "Penerbit"), ("kategori", "Kategori"), ("tahun", "Tahun"), ("stok", "Stok")]:
            self.tabel_buku.heading(c, text=h)
            self.tabel_buku.column(c, anchor="center")

        self.tabel_buku.bind("<<TreeviewSelect>>", self.on_select)

    def simpan_aksi(self):
        try:
            self.controller.model.tambah_buku(
                self.input_judul.get(), self.input_pengarang.get(), self.input_penerbit.get(),
                int(self.input_tahun.get()), self.input_kategori.get(), int(self.input_stok.get())
            )
            messagebox.showinfo("Sukses", "Buku berhasil ditambahkan!")
            self.reset_form()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", f"Input tidak valid: {e}")

    def edit_aksi(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data buku dari tabel lebih dulu!")
            return
        data = (self.input_judul.get(), self.input_pengarang.get(), self.input_penerbit.get(),
                int(self.input_tahun.get()), self.input_kategori.get(), int(self.input_stok.get()))
        self.controller.model.edit_buku(self.selected_id, data)
        messagebox.showinfo("Sukses", "Data buku diperbarui!")
        self.reset_form()
        self.refresh_data()

    def hapus_aksi(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data buku yang ingin dihapus!")
            return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus buku ini?"):
            self.controller.model.hapus_buku(self.selected_id)
            self.reset_form()
            self.refresh_data()

    def on_select(self, event):
        selected = self.tabel_buku.selection()
        if selected:
            vals = self.tabel_buku.item(selected[0], "values")
            self.selected_id = vals[0]
            self.input_judul.delete(0, tk.END); self.input_judul.insert(0, vals[1])
            self.input_pengarang.delete(0, tk.END); self.input_pengarang.insert(0, vals[2])
            self.input_penerbit.delete(0, tk.END); self.input_penerbit.insert(0, vals[3])
            self.input_kategori.set(vals[4])
            self.input_tahun.delete(0, tk.END); self.input_tahun.insert(0, vals[5])
            self.input_stok.delete(0, tk.END); self.input_stok.insert(0, vals[6])

    def reset_form(self):
        self.selected_id = None
        for entry in (self.input_judul, self.input_pengarang, self.input_penerbit, self.input_tahun, self.input_stok):
            entry.delete(0, tk.END)
        self.input_kategori.set('')

    def refresh_data(self):
        for item in self.tabel_buku.get_children():
            self.tabel_buku.delete(item)
        for row in self.controller.model.tampilkan_buku():
            self.tabel_buku.insert("", "end", values=row)


class AnggotaPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_id = None

        tk.Label(self, text="Kelola Anggota (AnggotaPage)", font=("Segoe UI", 16, "bold"), bg="#f4f6f9").pack(anchor="w", padx=20, pady=(20, 10))

        form = tk.LabelFrame(self, text=" Form Data Anggota ", bg="white", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Nama Lengkap", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.input_nama = ttk.Entry(form, width=35); self.input_nama.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Email", bg="white").grid(row=0, column=2, sticky="w", pady=5)
        self.input_email = ttk.Entry(form, width=35); self.input_email.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(form, text="No. Telepon", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.input_telepon = ttk.Entry(form, width=35); self.input_telepon.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form, text="Tanggal Daftar", bg="white").grid(row=1, column=2, sticky="w", pady=5)
        self.input_tgl = ttk.Entry(form, width=35)
        self.input_tgl.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.input_tgl.grid(row=1, column=3, padx=10, pady=5)

        tk.Label(form, text="Alamat", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.input_alamat = ttk.Entry(form, width=83); self.input_alamat.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky="w")

        btn_box = tk.Frame(self, bg="#f4f6f9")
        btn_box.pack(fill="x", padx=20, pady=5)

        tk.Button(btn_box, text="+ Tambah Anggota", bg="#10b981", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.simpan_aksi).pack(side="left", padx=5)
        tk.Button(btn_box, text="Edit Anggota", bg="#f59e0b", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.edit_aksi).pack(side="left", padx=5)
        tk.Button(btn_box, text="Hapus Anggota", bg="#ef4444", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.hapus_aksi).pack(side="left", padx=5)
        tk.Button(btn_box, text="Reset Form", bg="#6b7280", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.reset_form).pack(side="left", padx=5)

        cols = ("id", "nama", "email", "telepon", "alamat", "tgl")
        self.tabel_anggota = ttk.Treeview(self, columns=cols, show="headings")
        self.tabel_anggota.pack(fill="both", expand=True, padx=20, pady=15)

        for c, h in [("id", "ID"), ("nama", "Nama Lengkap"), ("email", "Email"), ("telepon", "Telepon"), ("alamat", "Alamat"), ("tgl", "Tgl Daftar")]:
            self.tabel_anggota.heading(c, text=h)
            self.tabel_anggota.column(c, anchor="center")

        self.tabel_anggota.bind("<<TreeviewSelect>>", self.on_select)

    def simpan_aksi(self):
        self.controller.model.tambah_anggota(
            self.input_nama.get(), self.input_email.get(), self.input_telepon.get(),
            self.input_alamat.get(), self.input_tgl.get()
        )
        messagebox.showinfo("Sukses", "Anggota berhasil ditambahkan!")
        self.reset_form(); self.refresh_data()

    def edit_aksi(self):
        if not self.selected_id: return
        data = (self.input_nama.get(), self.input_email.get(), self.input_telepon.get(),
                self.input_alamat.get(), self.input_tgl.get())
        self.controller.model.edit_anggota(self.selected_id, data)
        messagebox.showinfo("Sukses", "Data anggota diperbarui!")
        self.reset_form(); self.refresh_data()

    def hapus_aksi(self):
        if self.selected_id and messagebox.askyesno("Konfirmasi", "Hapus anggota ini?"):
            self.controller.model.hapus_anggota(self.selected_id)
            self.reset_form(); self.refresh_data()

    def on_select(self, event):
        selected = self.tabel_anggota.selection()
        if selected:
            vals = self.tabel_anggota.item(selected[0], "values")
            self.selected_id = vals[0]
            self.input_nama.delete(0, tk.END); self.input_nama.insert(0, vals[1])
            self.input_email.delete(0, tk.END); self.input_email.insert(0, vals[2])
            self.input_telepon.delete(0, tk.END); self.input_telepon.insert(0, vals[3])
            self.input_alamat.delete(0, tk.END); self.input_alamat.insert(0, vals[4])
            self.input_tgl.delete(0, tk.END); self.input_tgl.insert(0, vals[5])

    def reset_form(self):
        self.selected_id = None
        for entry in (self.input_nama, self.input_email, self.input_telepon, self.input_alamat):
            entry.delete(0, tk.END)

    def refresh_data(self):
        for item in self.tabel_anggota.get_children():
            self.tabel_anggota.delete(item)
        for row in self.controller.model.tampilkan_anggota():
            self.tabel_anggota.insert("", "end", values=row)


class TransaksiPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_pinjam_id = None

        tk.Label(self, text="Sistem Transaksi (TransaksiPage)", font=("Segoe UI", 16, "bold"), bg="#f4f6f9").pack(anchor="w", padx=20, pady=(20, 10))

        split = tk.Frame(self, bg="#f4f6f9")
        split.pack(fill="x", padx=20, pady=5)

        # Form Peminjaman
        f_left = tk.LabelFrame(split, text=" Form Peminjaman Buku ", bg="white", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        f_left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(f_left, text="Pilih Anggota", bg="white").pack(anchor="w")
        self.cb_anggota = ttk.Combobox(f_left, width=35)
        self.cb_anggota.pack(fill="x", pady=5)

        tk.Label(f_left, text="Pilih Buku", bg="white").pack(anchor="w")
        self.cb_buku = ttk.Combobox(f_left, width=35)
        self.cb_buku.pack(fill="x", pady=5)

        tk.Label(f_left, text="Tanggal Pinjam (YYYY-MM-DD)", bg="white").pack(anchor="w")
        self.entry_tgl_pinjam = ttk.Entry(f_left)
        self.entry_tgl_pinjam.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_tgl_pinjam.pack(fill="x", pady=5)

        tk.Button(f_left, text="Proses Peminjaman", bg="#10b981", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.proses_pinjam_aksi).pack(fill="x", pady=(15, 0))

        # Form Pengembalian
        f_right = tk.LabelFrame(split, text=" Form Pengembalian & Denda ", bg="white", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        f_right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(f_right, text="ID Transaksi Selected", bg="white").pack(anchor="w")
        self.lbl_selected_trx = tk.Label(f_right, text="[ Pilih dari tabel ]", font=("Segoe UI", 10, "italic"), bg="white", fg="#0284c7")
        self.lbl_selected_trx.pack(anchor="w", pady=5)

        tk.Label(f_right, text="Tanggal Pengembalian (YYYY-MM-DD)", bg="white").pack(anchor="w")
        self.entry_tgl_kembali = ttk.Entry(f_right)
        self.entry_tgl_kembali.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_tgl_kembali.pack(fill="x", pady=5)
        self.entry_tgl_kembali.bind("<KeyRelease>", self.hitung_denda_otomatis)

        self.lbl_info_denda = tk.Label(f_right, text="Hitung Denda: Rp 0", font=("Segoe UI", 11, "bold"), fg="#ef4444", bg="white")
        self.lbl_info_denda.pack(anchor="w", pady=10)

        tk.Button(f_right, text="Proses Pengembalian Buku", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.proses_kembali_aksi).pack(fill="x", pady=(5, 0))

        # Tabel Riwayat Transaksi
        cols = ("id", "anggota", "buku", "pinjam", "tempo", "kembali", "denda", "status")
        self.tabel_pinjam = ttk.Treeview(self, columns=cols, show="headings")
        self.tabel_pinjam.pack(fill="both", expand=True, padx=20, pady=15)

        for c, h in [("id", "ID Transaksi"), ("anggota", "Nama Anggota"), ("buku", "Buku"), ("pinjam", "Tgl Pinjam"), ("tempo", "Jatuh Tempo"), ("kembali", "Tgl Kembali"), ("denda", "Denda"), ("status", "Status")]:
            self.tabel_pinjam.heading(c, text=h)
            self.tabel_pinjam.column(c, anchor="center")

        self.tabel_pinjam.bind("<<TreeviewSelect>>", self.on_select_trx)

    def hitung_denda_otomatis(self, event=None):
        if not self.selected_pinjam_id: return
        try:
            vals = self.tabel_pinjam.item(self.tabel_pinjam.selection()[0], "values")
            dt_tempo = datetime.strptime(vals[4], "%Y-%m-%d")
            dt_kembali = datetime.strptime(self.entry_tgl_kembali.get(), "%Y-%m-%d")
            
            selisih_hari = (dt_kembali - dt_tempo).days
            if selisih_hari > 0:
                denda = selisih_hari * 1000
                self.lbl_info_denda.config(text=f"Terlambat {selisih_hari} Hari | Denda: Rp {denda:,}")
            else:
                self.lbl_info_denda.config(text="Tepat Waktu | Denda: Rp 0")
        except Exception:
            self.lbl_info_denda.config(text="Format Tanggal Salah!")

    def proses_pinjam_aksi(self):
        try:
            id_anggota = self.cb_anggota.get().split(" - ")[0]
            id_buku = self.cb_buku.get().split(" - ")[0]
            tgl = self.entry_tgl_pinjam.get()

            success, msg = self.controller.model.proses_peminjaman(id_buku, id_anggota, tgl)
            if success:
                messagebox.showinfo("Sukses", msg)
                self.refresh_data()
            else:
                messagebox.showwarning("Gagal", msg)
        except Exception:
            messagebox.showerror("Error", "Pilih Anggota dan Buku dengan benar!")

    def proses_kembali_aksi(self):
        if not self.selected_pinjam_id:
            messagebox.showwarning("Peringatan", "Pilih transaksi dari tabel!")
            return
        
        vals = self.tabel_pinjam.item(self.tabel_pinjam.selection()[0], "values")
        dt_tempo = datetime.strptime(vals[4], "%Y-%m-%d")
        dt_kembali = datetime.strptime(self.entry_tgl_kembali.get(), "%Y-%m-%d")
        selisih = (dt_kembali - dt_tempo).days
        denda = max(0, selisih * 1000)

        success, msg = self.controller.model.proses_pengembalian(self.selected_pinjam_id, self.entry_tgl_kembali.get(), denda)
        if success:
            messagebox.showinfo("Sukses", msg)
            self.selected_pinjam_id = None
            self.lbl_selected_trx.config(text="[ Pilih dari tabel ]")
            self.refresh_data()
        else:
            messagebox.showerror("Gagal", msg)

    def on_select_trx(self, event):
        selected = self.tabel_pinjam.selection()
        if selected:
            vals = self.tabel_pinjam.item(selected[0], "values")
            if vals[7] == 'Dipinjam':
                self.selected_pinjam_id = vals[0].replace("TRX-", "")
                self.lbl_selected_trx.config(text=f"{vals[0]} ({vals[1]})")
                self.hitung_denda_otomatis()

    def refresh_data(self):
        anggota_list = [f"{a[0]} - {a[1]}" for a in self.controller.model.tampilkan_anggota()]
        self.cb_anggota['values'] = anggota_list

        buku_list = [f"{b[0]} - {b[1]} (Stok: {b[6]})" for b in self.controller.model.tampilkan_buku()]
        self.cb_buku['values'] = buku_list

        for item in self.tabel_pinjam.get_children():
            self.tabel_pinjam.delete(item)
        for row in self.controller.model.tampilkan_transaksi():
            denda_fmt = f"Rp {row[6]:,}" if row[6] > 0 else "Rp 0"
            self.tabel_pinjam.insert("", "end", values=(f"TRX-{row[0]:03d}", row[1], row[2], row[3], row[4], row[5], denda_fmt, row[7]))