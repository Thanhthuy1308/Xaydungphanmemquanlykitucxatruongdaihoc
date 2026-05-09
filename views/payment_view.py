import customtkinter as ctk
from utils.theme import *
from utils.widgets import Table
from views.base_dialog import BaseDialog, ConfirmDialog, _shake
from datetime import date, datetime

def fmt_money(v):
    try: return f"{float(v):,.0f}đ"
    except: return "0đ"

class PaymentsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, ctrl): self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "💰  Thu tiền phòng").pack(side="left", padx=20, pady=16)
        ctk.CTkButton(tb, text="⚡  Tạo hàng loạt", command=self._on_gen_click,
                      height=34, width=140, corner_radius=8,
                      fg_color=C["card2"], hover_color=C["primary3"],
                      text_color=C["primary"], border_color=C["border"], border_width=1,
                      font=ctk.CTkFont(FONT_FAMILY, 12)
                      ).pack(side="right", padx=4, pady=11)
        ctk.CTkButton(tb, text="✅  Thu hàng loạt", command=self._on_bulk_collect_click,
                      height=34, width=140, corner_radius=8,
                      fg_color=C["green_bg"], hover_color="#A7F3D0",
                      text_color=C["green"], border_color=C["border"], border_width=1,
                      font=ctk.CTkFont(FONT_FAMILY, 12, "bold")
                      ).pack(side="right", padx=4, pady=11)
        ctk.CTkButton(tb, text="+  Tạo phiếu thu", command=self._on_add_click,
                      height=34, width=140, corner_radius=8,
                      fg_color=C["primary"], hover_color=C["accent"],
                      text_color=C["white"],
                      font=ctk.CTkFont(FONT_FAMILY, 12, "bold")
                      ).pack(side="right", padx=(4,8), pady=11)

        self.sum_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.sum_frame.pack(fill="x", padx=16, pady=(8,4))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=16, pady=(0,8))
        self.month_entry = Entry(bar, "YYYY-MM", width=110)
        self.month_entry.insert(0, datetime.now().strftime("%Y-%m"))
        self.month_entry.pack(side="left", padx=(0,6))
        self.month_entry.bind("<Return>", lambda _: self._on_filter())
        GhostBtn(bar, "🔍 Lọc", command=self._on_filter, width=80).pack(side="left", padx=(0,8))
        self.st_var = ctk.StringVar(value="Tất cả")
        Dropdown(bar, ["Tất cả","Chưa thu","Đã thu"],
                 variable=self.st_var, command=lambda _: self._on_filter(),
                 width=120).pack(side="left")
        self.count_lbl = ctk.CTkLabel(bar, text="",
                                       font=ctk.CTkFont(FONT_FAMILY,12),
                                       text_color=C["text3"])
        self.count_lbl.pack(side="left", padx=10)

        cols = [("MSSV",100),("Sinh viên",145),("Phòng",120),("Tháng",80),
                ("Số tiền",110),("Trạng thái",95),("Ngày thu",95),("",110)]
        self.table = Table(self, cols, on_select=self._on_row_click, action_col=True, page_size=10)
        self.table.pack(fill="both", expand=True, padx=16, pady=(0,16))
        self._raw = []

    def _on_filter(self):
        month = self.month_entry.get().strip() or datetime.now().strftime("%Y-%m")
        if self.controller: self.controller.load_data(month, self.st_var.get())

    def _on_add_click(self):
        if self.controller: self.controller.show_add_dialog()

    def _on_gen_click(self):
        if self.controller: self.controller.show_generate_dialog()

    def _on_bulk_collect_click(self):
        month = self.month_entry.get().strip() or datetime.now().strftime("%Y-%m")
        if self.controller: self.controller.bulk_collect(month)

    def _on_row_click(self, idx, row):
        if self.controller: self.controller.toggle_paid(idx)

    def update_ui(self, raw_payments, rows, summ):
        self._raw = raw_payments
        for w in self.sum_frame.winfo_children(): w.destroy()
        for icon,val,lbl,ck in [
            ("✅", fmt_money(summ['collected']), "Đã thu",    "green"),
            ("⏳", fmt_money(summ['pending']),   "Chưa thu",  "amber"),
            ("📋", str(summ['total']),           "Tổng phiếu","blue"),
        ]:
            f = ctk.CTkFrame(self.sum_frame, fg_color=C[ck+"_bg"],
                             corner_radius=10, border_width=1, border_color=C["border"])
            f.pack(side="left", padx=4, ipadx=10, ipady=6)
            ctk.CTkLabel(f, text=f"{icon}  {val}",
                         font=ctk.CTkFont(FONT_FAMILY, 13, "bold"),
                         text_color=C[ck]).pack(side="left", padx=(10,4))
            MutedLabel(f, lbl).pack(side="left", padx=(0,10))
        self.count_lbl.configure(text=f"{len(rows)} phiếu")
        self.table.load(rows)

    def set_month(self, month):
        self.month_entry.delete(0, "end")
        self.month_entry.insert(0, month)

    def set_status(self, status):
        self.st_var.set(status)

    def show_message(self, msg):
        import tkinter.messagebox as mb
        mb.showinfo("Thông báo", msg)

    def get_current_raw(self): return self._raw

