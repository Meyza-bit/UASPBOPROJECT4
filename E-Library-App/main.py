import tkinter as tk

# Meng-import modul dari sub-folder models dan views
from model.model import Database as DatabaseModel
from view.view import DashboardPage, BukuPage, AnggotaPage, TransaksiPage


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Informasi Manajemen E-Library (Tkinter App)")
        self.geometry("1100x680")
        self.config(bg="#f4f6f9")

        # Inisialisasi Model
        self.model = DatabaseModel("library.db")

        # Navbar Navigasi
        nav_frame = tk.Frame(self, bg="#1e293b", height=50)
        nav_frame.pack(side="top", fill="x")

        title_lbl = tk.Label(
            nav_frame,
            text="E-LIBRARY SYSTEM",
            font=("Segoe UI", 12, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
        )
        title_lbl.pack(side="left", padx=20, pady=10)

        # Tombol Navigasi
        btn_dash = tk.Button(
            nav_frame,
            text="Dashboard",
            bg="#1e293b",
            fg="white",
            bd=0,
            font=("Segoe UI", 10),
            command=lambda: self.tukar_halaman("DashboardPage"),
        )
        btn_dash.pack(side="left", padx=10)

        btn_buku = tk.Button(
            nav_frame,
            text="Kelola Buku",
            bg="#1e293b",
            fg="white",
            bd=0,
            font=("Segoe UI", 10),
            command=lambda: self.tukar_halaman("BukuPage"),
        )
        btn_buku.pack(side="left", padx=10)

        btn_anggota = tk.Button(
            nav_frame,
            text="Kelola Anggota",
            bg="#1e293b",
            fg="white",
            bd=0,
            font=("Segoe UI", 10),
            command=lambda: self.tukar_halaman("AnggotaPage"),
        )
        btn_anggota.pack(side="left", padx=10)

        btn_trans = tk.Button(
            nav_frame,
            text="Transaksi Pinjam/Kembali",
            bg="#1e293b",
            fg="white",
            bd=0,
            font=("Segoe UI", 10),
            command=lambda: self.tukar_halaman("TransaksiPage"),
        )
        btn_trans.pack(side="left", padx=10)

        # Container Utama Frame Switching
        self.container = tk.Frame(self, bg="#f4f6f9")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for PageClass in (DashboardPage, BukuPage, AnggotaPage, TransaksiPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.tukar_halaman("DashboardPage")

    def tukar_halaman(self, nama_frame):
        frame = self.frames[nama_frame]
        frame.refresh_data()
        frame.tkraise()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
