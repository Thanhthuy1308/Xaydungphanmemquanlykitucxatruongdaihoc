from datetime import date

import customtkinter as ctk

from utils.theme import *
from utils.widgets import Table
from views.base_dialog import BaseDialog, _shake


def fmt_money(v):
    try:
        return f"{float(v):,.0f}đ"
    except (TypeError, ValueError):
        return "0đ"


class InvoicesPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._raw = []
        self._build()

    def set_controller(self, ctrl):
        self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "🧾  Hóa đơn").pack(side="left", padx=20, pady=16)
        ctk.CTkButton(tb, text="+  Tạo hóa đơn", command=self._on_add_click,
                      height=34, width=140, corner_radius=8,
                      fg_color=C["primary"], hover_color=C["accent"],
                      text_color=C["white"], font=ctk.CTkFont(FONT_FAMILY,12,"bold")
                      ).pack(side="right", padx=16, pady=11)

        self.sum_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sum_frame.pack(fill="x", padx=16, pady=(8,4))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=16, pady=(0,8))
        self.month_entry = Entry(bar, "YYYY-MM", width=110)
        self.month_entry.insert(0, date.today().strftime("%Y-%m"))
        self.month_entry.pack(side="left", padx=(0,6))
        self.month_entry.bind("<Return>", lambda _: self._on_filter())
        GhostBtn(bar, "🔍 Lọc", command=self._on_filter, width=80).pack(side="left", padx=(0,8))
        self.st_var = ctk.StringVar(value="Tất cả")
        Dropdown(bar, ["Tất cả","Chưa thanh toán","Đã thanh toán"],
                 variable=self.st_var, command=lambda _: self._on_filter(),
                 width=150).pack(side="left", padx=(0,8))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_filter())
        Entry(bar, "Tìm tên / MSSV", textvariable=self.search_var, width=180).pack(side="left")
        self.count_lbl = ctk.CTkLabel(bar, text="",
                                      font=ctk.CTkFont(FONT_FAMILY,12),
                                      text_color=C["text3"])
        self.count_lbl.pack(side="left", padx=10)

        cols = [("MSSV",90),("Sinh viên",135),("Phòng",110),("Ngày",85),
                ("Tiền phòng",100),("Phí khác",95),("Tổng",105),
                ("Trạng thái",100),("",90)]
        self.table = Table(self, cols, on_select=self._on_row_click, action_col=True, page_size=10)
        self.table.pack(fill="both", expand=True, padx=16, pady=(0,16))

    def _on_add_click(self):
        if self.controller:
            self.controller.show_add_dialog()

    def _on_filter(self):
        month = self.month_entry.get().strip() or date.today().strftime("%Y-%m")
        if self.controller:
            self.controller.load_data(month, self.st_var.get(), self.search_var.get().strip())

    def _on_row_click(self, idx, row):
        if self.controller:
            self.controller.toggle_paid(idx)

    def update_ui(self, raw_invoices, rows, summary):
        self._raw = raw_invoices
        for w in self.sum_frame.winfo_children():
            w.destroy()
        cards = [
            ("💰", fmt_money(summary["total_revenue"]), "Doanh thu đã thu", "green"),
            ("⏳", fmt_money(summary["unpaid_amount"]), "Chưa thu", "amber"),
            ("🧾", str(summary["paid_invoices"] or 0), "Hóa đơn đã thu", "blue"),
            ("📌", str(summary["unpaid_invoices"] or 0), "Hóa đơn chưa thu", "rose"),
        ]
        for icon, value, label, ck in cards:
            f = ctk.CTkFrame(self.sum_frame, fg_color=C[ck+"_bg"],
                             corner_radius=10, border_width=1, border_color=C["border"])
            f.pack(side="left", padx=4, ipadx=10, ipady=6)
            ctk.CTkLabel(f, text=f"{icon}  {value}",
                         font=ctk.CTkFont(FONT_FAMILY, 13, "bold"),
                         text_color=C[ck]).pack(side="left", padx=(10,4))
            MutedLabel(f, label).pack(side="left", padx=(0,10))
        self.count_lbl.configure(text=f"{len(rows)} hóa đơn")
        self.table.load(rows)

    def set_month(self, month):
        self.month_entry.delete(0, "end")
        self.month_entry.insert(0, month)

    def set_status(self, status):
        self.st_var.set(status)