class AddPaymentDialogUI(BaseDialog):
    def __init__(self, master, students_data, submit_callback):
        super().__init__(master, "💰  Tạo phiếu thu", 480, 380)
        self.submit_callback = submit_callback
        self.students = students_data
        if not students_data:
            ctk.CTkLabel(self.body, text="⚠️ Chưa có sinh viên đang ở",
                         text_color=C["rose"],
                         font=ctk.CTkFont(FONT_FAMILY,13)).grid(row=0,column=0,columnspan=2,pady=20)
            self.ok_btn.configure(state="disabled")
            return
        labels = [self._student_label(s) for s in students_data]

        self.field("Sinh viên *", 0, 0, 2)
        self.sv_var = ctk.StringVar(value=labels[0])
        self.sv_dd  = Dropdown(self.body, labels, variable=self.sv_var,
                               command=lambda _: self._sync_amount())
        self.sv_dd.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

        self.field("Số tiền (đ) *", 2, 0)
        self.amount = Entry(self.body, "500000")
        self.amount.grid(row=3, column=0, sticky="ew", padx=4, pady=2)  # row=3, không phải 5

        self.field("Tháng (YYYY-MM) *", 2, 1)
        self.month = Entry(self.body, "")           # placeholder trống
        self.month.insert(0, date.today().strftime("%Y-%m"))  # chỉ insert 1 lần
        self.month.grid(row=3, column=1, sticky="ew", padx=4, pady=2)

        self.field("Ghi chú", 4, 0, 2)
        self.note = Entry(self.body, "Tiền phòng tháng...")
        self.note.grid(row=5, column=0, columnspan=2, sticky="ew", padx=4, pady=2)
        self._sync_amount()

    def _student_label(self, s):
        room = f" - {s.get('building_name')} P.{s.get('room_number')}" if s.get('room_number') else ""
        return f"{s['fullname']} ({s['student_id']}){room}"

    def _sync_amount(self):
        if not hasattr(self, "amount"):
            return
        try:
            idx = [self._student_label(s) for s in self.students].index(self.sv_var.get())
            price = self.students[idx].get("price")
        except ValueError:
            return
        if price:
            self.amount.delete(0, "end")
            self.amount.insert(0, str(int(price)))

    def _submit(self):
        try:
            idx = [self._student_label(s) for s in self.students].index(self.sv_var.get())
        except ValueError: _shake(self.ok_btn); return
        month = self.month.get().strip()
        if not month: _shake(self.ok_btn); return
        try: amt = float(self.amount.get().replace(',','').strip())
        except: _shake(self.ok_btn); return
        self.submit_callback(
            {"student_id": self.students[idx]['id'], "amount": amt,
             "month": month, "note": self.note.get().strip()},
            self
        )

class GeneratePaymentDialogUI(BaseDialog):
    def __init__(self, master, submit_callback):
        super().__init__(master, "⚡  Tạo phiếu thu hàng loạt", 460, 340)
        self.submit_callback = submit_callback
        self.ok_btn.configure(text="⚡  Tạo tự động")
        ctk.CTkLabel(self.body,
                     text="Tự động tạo phiếu thu cho tất cả\nsinh viên đang ở theo giá phòng.",
                     font=ctk.CTkFont(FONT_FAMILY,13), text_color=C["text2"],
                     justify="left").grid(row=0,column=0,columnspan=2,padx=4,pady=(0,12),sticky="w")
        self.field("Tháng (YYYY-MM) *", 1, 0, 2)
        self.month = Entry(self.body, "")
        self.month.insert(0, date.today().strftime("%Y-%m"))
        self.month.grid(row=3, column=0, columnspan=2, sticky="ew", padx=4, pady=2)
        self.collect_now = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.body,
            text="Tạo xong thu luôn các phiếu chưa thu của tháng này",
            variable=self.collect_now,
            fg_color=C["primary"],
            hover_color=C["accent"],
            text_color=C["text"],
            font=ctk.CTkFont(FONT_FAMILY, 12)
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=4, pady=(14, 0))

    def _submit(self):
        month = self.month.get().strip()
        if not month: _shake(self.ok_btn); return
        self.submit_callback({"month": month, "collect_now": self.collect_now.get()}, self)
