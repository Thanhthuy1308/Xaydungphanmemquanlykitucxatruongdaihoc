import customtkinter as ctk
from utils.theme import *
from utils.widgets import Table
from views.base_dialog import BaseDialog, _shake

class ApplicationsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, ctrl): self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "📋  Đơn xin ở KTX").pack(side="left", padx=20, pady=16)
        ctk.CTkButton(tb, text="+  Tạo đơn mới", border_width=1, border_color=C["primary"], command=self._on_add_click,
                      height=34, width=130, corner_radius=8,
                      fg_color=C["primary"], hover_color=C["accent"],
                      text_color=C["white"], font=ctk.CTkFont(FONT_FAMILY,12,"bold")
                      ).pack(side="right", padx=16, pady=11)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=16, pady=8)
        self.st_var = ctk.StringVar(value="Đang chờ")
        Dropdown(bar, ["Đang chờ","Đã duyệt","Từ chối","Tất cả"],
                 variable=self.st_var, command=lambda _: self._on_filter(), width=140).pack(side="left")
        self.count_lbl = ctk.CTkLabel(bar, text="", font=ctk.CTkFont(FONT_FAMILY,12), text_color=C["text3"])
        self.count_lbl.pack(side="left", padx=10)

        cols=[("Họ tên",135),("MSSV",100),("Giới tính",75),("Khoa",130),
              ("Loại phòng",100),("Ngày nộp",100),("Trạng thái",110),("",120)]
        self.table = Table(self, cols, on_select=self._on_row_click, action_col=True, page_size=10)
        self.table.pack(fill="both", expand=True, padx=16, pady=(0,16))

    def _on_filter(self):
        if self.controller: self.controller.load_data(self.st_var.get())

    def _on_add_click(self):
        if self.controller: self.controller.show_add_dialog()

    def _on_row_click(self, idx, row):
        if self.controller: self.controller.show_detail(idx)

    def update_table(self, rows):
        self.count_lbl.configure(text=f"{len(rows)} đơn")
        self.table.load(rows)


class ApproveDialog(ctk.CTkToplevel):
    def __init__(self, master, app_data, on_done=None):
        super().__init__(master)
        self.app_data = app_data
        self.on_done  = on_done
        self.title("Xét duyệt đơn xin ở")
        self.geometry("460x430")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.update_idletasks()
        try:
            x = master.winfo_rootx()+(master.winfo_width()-460)//2
            y = master.winfo_rooty()+(master.winfo_height()-430)//2
            self.geometry(f"+{x}+{y}")
        except: pass
        self.after(80, self._init_grab)
        self._build()

    def _init_grab(self):
        try: self.lift(); self.focus_force(); self.grab_set()
        except: pass

    def _close(self):
        try: self.grab_release()
        except: pass
        self.destroy()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=C["primary"], corner_radius=0, height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="📋  Xét duyệt đơn xin ở KTX",
                     font=ctk.CTkFont(FONT_FAMILY,14,"bold"),
                     text_color=C["white"]).pack(side="left", padx=16, pady=13)
        st = self.app_data['status']
        if st != 'pending':
            st_txt = {"approved":"✓ Đã duyệt","rejected":"✕ Đã từ chối"}.get(st,'')
            st_col = {"approved":C["green"],"rejected":C["rose"]}.get(st,C["text3"])
            ctk.CTkLabel(hdr, text=st_txt,
                         font=ctk.CTkFont(FONT_FAMILY,12,"bold"),
                         text_color=st_col).pack(side="right", padx=16)

        info = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=10,
                            border_width=1, border_color=C["border"])
        info.pack(fill="x", padx=14, pady=(14,6))
        ig = ctk.CTkFrame(info, fg_color="transparent")
        ig.pack(fill="x", padx=14, pady=12)
        ig.grid_columnconfigure((0,1), weight=1)
        fields=[("Họ và tên",self.app_data['fullname']),
                ("MSSV",     self.app_data.get('student_id') or '—'),
                ("Giới tính",self.app_data.get('gender') or '—'),
                ("SĐT",      self.app_data.get('phone') or '—'),
                ("Khoa",     self.app_data.get('faculty') or '—'),
                ("Loại phòng",self.app_data.get('preferred_room_type','standard'))]
        for i,(k,v) in enumerate(fields):
            r,c=(i//2)*2, i%2
            ctk.CTkLabel(ig,text=k,font=ctk.CTkFont(FONT_FAMILY,10,"bold"),
                         text_color=C["text3"]).grid(row=r,column=c,sticky="w",padx=8,pady=(4,0))
            ctk.CTkLabel(ig,text=str(v),font=ctk.CTkFont(FONT_FAMILY,13),
                         text_color=C["text"]).grid(row=r+1,column=c,sticky="w",padx=8,pady=(0,4))
        reason=(self.app_data.get('reason') or '').strip()
        if reason:
            ctk.CTkLabel(info,text="Lý do:",font=ctk.CTkFont(FONT_FAMILY,11,"bold"),
                         text_color=C["text3"]).pack(anchor="w",padx=14)
            ctk.CTkLabel(info,text=reason[:130],font=ctk.CTkFont(FONT_FAMILY,12),
                         text_color=C["text2"],wraplength=400,justify="left"
                         ).pack(anchor="w",padx=14,pady=(0,10))

        nf = ctk.CTkFrame(self, fg_color="transparent")
        nf.pack(fill="x", padx=14, pady=(4,0))
        ctk.CTkLabel(nf,text="Ghi chú phản hồi:",font=ctk.CTkFont(FONT_FAMILY,11,"bold"),
                     text_color=C["text2"]).pack(anchor="w",pady=(0,4))
        self.note_entry = ctk.CTkEntry(nf, placeholder_text="Nhập ghi chú...",
                                        fg_color=C["white"], border_color=C["border"],
                                        text_color=C["text"], corner_radius=8, height=36,
                                        font=ctk.CTkFont(FONT_FAMILY,13))
        self.note_entry.pack(fill="x")
        if self.app_data.get('note'):
            self.note_entry.insert(0, self.app_data['note'])

        foot = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0, height=58)
        foot.pack(fill="x", side="bottom"); foot.pack_propagate(False)
        ctk.CTkButton(foot, text="✕  Đóng", width=90, height=34,
                      fg_color=C["card2"], hover_color=C["primary3"],
                      text_color=C["text2"], corner_radius=8,
                      font=ctk.CTkFont(FONT_FAMILY,13),
                      command=self._close).pack(side="left", padx=14, pady=12)
        if self.app_data['status'] == 'pending':
            ctk.CTkButton(foot, text="✕  Từ chối", width=115, height=34,
                          fg_color=C["rose_bg"], hover_color="#FECACA",
                          text_color=C["rose"], corner_radius=8,
                          font=ctk.CTkFont(FONT_FAMILY,13,"bold"),
                          command=self._reject).pack(side="right", padx=6, pady=12)
            ctk.CTkButton(foot, text="✓  Duyệt đơn", width=125, height=34,
                          fg_color=C["green"], hover_color="#257A54",
                          text_color=C["white"], corner_radius=8,
                          font=ctk.CTkFont(FONT_FAMILY,13,"bold"),
                          command=self._approve).pack(side="right", padx=6, pady=12)

    def _approve(self):
        from models import database as db
        db.update_application_status(self.app_data['id'], "approved", self.note_entry.get().strip())
        self._close()
        if self.on_done: self.on_done()

    def _reject(self):
        from models import database as db
        db.update_application_status(self.app_data['id'], "rejected", self.note_entry.get().strip())
        self._close()
        if self.on_done: self.on_done()