class AddInvoiceDialogUI(BaseDialog):
    def __init__(self, master, students_data, submit_callback):
        super().__init__(master, "🧾  Tạo hóa đơn", 540, 600)
        self.submit_callback = submit_callback
        self.students = students_data
        if not students_data:
            ctk.CTkLabel(self.body, text="Chưa có sinh viên đang ở",
                         text_color=C["rose"],
                         font=ctk.CTkFont(FONT_FAMILY,13)).grid(row=0,column=0,columnspan=2,pady=20)
            self.ok_btn.configure(state="disabled")
            return

        labels = [self._student_label(s) for s in students_data]
        self.field("Sinh viên *", 0, 0, 2)
        self.sv_var = ctk.StringVar(value=labels[0])
        self.sv_dd = Dropdown(self.body, labels, variable=self.sv_var,
                              command=lambda _: self._sync_defaults())
        self.sv_dd.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

        self.field("Tiền phòng", 2, 0)
        self.room_fee = Entry(self.body, "0")
        self.room_fee.grid(row=5, column=0, sticky="ew", padx=4, pady=2)
        self.field("Tiền điện", 2, 1)
        self.electric_fee = Entry(self.body, "0")
        self.electric_fee.grid(row=5, column=1, sticky="ew", padx=4, pady=2)

        self.field("Tiền nước", 3, 0)
        self.water_fee = Entry(self.body, "0")
        self.water_fee.grid(row=7, column=0, sticky="ew", padx=4, pady=2)
        self.field("Phí vi phạm", 3, 1)
        self.violation_fee = Entry(self.body, "0")
        self.violation_fee.grid(row=7, column=1, sticky="ew", padx=4, pady=2)

        self.field("Ngày tạo", 4, 0)
        self.created_date = Entry(self.body, "YYYY-MM-DD")
        self.created_date.insert(0, date.today().isoformat())
        self.created_date.grid(row=9, column=0, sticky="ew", padx=4, pady=2)

        self.field("Trạng thái", 4, 1)
        self.status = Dropdown(self.body, ["unpaid","paid"])
        self.status.grid(row=9, column=1, sticky="ew", padx=4, pady=2)

        self.field("Ghi chú", 5, 0, 2)
        self.note = Entry(self.body, "Hóa đơn tháng...")
        self.note.grid(row=11, column=0, columnspan=2, sticky="ew", padx=4, pady=2)
        self._sync_defaults()

    def _student_label(self, s):
        room = f" - {s.get('building_name')} P.{s.get('room_number')}" if s.get("room_number") else ""
        return f"{s['fullname']} ({s['student_id']}){room}"

    def _current_student(self):
        labels = [self._student_label(s) for s in self.students]
        try:
            return self.students[labels.index(self.sv_var.get())]
        except ValueError:
            return None

    def _sync_defaults(self):
        student = self._current_student()
        if not student:
            return
        self.room_fee.delete(0, "end")
        self.room_fee.insert(0, str(int(student.get("price") or 0)))
        self.violation_fee.delete(0, "end")
        self.violation_fee.insert(0, str(int(student.get("open_violation_fines") or 0)))

    def _money(self, entry):
        try:
            return float(entry.get().replace(",", "").strip() or 0)
        except ValueError:
            _shake(self.ok_btn)
            return None

    def _submit(self):
        student = self._current_student()
        if not student:
            _shake(self.ok_btn)
            return
        amounts = [self._money(e) for e in [self.room_fee, self.electric_fee, self.water_fee, self.violation_fee]]
        if any(v is None for v in amounts):
            return
        created = self.created_date.get().strip()
        if not created:
            _shake(self.ok_btn)
            return
        self.submit_callback({
            "student_id": student["id"],
            "room_fee": amounts[0],
            "electric_fee": amounts[1],
            "water_fee": amounts[2],
            "violation_fee": amounts[3],
            "payment_status": self.status.get(),
            "created_date": created,
            "note": self.note.get().strip(),
        }, self)
