from datetime import date

import customtkinter as ctk

from utils.theme import *
from utils.widgets import Table
from views.invoice_view import fmt_money


class RevenueReportPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, ctrl):
        self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "📈  Báo cáo doanh thu tháng").pack(side="left", padx=20, pady=16)

        bar = ctk.CTkFrame(tb, fg_color="transparent")
        bar.pack(side="right", padx=16, pady=10)
        self.month_entry = Entry(bar, "YYYY-MM", width=120)
        self.month_entry.insert(0, date.today().strftime("%Y-%m"))
        self.month_entry.pack(side="left", padx=(0,8))
        self.month_entry.bind("<Return>", lambda _: self._on_filter())
        GhostBtn(bar, "Lọc", command=self._on_filter, width=72).pack(side="left")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        self.scroll.pack(fill="both", expand=True, padx=16, pady=16)
        self.scroll.grid_columnconfigure((0,1), weight=1)

    def _on_filter(self):
        if self.controller:
            self.controller.load_data(self.month_entry.get().strip() or date.today().strftime("%Y-%m"))

    def update_ui(self, month, summary, by_building, invoice_rows):
        self.month_entry.delete(0, "end")
        self.month_entry.insert(0, month)
        for w in self.scroll.winfo_children():
            w.destroy()

        top = ctk.CTkFrame(self.scroll, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        for col in range(4):
            top.grid_columnconfigure(col, weight=1)
        stat_card(top, "💰", fmt_money(summary["total_revenue"]), "Tổng doanh thu đã thu", "green", 0, 0)
        stat_card(top, "🧾", summary["paid_invoices"] or 0, "Hóa đơn đã thu", "blue", 0, 1)
        stat_card(top, "⏳", summary["unpaid_invoices"] or 0, "Hóa đơn chưa thu", "amber", 0, 2)
        stat_card(top, "📌", fmt_money(summary["unpaid_amount"]), "Số tiền chưa thu", "rose", 0, 3)

        bc = Card(self.scroll)
        bc.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=8)
        SectionTitle(bc, "Doanh thu theo tòa nhà").pack(anchor="w", padx=16, pady=(12,6))
        if by_building:
            max_revenue = max(float(r["revenue"] or 0) for r in by_building) or 1
            for row in by_building:
                pct = float(row["revenue"] or 0) / max_revenue
                line = ctk.CTkFrame(bc, fg_color="transparent")
                line.pack(fill="x", padx=16, pady=(4,0))
                Label(line, row["building_name"], size=13, bold=True).pack(side="left")
                MutedLabel(line, f"{row['paid_invoices'] or 0} đã thu / {row['unpaid_invoices'] or 0} chưa thu").pack(side="left", padx=10)
                Label(line, fmt_money(row["revenue"]), size=13, bold=True, color=C["green"]).pack(side="right")
                bar_bg = ctk.CTkFrame(bc, fg_color=C["bg2"], height=10, corner_radius=5)
                bar_bg.pack(fill="x", padx=16, pady=(2,6))
                ctk.CTkFrame(bar_bg, fg_color=C["green"], height=10, corner_radius=5).place(
                    relx=0, rely=0, relheight=1, relwidth=max(pct, 0.02)
                )
        else:
            MutedLabel(bc, "Chưa có hóa đơn trong tháng này").pack(padx=16, pady=(0,16), anchor="w")

        ic = Card(self.scroll)
        ic.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=4, pady=8)
        SectionTitle(ic, "Hóa đơn trong tháng").pack(anchor="w", padx=16, pady=(12,6))
        Table(ic, [("MSSV",100),("Sinh viên",180),("Tòa nhà",110),("Tổng tiền",120),("Trạng thái",130)],
              rows=invoice_rows, page_size=10).pack(fill="both", expand=True, padx=12, pady=(0,12))
