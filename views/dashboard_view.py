import customtkinter as ctk
from utils.theme import *
from utils.widgets import Table
from datetime import datetime

def fmt_money(v):
    try: return f"{float(v):,.0f}đ"
    except: return "0đ"

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, current_user_fullname):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self.fullname = current_user_fullname
        self.grid_columnconfigure(0, weight=1)

    def set_controller(self, controller):
        self.controller = controller

    def update_dashboard(self, s, occupancy, viol_rows):
        for w in self.winfo_children(): w.destroy()

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(20,8))
        Label(top, f"Xin chào, {self.fullname} 👋", size=20, bold=True).pack(side="left")
        Label(top, datetime.now().strftime("%d/%m/%Y"), size=13, color=C["text3"]).pack(side="right")

        sg = ctk.CTkFrame(self, fg_color="transparent")
        sg.pack(fill="x", padx=18, pady=4)
        for i in range(4): sg.grid_columnconfigure(i, weight=1)
        stat_card(sg, "🎓", s['total_students'], "Sinh viên đang ở", "primary", 0, 0)
        stat_card(sg, "🚪", s['available_rooms'], f"Phòng trống / {s['total_rooms']}", "green", 0, 1)
        stat_card(sg, "⏳", s['pending_payments'], "Chưa đóng tiền", "amber", 0, 2)
        stat_card(sg, "⚠️", s['open_violations'], "Vi phạm chưa xử lý", "rose", 0, 3)

        sg2 = ctk.CTkFrame(self, fg_color="transparent")
        sg2.pack(fill="x", padx=18, pady=4)
        for i in range(4): sg2.grid_columnconfigure(i, weight=1)
        stat_card(sg2, "💰", fmt_money(s['monthly_revenue']), "Doanh thu tháng này", "blue", 0, 0)
        stat_card(sg2, "🏢", s['occupied_rooms'], "Phòng đang sử dụng", "pink", 0, 1)
        stat_card(sg2, "📋", s['pending_apps'], "Đơn xin ở đang chờ", "amber", 0, 2)
        stat_card(sg2, "👷", s['total_staff'], "Nhân viên", "green", 0, 3)

        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="both", expand=True, padx=18, pady=(8,18))
        bot.grid_columnconfigure((0,1), weight=1)

        occ_card = Card(bot)
        occ_card.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        SectionTitle(occ_card, "🏢 Tỷ lệ lấp đầy theo tòa").pack(anchor="w", padx=16, pady=(12,8))
        for b in occupancy:
            pct = int(b['occupied'] / b['total_rooms'] * 100) if b['total_rooms'] else 0
            row = ctk.CTkFrame(occ_card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=4)
            Label(row, b['name'], size=13, bold=True).pack(side="left")
            Label(row, f"{pct}%", size=12, color=C["primary"]).pack(side="right")
            bar_bg = ctk.CTkFrame(occ_card, fg_color=C["bg2"], height=8, corner_radius=4)
            bar_bg.pack(fill="x", padx=16, pady=(0,4))
            bar_fg = ctk.CTkFrame(bar_bg, fg_color=C["primary2"], height=8, corner_radius=4)
            bar_fg.place(relx=0, rely=0, relheight=1, relwidth=max(pct/100, 0.02))

        vio_card = Card(bot)
        vio_card.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        SectionTitle(vio_card, "⚠️ Vi phạm gần đây").pack(anchor="w", padx=16, pady=(12,8))
        if viol_rows:
            cols = [("Sinh viên", 140), ("Loại", 130), ("Mức độ", 90)]
            t = Table(vio_card, cols, viol_rows)
            t.pack(fill="both", expand=True, padx=8, pady=(0,8))
        else:
            MutedLabel(vio_card, "✅ Không có vi phạm chưa xử lý").pack(pady=24)