import customtkinter as ctk
from utils.theme import *
from utils.widgets import Table
from views.base_dialog import BaseDialog, _shake

class ViolationsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, controller):
        self.controller = controller

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=72, corner_radius=0,
                          border_width=1, border_color=C["border"])
        tb.pack(fill="x"); tb.pack_propagate(False)
        title_box = ctk.CTkFrame(tb, fg_color="transparent")
        title_box.pack(side="left", padx=22, pady=13)
        SectionTitle(title_box, "Vi phạm nội quy").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Theo dõi, ghi nhận và xử lý vi phạm",
                     font=ctk.CTkFont(FONT_FAMILY, 11),
                     text_color=C["text3"]).pack(anchor="w", pady=(2, 0))
        PrimaryBtn(tb, "+  Ghi vi phạm", command=self._on_add_click, width=132).pack(side="right", padx=18, pady=18)

        bar = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=8,
                           border_width=1, border_color=C["border"], height=56)
        bar.pack(fill="x", padx=16, pady=12)
        bar.pack_propagate(False)
        self.st_var = ctk.StringVar(value="Chưa xử lý")
        Dropdown(bar, ["Chưa xử lý","Đã xử lý","Tất cả"], variable=self.st_var, command=lambda _: self._on_filter(), width=140).pack(side="left", padx=(12, 8), pady=10)
        self.count_lbl = ctk.CTkLabel(bar, text="", font=ctk.CTkFont(FONT_FAMILY,12), text_color=C["text3"])
        self.count_lbl.pack(side="left", padx=10)

        cols = [("Sinh viên",140),("Loại",130),("Mức độ",100),("Tiền phạt",100),("Người ghi",120),("Ngày",100),("Trạng thái",100),("",90)]
        self.table = Table(self, cols, on_select=self._on_row_click, action_col=True, page_size=10)
        self.table.pack(fill="both", expand=True, padx=16, pady=(0,16))

    def _on_filter(self):
        if self.controller: self.controller.load_data(self.st_var.get())

    def _on_add_click(self):
        if self.controller: self.controller.show_add_dialog()

    def _on_row_click(self, idx, row):
        if self.controller: self.controller.resolve(idx)

    def update_table(self, rows):
        self.count_lbl.configure(text=f"{len(rows)} vi phạm")
        self.table.load(rows)

class AddViolationDialogUI(BaseDialog):
    def __init__(self, master, students_data, submit_callback):
        super().__init__(master, "⚠️  Ghi nhận vi phạm", 500, 520)
        self.submit_callback = submit_callback
        self.students = students_data
        student_labels = [f"{s['fullname']} ({s['student_id']})" for s in self.students] if self.students else ["— Chưa có sinh viên —"]

        self.field("Sinh viên *", 0, 0, 2)
        self.sv_var = ctk.StringVar(value=student_labels[0])
        self.sv_dd = Dropdown(self.body, student_labels, variable=self.sv_var)
        self.sv_dd.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

        self.field("Loại vi phạm *", 2, 0)
        self.vtype = Dropdown(self.body, ["Ồn ào quá giờ","Hút thuốc","Uống rượu bia","Khách trái phép","Vi phạm giờ giới nghiêm","Phá hoại tài sản","Không đóng tiền","Khác"])
        self.vtype.grid(row=5, column=0, sticky="ew", padx=4, pady=2)

        self.field("Mức độ", 2, 1)
        self.severity = Dropdown(self.body, ["Nhẹ","Trung bình","Nghiêm trọng"])
        self.severity.grid(row=5, column=1, sticky="ew", padx=4, pady=2)

        self.field("Tiền phạt (đ)", 4, 0, 2); self.fine = Entry(self.body, "0")
        self.fine.grid(row=9, column=0, columnspan=2, sticky="ew", padx=4, pady=2)
        self.field("Mô tả chi tiết", 6, 0, 2); self.desc = TextBox(self.body, height=100)
        self.desc.grid(row=13, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

    def _submit(self):
        idx = list(self.sv_dd.cget("values")).index(self.sv_var.get())
        if idx >= len(self.students): _shake(self.ok_btn); return
        sv_map = {"Nhẹ":"minor","Trung bình":"medium","Nghiêm trọng":"severe"}
        try: fine = float(self.fine.get().replace(',','') or 0)
        except: fine = 0
        data = {"student_id": self.students[idx]["id"], "vtype": self.vtype.get(), "desc": self.desc.get("1.0","end").strip(), "severity": sv_map[self.severity.get()], "fine": fine}
        self.submit_callback(data, self)
