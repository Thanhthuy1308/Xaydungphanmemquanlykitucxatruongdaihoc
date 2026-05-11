import customtkinter as ctk
from utils.theme import setup_theme, C, FONT_FAMILY, Label, MutedLabel, Card
from models import database as db
from controllers.main_controller import MainController

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        setup_theme()
        self.title("KTX Manager — Đăng nhập")
        self.geometry("520x620")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 460) // 2
        y = (self.winfo_screenheight() - 560) // 2
        self.geometry(f"+{x}+{y}")
        self._build()

    def _build(self):
        # accent strip
        ctk.CTkFrame(self, fg_color=C["primary"], corner_radius=0, height=5).pack(fill="x")

        # logo area
        logo = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0)
        logo.pack(fill="x")
        ctk.CTkLabel(logo, text="🏢", font=ctk.CTkFont(size=64)).pack(pady=(30,6))
        Label(logo, "KTX SMART MANAGER", size=28, bold=True).pack()
        MutedLabel(logo, "Hệ thống Quản lý Ký Túc Xá Đại Học").pack(pady=(2,20))

        # card
        card = Card(self)
        card.pack(padx=42, pady=24, fill="x")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=28, pady=24, fill="x")

        Label(inner, "Đăng nhập hệ thống", size=16, bold=True).pack(anchor="w")
        MutedLabel(inner, "Dành cho Ban quản lý Ký Túc Xá").pack(anchor="w", pady=(2,16))

        ctk.CTkLabel(inner, text="Tên đăng nhập",
                     font=ctk.CTkFont(FONT_FAMILY, 11, "bold"),
                     text_color=C["text2"]).pack(anchor="w")
        self.username = ctk.CTkEntry(inner, placeholder_text="Nhập tên đăng nhập...",
                                      fg_color=C["white"], border_color=C["border"],
                                      text_color=C["text"], corner_radius=8, height=38,
                                      font=ctk.CTkFont(FONT_FAMILY, 13))
        self.username.pack(fill="x", pady=(4,12))

        ctk.CTkLabel(inner, text="Mật khẩu",
                     font=ctk.CTkFont(FONT_FAMILY, 11, "bold"),
                     text_color=C["text2"]).pack(anchor="w")
        self.password = ctk.CTkEntry(inner, placeholder_text="Nhập mật khẩu...",
                                      show="●", fg_color=C["white"],
                                      border_color=C["border"], text_color=C["text"],
                                      corner_radius=8, height=38,
                                      font=ctk.CTkFont(FONT_FAMILY, 13))
        self.password.pack(fill="x", pady=(4,6))

        self.err_lbl = ctk.CTkLabel(inner, text="",
                                     font=ctk.CTkFont(FONT_FAMILY, 12),
                                     text_color=C["rose"])
        self.err_lbl.pack(pady=(4,0))

        # LOGIN BUTTON — full width, không dùng PrimaryBtn để tránh width=0 bug
        ctk.CTkButton(inner, text="🔓  Đăng nhập hệ thống",
                      command=self._login, height=46, corner_radius=8,
                      fg_color=C["primary"], hover_color=C["accent"],
                      text_color=C["white"],
                      font=ctk.CTkFont(FONT_FAMILY, 14, "bold")
                      ).pack(fill="x", pady=(18, 0))

        # footer
        ctk.CTkFrame(self, fg_color=C["border"], height=1).pack(fill="x", padx=36)
        MutedLabel(self, "🔒  Hệ thống nội bộ — Chỉ dành cho Ban quản lý").pack(pady=12)

        self.username.bind("<Return>", lambda e: self.password.focus())
        self.password.bind("<Return>", lambda e: self._login())
        self.username.focus()

    def _login(self):
        user = db.login(self.username.get().strip(), self.password.get())
        if user:
            self.withdraw()
            MainApp(user).mainloop()
        else:
            self.err_lbl.configure(text="❌  Tên đăng nhập hoặc mật khẩu không đúng!")
            self.password.delete(0, "end")
            self.password.focus()


