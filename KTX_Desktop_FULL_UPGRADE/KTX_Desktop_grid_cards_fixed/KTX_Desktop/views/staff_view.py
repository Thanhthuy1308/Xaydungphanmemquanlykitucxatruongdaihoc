import customtkinter as ctk
from utils.theme import *
from utils.widgets import Table
from views.base_dialog import BaseDialog, ConfirmDialog, _shake
from werkzeug.security import generate_password_hash

class StaffPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, ctrl): self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "👷  Nhân viên & Bảo vệ").pack(side="left", padx=20, pady=16)
        ctk.CTkButton(tb, text="+  Thêm nhân viên", command=self._on_add_click,
                      height=34, width=140, corner_radius=8,
                      fg_color=C["primary"], hover_color=C["accent"],
                      text_color=C["white"], font=ctk.CTkFont(FONT_FAMILY,12,"bold")
                      ).pack(side="right", padx=16, pady=11)
        cols=[("Tên đăng nhập",120),("Họ và tên",155),("Chức vụ",110),
              ("Ca làm",145),("Tòa phụ trách",110),("SĐT",110),("",80)]
        self.table = Table(self, cols, on_select=self._on_row_click, action_col=True, page_size=10)
        self.table.pack(fill="both", expand=True, padx=16, pady=14)

    def _on_add_click(self):
        if self.controller: self.controller.show_add_dialog()

    def _on_row_click(self, idx, row):
        if self.controller: self.controller.confirm_delete(idx)

    def update_table(self, rows):
        self.table.load(rows)

class AddStaffDialogUI(BaseDialog):
    def __init__(self, master, buildings, submit_callback):
        super().__init__(master, "👷  Thêm nhân viên mới", 480, 480)
        self.submit_callback = submit_callback
        self.buildings = buildings
        b_labels = ["— Tất cả tòa —"] + [b['name'] for b in buildings]

        self.field("Tên đăng nhập *", 0, 0); self.uname = Entry(self.body, "nv001")
        self.uname.grid(row=1,column=0,sticky="ew",padx=4,pady=2)
        self.field("Mật khẩu *", 0, 1); self.pwd = Entry(self.body, "")
        self.pwd.configure(show="●")
        self.pwd.grid(row=1,column=1,sticky="ew",padx=4,pady=2)

        self.field("Họ và tên *", 2, 0, 2); self.fullname = Entry(self.body, "Nguyễn Văn B")
        self.fullname.grid(row=3,column=0,columnspan=2,sticky="ew",padx=4,pady=2)

        self.field("SĐT", 4, 0); self.phone = Entry(self.body, "09xxxxxxxx")
        self.phone.grid(row=5,column=0,sticky="ew",padx=4,pady=2)
        self.field("Chức vụ", 4, 1)
        self.pos = Dropdown(self.body, ["Bảo vệ","Quản lý tòa","Kế toán","Tạp vụ"])
        self.pos.grid(row=5,column=1,sticky="ew",padx=4,pady=2)

        self.field("Ca làm việc", 6, 0)
        self.shift = Dropdown(self.body, ["Ca sáng (6h-14h)","Ca chiều (14h-22h)","Ca đêm (22h-6h)","Hành chính"])
        self.shift.grid(row=7,column=0,sticky="ew",padx=4,pady=2)
        self.field("Tòa phụ trách", 6, 1)
        self.bld_var = ctk.StringVar(value=b_labels[0])
        self.bld = Dropdown(self.body, b_labels, variable=self.bld_var)
        self.bld.grid(row=7,column=1,sticky="ew",padx=4,pady=2)

    def _submit(self):
        uname = self.uname.get().strip()
        pwd   = self.pwd.get().strip()
        fname = self.fullname.get().strip()
        if not uname or not pwd or not fname: _shake(self.ok_btn); return
        idx = list(self.bld.cget("values")).index(self.bld_var.get()) - 1
        bid = self.buildings[idx]['id'] if idx >= 0 else None
        self.submit_callback({
            "username": uname, "password": pwd, "fullname": fname,
            "phone": self.phone.get().strip(), "position": self.pos.get(),
            "shift": self.shift.get(), "building_id": bid
        }, self)
