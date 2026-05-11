
import customtkinter as ctk
from utils.theme import *

def fmt_money(v):
    try: return f"{float(v):,.0f}đ"
    except (TypeError, ValueError): return "0đ"

class ReportsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, controller):
        self.controller = controller

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "📈 Báo cáo & Thống kê").pack(side="left", padx=20, pady=16)

        # Khung cuộn chứa các Card thống kê
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        self.scroll.pack(fill="both", expand=True, padx=16, pady=16)
        self.scroll.grid_columnconfigure((0,1), weight=1)

    def update_ui(self, occupancy, revenue, violation_counts):
        # Xóa các card cũ nếu có (để refresh làm mới dữ liệu)
        for w in self.scroll.winfo_children(): 
            w.destroy()

        # ── 1. CARD LẤP ĐẦY TÒA NHÀ ──
        oc = Card(self.scroll)
        oc.grid(row=0, column=0, columnspan=2, padx=4, pady=6, sticky="ew")
        SectionTitle(oc, "🏢 Tình trạng lấp đầy theo tòa nhà").pack(anchor="w", padx=16, pady=(12,4))
        
        for b in occupancy:
            pct = int(b['occupied']/b['total_rooms']*100) if b['total_rooms'] else 0
            row = ctk.CTkFrame(oc, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            Label(row, b['name'], size=13, bold=True).pack(side="left", padx=(0,8))
            Label(row, f"{b['occupied']}/{b['total_rooms']} phòng  •  {b['total_students']} SV", size=12, color=C["text2"]).pack(side="left")
            Label(row, f"{pct}%", size=13, bold=True, color=C["primary"]).pack(side="right")
            bar_bg = ctk.CTkFrame(oc, fg_color=C["bg2"], height=10, corner_radius=5)
            bar_bg.pack(fill="x", padx=16, pady=(0,6))
            ctk.CTkFrame(bar_bg, fg_color=C["primary2"], height=10, corner_radius=5).place(relx=0, rely=0, relheight=1, relwidth=max(pct/100, 0.02))

        # ── 2. CARD DOANH THU ──
        rc = Card(self.scroll)
        rc.grid(row=1, column=0, padx=4, pady=6, sticky="nsew")
        SectionTitle(rc, "💰 Doanh thu 6 tháng gần nhất").pack(anchor="w", padx=16, pady=(12,4))
        
        if revenue:
            max_v = max(r['total'] for r in revenue) or 1
            for r in revenue:
                pct = int(r['collected']/max_v*100)
                row = ctk.CTkFrame(rc, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=3)
                Label(row, r['month'], size=12, bold=True).pack(side="left", padx=(0,8))
                Label(row, fmt_money(r['collected']), size=12, color=C["green"]).pack(side="right")
                bar_bg = ctk.CTkFrame(rc, fg_color=C["bg2"], height=8, corner_radius=4)
                bar_bg.pack(fill="x", padx=16, pady=(0,4))
                ctk.CTkFrame(bar_bg, fg_color=C["green"], height=8, corner_radius=4).place(relx=0, rely=0, relheight=1, relwidth=max(pct/100, 0.02))
        else:
            MutedLabel(rc, "Chưa có dữ liệu").pack(pady=16)

        # ── 3. CARD VI PHẠM THEO LOẠI ──
        vc = Card(self.scroll)
        vc.grid(row=1, column=1, padx=4, pady=6, sticky="nsew")
        SectionTitle(vc, "⚠️ Vi phạm theo loại").pack(anchor="w", padx=16, pady=(12,4))
        
        if violation_counts:
            max_v = max(cnt for _, cnt in violation_counts) or 1
            for vtype, cnt in violation_counts:
                row = ctk.CTkFrame(vc, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=3)
                Label(row, vtype, size=12).pack(side="left")
                Label(row, str(cnt), size=12, bold=True, color=C["rose"]).pack(side="right")
                bar_bg = ctk.CTkFrame(vc, fg_color=C["bg2"], height=8, corner_radius=4)
                bar_bg.pack(fill="x", padx=16, pady=(0,4))
                ctk.CTkFrame(bar_bg, fg_color=C["rose"], height=8, corner_radius=4).place(relx=0, rely=0, relheight=1, relwidth=max(cnt/max_v, 0.02))
        else:
            MutedLabel(vc, "✅ Không có vi phạm").pack(pady=16)