class MainApp(ctk.CTkToplevel):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.title("KTX Manager — Ban Quản lý Ký Túc Xá")
        self.geometry("1200x720")
        self.minsize(960, 620)
        self.configure(fg_color=C["bg"])
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-1200)//2}+{(sh-720)//2}")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.main_controller = MainController(self, current_user)
        self._active_btn = None
        self._nav_btns   = {}
        self._build_ui()
        self._on_sidebar_click("dashboard")

    def _build_ui(self):
        ctk.CTkFrame(self, fg_color=C["border"], corner_radius=0, height=1).pack(fill="x")
        container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(container, fg_color=C["bg2"], corner_radius=0,
                                     width=230, border_width=1, border_color=C["border"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo = ctk.CTkFrame(self.sidebar, fg_color=C["bg2"], corner_radius=0, height=76)
        logo.pack(fill="x"); logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="🏠  KTX Manager",
                     font=ctk.CTkFont(FONT_FAMILY, 16, "bold"),
                     text_color=C["primary"]).pack(anchor="w", padx=18, pady=(18,2))
        ctk.CTkLabel(logo, text="Ban Quản lý Ký Túc Xá",
                     font=ctk.CTkFont(FONT_FAMILY, 10),
                     text_color=C["text2"]).pack(anchor="w", padx=18)
        ctk.CTkFrame(self.sidebar, fg_color=C["border"], corner_radius=0, height=1).pack(fill="x")

        nav_groups = [
            ("TỔNG QUAN", [("dashboard","📊","Dashboard")]),
            ("CƠ SỞ VẬT CHẤT", [
                ("buildings","🏢","Tòa nhà"),
                ("rooms","🚪","Phòng ở"),
            ]),
            ("QUẢN LÝ", [
                ("students","🎓","Sinh viên"),
                ("payments","💰","Thu tiền phòng"),
                ("invoices","🧾","Hóa đơn"),
                ("violations","⚠️","Vi phạm nội quy"),
                ("applications","📋","Đơn xin ở KTX"),
            ]),
        ]
        if self.current_user['role'] == 'admin':
            nav_groups.append(("NHÂN SỰ", [("staff","👷","Nhân viên & Bảo vệ")]))
        nav_groups.append(("BÁO CÁO", [
            ("reports","📈","Thống kê & Báo cáo"),
            ("revenue","💰","Doanh thu tháng"),
        ]))

        nav_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        nav_scroll.pack(fill="both", expand=True, pady=6)

        for group_label, items in nav_groups:
            ctk.CTkLabel(nav_scroll, text=group_label,
                         font=ctk.CTkFont(FONT_FAMILY, 9, "bold"),
                         text_color=C["text3"]).pack(anchor="w", padx=18, pady=(12,4))
            for page_id, icon, label in items:
                btn = ctk.CTkButton(
                    nav_scroll, text=f"  {icon}  {label}", anchor="w",
                    height=40, corner_radius=8, border_spacing=8,
                    fg_color="transparent", text_color=C["text2"],
                    hover_color=C["primary3"],
                    font=ctk.CTkFont(FONT_FAMILY, 12),
                    command=lambda p=page_id: self._on_sidebar_click(p)
                )
                btn.pack(fill="x", padx=10, pady=2)
                self._nav_btns[page_id] = btn

        # user card
        uc = ctk.CTkFrame(self.sidebar, fg_color=C["card2"], corner_radius=8,
                          border_width=1, border_color=C["border"], height=64)
        uc.pack(fill="x", padx=12, pady=12); uc.pack_propagate(False)
        av = ctk.CTkFrame(uc, fg_color=C["primary"], width=34, height=34, corner_radius=17)
        av.pack(side="left", padx=(10,8), pady=13); av.pack_propagate(False)
        ctk.CTkLabel(av, text=(self.current_user['fullname'] or 'A')[0].upper(),
                     font=ctk.CTkFont(FONT_FAMILY, 14, "bold"),
                     text_color=C["white"]).place(relx=0.5, rely=0.5, anchor="center")
        inf = ctk.CTkFrame(uc, fg_color="transparent")
        inf.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(inf, text=self.current_user['fullname'] or self.current_user['username'],
                     font=ctk.CTkFont(FONT_FAMILY, 11, "bold"),
                     text_color=C["text"]).pack(anchor="w")
        ctk.CTkLabel(inf, text="Quản trị viên" if self.current_user['role']=='admin' else "Nhân viên",
                     font=ctk.CTkFont(FONT_FAMILY, 10),
                     text_color=C["text3"]).pack(anchor="w")
        ctk.CTkButton(uc, text="⏻", width=28, height=28,
                      fg_color="transparent", hover_color=C["rose_bg"],
                      text_color=C["rose"], font=ctk.CTkFont(size=16),
                      command=self._on_close).pack(side="right", padx=8)

        # ── Content area ─────────────────────────────────────────────
        self.content = ctk.CTkFrame(container, fg_color=C["bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _on_sidebar_click(self, page_id):
        if self._active_btn:
            self._active_btn.configure(fg_color="transparent", text_color=C["text2"],
                                       hover_color=C["primary3"])
        btn = self._nav_btns.get(page_id)
        if btn:
            btn.configure(fg_color=C["primary"], text_color=C["white"],
                          hover_color=C["accent"])
            self._active_btn = btn
        self.main_controller.switch_page(page_id)

    def _on_close(self):
        self.destroy()
        import sys; sys.exit(0)


if __name__ == "__main__":
    db.init_db()
    LoginWindow().mainloop()