class AddApplicationDialogUI(BaseDialog):
    def __init__(self, master, submit_callback):
        super().__init__(master, "📋  Đơn xin ở KTX", 500, 530)
        self.submit_callback = submit_callback

        self.field("Họ và tên *", 0, 0); self.name = Entry(self.body, "Nguyễn Văn A")
        self.name.grid(row=1,column=0,sticky="ew",padx=4,pady=2)
        self.field("MSSV", 0, 1); self.sid = Entry(self.body, "SV2024xxxx")
        self.sid.grid(row=1,column=1,sticky="ew",padx=4,pady=2)

        self.field("Giới tính", 2, 0)
        self.gender = Dropdown(self.body, ["Nam","Nữ","Khác"])
        self.gender.grid(row=3,column=0,sticky="ew",padx=4,pady=2)
        self.field("SĐT", 2, 1); self.phone = Entry(self.body,"09xxxxxxxx")
        self.phone.grid(row=3,column=1,sticky="ew",padx=4,pady=2)

        self.field("Email", 4, 0); self.email = Entry(self.body,"sv@email.com")
        self.email.grid(row=5,column=0,sticky="ew",padx=4,pady=2)
        self.field("Khoa", 4, 1); self.faculty = Entry(self.body,"Công nghệ thông tin")
        self.faculty.grid(row=5,column=1,sticky="ew",padx=4,pady=2)

        self.field("Loại phòng mong muốn", 6, 0, 2)
        self.pref = Dropdown(self.body, ["standard","vip"])
        self.pref.grid(row=7,column=0,columnspan=2,sticky="ew",padx=4,pady=2)

        self.field("Lý do xin ở KTX", 8, 0, 2)
        self.reason = TextBox(self.body, height=80)
        self.reason.grid(row=9,column=0,columnspan=2,sticky="ew",padx=4,pady=2)

    def _submit(self):
        name = self.name.get().strip()
        if not name: _shake(self.ok_btn); return
        self.submit_callback({
            "fullname": name, "student_id": self.sid.get().strip(),
            "gender": self.gender.get(), "phone": self.phone.get().strip(),
            "email": self.email.get().strip(), "faculty": self.faculty.get().strip(),
            "reason": self.reason.get("1.0","end").strip(), "preferred": self.pref.get()
        }, self)
