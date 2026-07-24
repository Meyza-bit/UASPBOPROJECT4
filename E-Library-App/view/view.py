import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class PlaceholderEntry(ttk.Entry):
    """Entry widget khusus dengan dukungan Placeholder"""

    def __init__(self, container, placeholder="", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "#9ca3af"
        self.default_fg_color = "#1f2937"

        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self._put_placeholder()

    def _put_placeholder(self):
        self.insert(0, self.placeholder)
        self.config(foreground=self.placeholder_color)

    def _focus_in(self, *args):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg_color)

    def _focus_out(self, *args):
        if not self.get():
            self._put_placeholder()

    def get_clean_text(self):
        val = self.get().strip()
        if val == self.placeholder:
            return ""
        return val


class BaseFrame(tk.Frame):
    """Kelas Induk (Base) untuk seluruh Halaman/Frame"""

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller

    def refresh_data(self):
        pass


class DashboardPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        lbl_title = tk.Label(
            self,
            text="Dashboard Overview (DashboardPage)",
            font=("Segoe UI", 14, "bold"),
            bg="#f8fafc",
            fg="#1e293b",
        )
        lbl_title.pack(anchor="w", padx=20, pady=(15, 10))

        card_frame = tk.Frame(self, bg="#f8fafc")
        card_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.lbl_buku = self._create_card(
            card_frame, "TOTAL BUKU", "0 Judul", "#0284c7"
        )
        self.lbl_anggota = self._create_card(
            card_frame, "TOTAL ANGGOTA", "0 Orang", "#7c3aed"
        )
        self.lbl_pinjam = self._create_card(
            card_frame, "BUKU DIPINJAM", "0 Transaksi", "#ea580c"
        )
        self.lbl_kembali = self._create_card(
            card_frame, "SELESAI KEMBALI", "0 Transaksi", "#16a34a"
        )

        lbl_sub = tk.Label(
            self,
            text="Aktivitas Transaksi Terbaru (tabel_summary)",
            font=("Segoe UI", 11, "bold"),
            bg="#f8fafc",
            fg="#1e293b",
        )
        lbl_sub.pack(anchor="w", padx=20, pady=(10, 8))

        cols = ("id", "anggota", "buku", "pinjam", "tempo", "status")
        self.tabel_summary = ttk.Treeview(self, columns=cols, show="headings", height=8)
        self.tabel_summary.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        headers = [
            ("id", "ID Pinjam", 90),
            ("anggota", "Nama Anggota", 180),
            ("buku", "Judul Buku", 220),
            ("pinjam", "Tgl Pinjam", 110),
            ("tempo", "Jatuh Tempo", 110),
            ("status", "Status", 120),
        ]
        for col, heading, width in headers:
            self.tabel_summary.heading(col, text=heading)
            self.tabel_summary.column(col, anchor="center", width=width, stretch=True)

        self.tabel_summary.tag_configure(
            "Dipinjam", foreground="#ea580c", font=("Segoe UI", 9, "bold")
        )
        self.tabel_summary.tag_configure(
            "Dikembalikan", foreground="#16a34a", font=("Segoe UI", 9, "bold")
        )

    def _create_card(self, parent, title, value, color):
        f = tk.Frame(
            parent, bg="white", highlightbackground="#e2e8f0", highlightthickness=1
        )
        f.pack(side="left", fill="both", expand=True, padx=5)

        strip = tk.Frame(f, bg=color, width=4)
        strip.pack(side="left", fill="y")

        content = tk.Frame(f, bg="white")
        content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            content, text=title, font=("Segoe UI", 8, "bold"), fg="#64748b", bg="white"
        ).pack(anchor="w")
        lbl_val = tk.Label(
            content, text=value, font=("Segoe UI", 14, "bold"), fg="#0f172a", bg="white"
        )
        lbl_val.pack(anchor="w", pady=(2, 0))
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
            status = row[7]
            self.tabel_summary.insert(
                "",
                "end",
                values=(f"TRX-{row[0]:03d}", row[1], row[2], row[3], row[4], status),
                tags=(status,),
            )


class BukuPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_id = None

        tk.Label(
            self,
            text="Kelola Katalog Buku (BukuPage)",
            font=("Segoe UI", 14, "bold"),
            bg="#f8fafc",
            fg="#1e293b",
        ).pack(anchor="w", padx=20, pady=(15, 10))

        form = tk.LabelFrame(
            self,
            text="",
            bg="white",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            bd=0,
            padx=15,
            pady=10,
        )
        form.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(
            form,
            text="Judul Buku",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.input_judul = PlaceholderEntry(
            form, placeholder="Masukkan judul buku...", width=36
        )
        self.input_judul.grid(row=1, column=0, padx=(0, 15), pady=(0, 8))

        tk.Label(
            form,
            text="Pengarang",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.input_pengarang = PlaceholderEntry(
            form, placeholder="Nama pengarang...", width=36
        )
        self.input_pengarang.grid(row=1, column=1, pady=(0, 8))

        tk.Label(
            form,
            text="Penerbit",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.input_penerbit = PlaceholderEntry(
            form, placeholder="Nama penerbit...", width=36
        )
        self.input_penerbit.grid(row=3, column=0, padx=(0, 15), pady=(0, 8))

        tk.Label(
            form,
            text="Kategori",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=2, column=1, sticky="w", pady=(0, 2))
        self.input_kategori = ttk.Combobox(
            form, values=["Pemrograman", "Database", "Jaringan", "Umum"], width=34
        )
        self.input_kategori.set("Pemrograman")
        self.input_kategori.grid(row=3, column=1, pady=(0, 8))

        tk.Label(
            form,
            text="Tahun Terbit",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=4, column=0, sticky="w", pady=(0, 2))
        self.input_tahun = PlaceholderEntry(form, placeholder="2026", width=36)
        self.input_tahun.grid(row=5, column=0, padx=(0, 15))

        tk.Label(
            form,
            text="Jumlah Stok",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=4, column=1, sticky="w", pady=(0, 2))
        self.input_stok = PlaceholderEntry(form, placeholder="10", width=36)
        self.input_stok.grid(row=5, column=1)

        btn_box = tk.Frame(self, bg="#f8fafc")
        btn_box.pack(fill="x", padx=20, pady=(10, 10))

        tk.Button(
            btn_box,
            text="+ Tambah Buku",
            bg="#10b981",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.simpan_aksi,
        ).pack(side="left", padx=(0, 5))
        tk.Button(
            btn_box,
            text="Edit Buku",
            bg="#f59e0b",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.edit_aksi,
        ).pack(side="left", padx=5)
        tk.Button(
            btn_box,
            text="Hapus Buku",
            bg="#ef4444",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.hapus_aksi,
        ).pack(side="left", padx=5)
        tk.Button(
            btn_box,
            text="Reset Form",
            bg="#9ca3af",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.reset_form,
        ).pack(side="left", padx=5)

        cols = ("id", "judul", "pengarang", "penerbit", "kategori", "tahun", "stok")
        self.tabel_buku = ttk.Treeview(self, columns=cols, show="headings", height=8)
        self.tabel_buku.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols_buku = [
            ("id", "ID Buku", 60),
            ("judul", "Judul Buku", 220),
            ("pengarang", "Pengarang", 160),
            ("penerbit", "Penerbit", 140),
            ("kategori", "Kategori", 120),
            ("tahun", "Tahun", 70),
            ("stok", "Stok", 60),
        ]
        for c, h, w in cols_buku:
            self.tabel_buku.heading(c, text=h)
            self.tabel_buku.column(c, anchor="center", width=w, stretch=True)

        self.tabel_buku.bind("<<TreeviewSelect>>", self.on_select)

    def simpan_aksi(self):
        try:
            self.controller.model.tambah_buku(
                self.input_judul.get_clean_text(),
                self.input_pengarang.get_clean_text(),
                self.input_penerbit.get_clean_text(),
                int(self.input_tahun.get_clean_text()),
                self.input_kategori.get(),
                int(self.input_stok.get_clean_text()),
            )
            messagebox.showinfo("Sukses", "Buku berhasil ditambahkan!")
            self.reset_form()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", f"Input tidak valid: {e}")

    def edit_aksi(self):
        if not self.selected_id:
            messagebox.showwarning(
                "Peringatan", "Pilih data buku dari tabel lebih dulu!"
            )
            return
        data = (
            self.input_judul.get_clean_text(),
            self.input_pengarang.get_clean_text(),
            self.input_penerbit.get_clean_text(),
            int(self.input_tahun.get_clean_text()),
            self.input_kategori.get(),
            int(self.input_stok.get_clean_text()),
        )
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
            self.input_judul.delete(0, tk.END)
            self.input_judul.insert(0, vals[1])
            self.input_judul.config(foreground="#1f2937")
            self.input_pengarang.delete(0, tk.END)
            self.input_pengarang.insert(0, vals[2])
            self.input_pengarang.config(foreground="#1f2937")
            self.input_penerbit.delete(0, tk.END)
            self.input_penerbit.insert(0, vals[3])
            self.input_penerbit.config(foreground="#1f2937")
            self.input_kategori.set(vals[4])
            self.input_tahun.delete(0, tk.END)
            self.input_tahun.insert(0, vals[5])
            self.input_tahun.config(foreground="#1f2937")
            self.input_stok.delete(0, tk.END)
            self.input_stok.insert(0, vals[6])
            self.input_stok.config(foreground="#1f2937")

    def reset_form(self):
        self.selected_id = None
        for entry in (
            self.input_judul,
            self.input_pengarang,
            self.input_penerbit,
            self.input_tahun,
            self.input_stok,
        ):
            entry.delete(0, tk.END)
            entry._put_placeholder()

    def refresh_data(self):
        for item in self.tabel_buku.get_children():
            self.tabel_buku.delete(item)
        for row in self.controller.model.tampilkan_buku():
            self.tabel_buku.insert("", "end", values=row)


class AnggotaPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_id = None

        tk.Label(
            self,
            text="Kelola Anggota (AnggotaPage)",
            font=("Segoe UI", 14, "bold"),
            bg="#f8fafc",
            fg="#1e293b",
        ).pack(anchor="w", padx=20, pady=(15, 10))

        form = tk.LabelFrame(
            self,
            text="",
            bg="white",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            bd=0,
            padx=15,
            pady=10,
        )
        form.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(
            form,
            text="Nama Lengkap",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.input_nama = PlaceholderEntry(
            form, placeholder="Masukkan nama...", width=36
        )
        self.input_nama.grid(row=1, column=0, padx=(0, 15), pady=(0, 8))

        tk.Label(
            form, text="Email", bg="white", font=("Segoe UI", 9, "bold"), fg="#334155"
        ).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.input_email = PlaceholderEntry(
            form, placeholder="contoh@domain.com", width=36
        )
        self.input_email.grid(row=1, column=1, pady=(0, 8))

        tk.Label(
            form,
            text="No. Telepon",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.input_telepon = PlaceholderEntry(
            form, placeholder="08xxxxxxxxxx", width=36
        )
        self.input_telepon.grid(row=3, column=0, padx=(0, 15), pady=(0, 8))

        tk.Label(
            form,
            text="Tanggal Daftar (DD/MM/YYYY)",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
        ).grid(row=2, column=1, sticky="w", pady=(0, 2))
        self.input_tgl = ttk.Entry(form, width=36)
        self.input_tgl.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.input_tgl.grid(row=3, column=1, pady=(0, 8))

        tk.Label(
            form, text="Alamat", bg="white", font=("Segoe UI", 9, "bold"), fg="#334155"
        ).grid(row=4, column=0, sticky="w", pady=(0, 2))
        self.input_alamat = PlaceholderEntry(
            form, placeholder="Alamat lengkap...", width=77
        )
        self.input_alamat.grid(row=5, column=0, columnspan=2, sticky="w")

        btn_box = tk.Frame(self, bg="#f8fafc")
        btn_box.pack(fill="x", padx=20, pady=(10, 10))

        tk.Button(
            btn_box,
            text="+ Tambah Anggota",
            bg="#10b981",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.simpan_aksi,
        ).pack(side="left", padx=(0, 5))
        tk.Button(
            btn_box,
            text="Edit Anggota",
            bg="#f59e0b",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.edit_aksi,
        ).pack(side="left", padx=5)
        tk.Button(
            btn_box,
            text="Hapus Anggota",
            bg="#ef4444",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.hapus_aksi,
        ).pack(side="left", padx=5)
        tk.Button(
            btn_box,
            text="Reset Form",
            bg="#9ca3af",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            command=self.reset_form,
        ).pack(side="left", padx=5)

        cols = ("id", "nama", "email", "telepon", "alamat", "tgl")
        self.tabel_anggota = ttk.Treeview(self, columns=cols, show="headings", height=8)
        self.tabel_anggota.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols_anggota = [
            ("id", "ID Anggota", 80),
            ("nama", "Nama Lengkap", 180),
            ("email", "Email", 180),
            ("telepon", "Telepon", 120),
            ("alamat", "Alamat", 200),
            ("tgl", "Tgl Daftar", 100),
        ]
        for c, h, w in cols_anggota:
            self.tabel_anggota.heading(c, text=h)
            self.tabel_anggota.column(c, anchor="center", width=w, stretch=True)

        self.tabel_anggota.bind("<<TreeviewSelect>>", self.on_select)

    def simpan_aksi(self):
        self.controller.model.tambah_anggota(
            self.input_nama.get_clean_text(),
            self.input_email.get_clean_text(),
            self.input_telepon.get_clean_text(),
            self.input_alamat.get_clean_text(),
            self.input_tgl.get(),
        )
        messagebox.showinfo("Sukses", "Anggota berhasil ditambahkan!")
        self.reset_form()
        self.refresh_data()

    def edit_aksi(self):
        if not self.selected_id:
            return
        data = (
            self.input_nama.get_clean_text(),
            self.input_email.get_clean_text(),
            self.input_telepon.get_clean_text(),
            self.input_alamat.get_clean_text(),
            self.input_tgl.get(),
        )
        self.controller.model.edit_anggota(self.selected_id, data)
        messagebox.showinfo("Sukses", "Data anggota diperbarui!")
        self.reset_form()
        self.refresh_data()

    def hapus_aksi(self):
        if self.selected_id and messagebox.askyesno("Konfirmasi", "Hapus anggota ini?"):
            self.controller.model.hapus_anggota(self.selected_id)
            self.reset_form()
            self.refresh_data()

    def on_select(self, event):
        selected = self.tabel_anggota.selection()
        if selected:
            vals = self.tabel_anggota.item(selected[0], "values")
            self.selected_id = vals[0]
            self.input_nama.delete(0, tk.END)
            self.input_nama.insert(0, vals[1])
            self.input_nama.config(foreground="#1f2937")
            self.input_email.delete(0, tk.END)
            self.input_email.insert(0, vals[2])
            self.input_email.config(foreground="#1f2937")
            self.input_telepon.delete(0, tk.END)
            self.input_telepon.insert(0, vals[3])
            self.input_telepon.config(foreground="#1f2937")
            self.input_alamat.delete(0, tk.END)
            self.input_alamat.insert(0, vals[4])
            self.input_alamat.config(foreground="#1f2937")
            self.input_tgl.delete(0, tk.END)
            self.input_tgl.insert(0, vals[5])

    def reset_form(self):
        self.selected_id = None
        for entry in (
            self.input_nama,
            self.input_email,
            self.input_telepon,
            self.input_alamat,
        ):
            entry.delete(0, tk.END)
            entry._put_placeholder()

    def refresh_data(self):
        for item in self.tabel_anggota.get_children():
            self.tabel_anggota.delete(item)
        for row in self.controller.model.tampilkan_anggota():
            self.tabel_anggota.insert("", "end", values=row)


class TransaksiPage(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.selected_pinjam_id = None

        tk.Label(
            self,
            text="Sistem Transaksi (TransaksiPage)",
            font=("Segoe UI", 14, "bold"),
            bg="#f8fafc",
            fg="#1e293b",
        ).pack(anchor="w", padx=20, pady=(15, 10))

        split = tk.Frame(self, bg="#f8fafc")
        split.pack(fill="x", padx=20, pady=(0, 10))

        # --- FORM PEMINJAMAN BUKU (KIRI) ---
        f_left = tk.LabelFrame(
            split,
            text=" Form Peminjaman Buku ",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#1e293b",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            bd=0,
            padx=12,
            pady=10,
        )
        f_left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(
            f_left,
            text="Pilih Anggota",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.cb_anggota = ttk.Combobox(f_left, width=32)
        self.cb_anggota.pack(fill="x", pady=(2, 6))

        tk.Label(
            f_left,
            text="Pilih Buku",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.cb_buku = ttk.Combobox(f_left, width=32)
        self.cb_buku.pack(fill="x", pady=(2, 6))

        tk.Label(
            f_left,
            text="Tanggal Pinjam (DD/MM/YYYY)",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.entry_tgl_pinjam = ttk.Entry(f_left)
        now_str = datetime.now().strftime("%d/%m/%Y")
        self.entry_tgl_pinjam.insert(0, now_str)
        self.entry_tgl_pinjam.pack(fill="x", pady=(2, 6))

        tk.Label(
            f_left,
            text="Jatuh Tempo (Otomatis +7 Hari)",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.entry_tgl_tempo = ttk.Entry(f_left)
        tempo_str = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
        self.entry_tgl_tempo.insert(0, tempo_str)
        self.entry_tgl_tempo.pack(fill="x", pady=(2, 10))

        tk.Button(
            f_left,
            text="Proses Peminjaman",
            bg="#10b981",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            pady=5,
            command=self.proses_pinjam_aksi,
        ).pack(fill="x")

        # --- FORM PENGEMBALIAN & DENDA (KANAN) ---
        f_right = tk.LabelFrame(
            split,
            text=" Form Pengembalian & Denda ",
            bg="white",
            font=("Segoe UI", 9, "bold"),
            fg="#1e293b",
            highlightbackground="#e2e8f0",
            highlightthickness=1,
            bd=0,
            padx=12,
            pady=10,
        )
        f_right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(
            f_right,
            text="ID Transaksi Selected",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.entry_selected_id = ttk.Entry(f_right)
        self.entry_selected_id.insert(0, "TRX-000")
        self.entry_selected_id.pack(fill="x", pady=(2, 6))

        tk.Label(
            f_right,
            text="Tanggal Pengembalian (DD/MM/YYYY)",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.entry_tgl_kembali = ttk.Entry(f_right)
        self.entry_tgl_kembali.insert(0, now_str)
        self.entry_tgl_kembali.pack(fill="x", pady=(2, 6))
        self.entry_tgl_kembali.bind("<KeyRelease>", self.hitung_denda_otomatis)

        tk.Label(
            f_right,
            text="Keterlambatan",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.entry_keterlambatan = ttk.Entry(f_right)
        self.entry_keterlambatan.insert(0, "0 Hari")
        self.entry_keterlambatan.pack(fill="x", pady=(2, 6))

        tk.Label(
            f_right,
            text="Hitung Denda (Rp1.000/Hari)",
            bg="white",
            font=("Segoe UI", 8, "bold"),
            fg="#334155",
        ).pack(anchor="w")
        self.lbl_info_denda = ttk.Entry(f_right)
        self.lbl_info_denda.insert(0, "Rp 0")
        self.lbl_info_denda.pack(fill="x", pady=(2, 10))

        tk.Button(
            f_right,
            text="Proses Pengembalian Buku",
            bg="#0284c7",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            pady=5,
            command=self.proses_kembali_aksi,
        ).pack(fill="x")

        # --- TABEL RIWAYAT TRANSAKSI ---
        cols = (
            "id",
            "anggota",
            "buku",
            "pinjam",
            "tempo",
            "kembali",
            "denda",
            "status",
        )
        self.tabel_pinjam = ttk.Treeview(self, columns=cols, show="headings", height=6)
        self.tabel_pinjam.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols_trx = [
            ("id", "ID Transaksi", 100),
            ("anggota", "Nama Anggota", 150),
            ("buku", "Buku", 180),
            ("pinjam", "Tgl Pinjam", 100),
            ("tempo", "Jatuh Tempo", 100),
            ("kembali", "Tgl Kembali", 100),
            ("denda", "Denda", 90),
            ("status", "Status", 110),
        ]
        for c, h, w in cols_trx:
            self.tabel_pinjam.heading(c, text=h)
            self.tabel_pinjam.column(c, anchor="center", width=w, stretch=True)

        self.tabel_pinjam.tag_configure(
            "Dipinjam", foreground="#ea580c", font=("Segoe UI", 9, "bold")
        )
        self.tabel_pinjam.tag_configure(
            "Dikembalikan", foreground="#16a34a", font=("Segoe UI", 9, "bold")
        )

        self.tabel_pinjam.bind("<<TreeviewSelect>>", self.on_select_trx)

    def _parse_input_date(self, date_str):
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

    def hitung_denda_otomatis(self, event=None):
        if not self.selected_pinjam_id:
            return
        try:
            vals = self.tabel_pinjam.item(self.tabel_pinjam.selection()[0], "values")
            dt_tempo = self._parse_input_date(vals[4])
            dt_kembali = self._parse_input_date(self.entry_tgl_kembali.get())

            selisih_hari = (dt_kembali - dt_tempo).days
            if selisih_hari > 0:
                denda = selisih_hari * 1000
                self.entry_keterlambatan.delete(0, tk.END)
                self.entry_keterlambatan.insert(0, f"{selisih_hari} Hari")
                self.lbl_info_denda.delete(0, tk.END)
                self.lbl_info_denda.insert(0, f"Rp {denda:,}")
            else:
                self.entry_keterlambatan.delete(0, tk.END)
                self.entry_keterlambatan.insert(0, "0 Hari")
                self.lbl_info_denda.delete(0, tk.END)
                self.lbl_info_denda.insert(0, "Rp 0")
        except Exception:
            pass

    def proses_pinjam_aksi(self):
        try:
            str_anggota = self.cb_anggota.get()
            str_buku = self.cb_buku.get()

            if not str_anggota or not str_buku:
                messagebox.showwarning(
                    "Peringatan", "Pilih Anggota dan Buku terlebih dahulu!"
                )
                return

            id_anggota = int(str_anggota.split("]")[0].replace("[", "").strip())
            id_buku = int(str_buku.split("]")[0].replace("[", "").strip())
            tgl = self.entry_tgl_pinjam.get()

            success, msg = self.controller.model.proses_peminjaman(
                id_buku, id_anggota, tgl
            )
            if success:
                messagebox.showinfo("Sukses", msg)
                self.refresh_data()
            else:
                messagebox.showwarning("Gagal", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

    def proses_kembali_aksi(self):
        if not self.selected_pinjam_id:
            messagebox.showwarning("Peringatan", "Pilih transaksi dari tabel!")
            return

        vals = self.tabel_pinjam.item(self.tabel_pinjam.selection()[0], "values")
        dt_tempo = self._parse_input_date(vals[4])
        dt_kembali = self._parse_input_date(self.entry_tgl_kembali.get())

        selisih = (dt_kembali - dt_tempo).days
        denda = max(0, selisih * 1000)

        success, msg = self.controller.model.proses_pengembalian(
            self.selected_pinjam_id, self.entry_tgl_kembali.get(), denda
        )
        if success:
            messagebox.showinfo("Sukses", msg)
            self.selected_pinjam_id = None
            self.entry_selected_id.delete(0, tk.END)
            self.entry_selected_id.insert(0, "TRX-000")
            self.refresh_data()
        else:
            messagebox.showerror("Gagal", msg)

    def on_select_trx(self, event):
        selected = self.tabel_pinjam.selection()
        if selected:
            vals = self.tabel_pinjam.item(selected[0], "values")
            self.selected_pinjam_id = vals[0].replace("TRX-", "")
            self.entry_selected_id.delete(0, tk.END)
            self.entry_selected_id.insert(0, vals[0])
            self.hitung_denda_otomatis()

    def refresh_data(self):
        anggota_list = [
            f"[{a[0]}] {a[1]}" for a in self.controller.model.tampilkan_anggota()
        ]
        self.cb_anggota["values"] = anggota_list

        buku_list = [f"[{b[0]}] {b[1]}" for b in self.controller.model.tampilkan_buku()]
        self.cb_buku["values"] = buku_list

        for item in self.tabel_pinjam.get_children():
            self.tabel_pinjam.delete(item)
        for row in self.controller.model.tampilkan_transaksi():
            denda_fmt = f"Rp {row[6]:,}" if row[6] > 0 else "Rp 0"
            status = row[7]
            self.tabel_pinjam.insert(
                "",
                "end",
                values=(
                    f"TRX-{row[0]:03d}",
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    denda_fmt,
                    status,
                ),
                tags=(status,),
            )
