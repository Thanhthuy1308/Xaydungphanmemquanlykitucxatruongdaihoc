import customtkinter as ctk
from utils.theme import *
from utils.widgets import Table
from views.base_dialog import BaseDialog, ConfirmDialog, _shake
from datetime import date

def fmt_money(v):
    try: return f"{float(v):,.0f}đ"
    except (TypeError, ValueError): return "0đ"

class StudentsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, ctrl): self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "🎓  Danh sách sinh viên").pack(side="left", padx=20, pady=16)
        ctk.CTkButton(tb, text="+  Thêm sinh viên", command=self._on_add_click,
                      height=34, width=140, corner_radius=8,
                      fg_color=C["primary"], hover_color=C["accent"],
                      text_color=C["white"], font=ctk.CTkFont(FONT_FAMILY,12,"bold")
                      ).pack(side="right", padx=16, pady=11)

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=16, pady=8)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_filter_change)
        Entry(bar, "🔍 Tìm tên, MSSV, khoa...",
              textvariable=self.search_var).pack(side="left", padx=(0,8))
        self.status_var = ctk.StringVar(value="Đang ở")
        Dropdown(bar, ["Đang ở","Đã trả phòng"],
                 variable=self.status_var,
                 command=self._on_filter_change, width=140).pack(side="left")
        self.count_lbl = ctk.CTkLabel(bar, text="",
                                       font=ctk.CTkFont(FONT_FAMILY,12),
                                       text_color=C["text3"])
        self.count_lbl.pack(side="left", padx=10)

        cols = [("MSSV",105),("Họ và tên",155),("Khoa",135),
                ("Phòng",130),("SĐT",110),("Ngày vào",95),("",96)]
        self.table = Table(self, cols, on_select=self._on_row_click, action_col=True, page_size=10)
        self.table.pack(fill="both", expand=True, padx=16, pady=(0,16))

    def _on_add_click(self):
        if self.controller: self.controller.show_add_dialog()

    def _on_filter_change(self, *args):
        if self.controller:
            self.controller.load_data(self.search_var.get(), self.status_var.get())

    def _on_row_click(self, idx, row):
        if self.controller: self.controller.show_detail(idx)

    def update_table(self, rows):
        self.count_lbl.configure(text=f"{len(rows)} sinh viên")
        self.table.load(rows)


class StudentDetailDialog(ctk.CTkToplevel):
    def __init__(self, master, student_id, on_done=None):
        super().__init__(master)
        self.student_id = student_id
        self.on_done    = on_done
        self.title("Chi tiết sinh viên")
        self.geometry("720x580")
        self.configure(fg_color=C["bg"])
        self.update_idletasks()
        try:
            x = master.winfo_rootx()+(master.winfo_width()-720)//2
            y = master.winfo_rooty()+(master.winfo_height()-580)//2
            self.geometry(f"+{x}+{y}")
        except Exception: pass
        self.after(70, self._init_grab)
        self._build()

    def _init_grab(self):
        try: self.lift(); self.focus_force(); self.grab_set()
        except Exception: pass

    def _close(self):
        try: self.grab_release()
        except Exception: pass
        self.destroy()
        if self.on_done: self.on_done()

    def _build(self):
        for w in self.winfo_children(): w.destroy()
        from models import database as db
        student = db.get_student_detail(self.student_id)
        if not student:
            ctk.CTkLabel(self, text="Không tìm thấy sinh viên").pack(pady=40)
            return
        self._student = student

        hdr = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0, height=58)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=student['fullname'],
                     font=ctk.CTkFont(FONT_FAMILY,16,"bold"),
                     text_color=C["text"]).pack(side="left", padx=20, pady=17)
        ctk.CTkButton(hdr, text="✕  Đóng", width=80, height=32,
                      fg_color=C["card2"], hover_color=C["primary3"],
                      text_color=C["text2"], corner_radius=8,
                      command=self._close).pack(side="right", padx=8, pady=13)
        if student['status'] == 'active':
            ctk.CTkButton(hdr, text="🚪 Trả phòng", width=110, height=32,
                          fg_color=C["rose_bg"], hover_color="#FECACA",
                          text_color=C["rose"], corner_radius=8,
                          font=ctk.CTkFont(FONT_FAMILY,12,"bold"),
                          command=self._checkout).pack(side="right", padx=4, pady=13)
            ctk.CTkButton(hdr, text="✏ Sửa", width=70, height=32,
                          fg_color=C["blue_bg"], hover_color="#DBEAFE",
                          text_color=C["blue"], corner_radius=8,
                          font=ctk.CTkFont(FONT_FAMILY,12,"bold"),
                          command=self._edit).pack(side="right", padx=4, pady=13)

        body = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.grid_columnconfigure((0,1), weight=1)

        # Info card
        ic = ctk.CTkFrame(body, fg_color=C["card"], corner_radius=10,
                          border_width=1, border_color=C["border"])
        ic.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        ig = ctk.CTkFrame(ic, fg_color="transparent")
        ig.pack(fill="x", padx=14, pady=12)
        for i in range(4): ig.grid_columnconfigure(i, weight=1)
        infos = [("MSSV",student['student_id']),("Giới tính",student.get('gender','—')),
                 ("Khoa",student.get('faculty','—')),("Lớp",student.get('class','—')),
                 ("SĐT",student.get('phone','—')),("Email",student.get('email','—')),
                 ("Phòng",f"{student.get('building_name','?')} P.{student.get('room_number','?')}" if student.get('room_number') else "Chưa phân"),
                 ("Ngày vào",student.get('checkin_date','—'))]
        for i,(k,v) in enumerate(infos):
            ctk.CTkLabel(ig,text=k,font=ctk.CTkFont(FONT_FAMILY,10,"bold"),
                         text_color=C["text3"]).grid(row=(i//4)*2,column=i%4,sticky="w",padx=6,pady=(6,0))
            ctk.CTkLabel(ig,text=str(v),font=ctk.CTkFont(FONT_FAMILY,13),
                         text_color=C["text"]).grid(row=(i//4)*2+1,column=i%4,sticky="w",padx=6,pady=(0,6))

        # Payments
        pc = ctk.CTkFrame(body,fg_color=C["card"],corner_radius=10,border_width=1,border_color=C["border"])
        pc.grid(row=1,column=0,sticky="nsew",padx=4,pady=4)
        ctk.CTkLabel(pc,text="💰  Lịch sử thanh toán",font=ctk.CTkFont(FONT_FAMILY,13,"bold"),
                     text_color=C["text"]).pack(anchor="w",padx=12,pady=(10,6))
        from models import database as db
        self._pays = [p for p in db.get_payments() if p['student_id']==student['id']]
        if self._pays:
            Table(pc,[("Tháng",78),("Số tiền",105),("Trạng thái",95),("Ngày thu",95),("",65)],
                  rows=[[p['month'],fmt_money(p['amount']),
                         "✓ Đã thu" if p['status']=='paid' else "⏳ Chờ",
                         p.get('paid_date','—'),
                         "Thu" if p['status']=='pending' else "↩"] for p in self._pays],
                  on_select=lambda i,r: self._toggle_payment(i)
                  ).pack(fill="both",expand=True,padx=6,pady=(0,8))
        else:
            ctk.CTkLabel(pc,text="Chưa có phiếu thu",font=ctk.CTkFont(FONT_FAMILY,12),
                         text_color=C["text3"]).pack(pady=16)

        # Violations
        vc = ctk.CTkFrame(body,fg_color=C["card"],corner_radius=10,border_width=1,border_color=C["border"])
        vc.grid(row=1,column=1,sticky="nsew",padx=4,pady=4)
        ctk.CTkLabel(vc,text="⚠️  Vi phạm nội quy",font=ctk.CTkFont(FONT_FAMILY,13,"bold"),
                     text_color=C["text"]).pack(anchor="w",padx=12,pady=(10,6))
        viols = [v for v in db.get_violations() if v['student_id']==student['id']]
        sev={"minor":"Nhẹ","medium":"Trung bình","severe":"Nghiêm trọng"}
        if viols:
            Table(vc,[("Loại",110),("Mức độ",95),("Phạt",85),("Ngày",90)],
                  rows=[[v['type'],sev.get(v['severity'],'?'),
                         fmt_money(v['fine']),v['reported_at'][:10]] for v in viols]
                  ).pack(fill="both",expand=True,padx=6,pady=(0,8))
        else:
            ctk.CTkLabel(vc,text="✅  Không có vi phạm",font=ctk.CTkFont(FONT_FAMILY,12),
                         text_color=C["green"]).pack(pady=16)

    def _toggle_payment(self, idx):
        if idx >= len(self._pays): return
        p = self._pays[idx]
        from models import database as db
        if p['status']=='pending':
            ConfirmDialog(self,
                message=f"Thu tiền tháng {p['month']}?\nSố tiền: {fmt_money(p['amount'])}",
                on_confirm=lambda:(db.mark_paid(p['id']), self._rebuild()),
                confirm_text="💰  Thu tiền")
        else:
            ConfirmDialog(self,
                message=f"Hủy xác nhận đã thu tháng {p['month']}?",
                on_confirm=lambda:(db.unmark_paid(p['id']), self._rebuild()),
                confirm_text="↩  Hủy thu", danger=True)

    def _checkout(self):
        ConfirmDialog(self,
            message=f"Xác nhận trả phòng cho:\n{self._student['fullname']}?",
            on_confirm=self._do_checkout,
            confirm_text="🚪  Trả phòng", danger=True)

    def _do_checkout(self):
        from models import database as db
        db.checkout_student(self._student['id'])
        self._close()

    def _edit(self):
        from views.base_dialog import BaseDialog, _shake
        EditStudentDialog(self, self._student, on_done=self._rebuild)

    def _rebuild(self):
        self.after(20, self._build)


class EditStudentDialog(BaseDialog):
    def __init__(self, master, student, on_done=None):
        super().__init__(master, "✏  Sửa thông tin sinh viên", 500, 480)
        self.student = student
        self.on_done = on_done
        self.ok_btn.configure(text="✓  Lưu thay đổi")

        from models import database as db
        rooms = db.get_available_rooms()
        self.rooms = rooms
        room_labels = ["— Giữ nguyên phòng hiện tại —"] + [
            f"{r['building_name']} – P.{r['room_number']} (còn {r['free_slots']} chỗ)"
            for r in rooms]

        self.field("Họ và tên *", 0, 0, 2)
        self.name = Entry(self.body, "")
        self.name.insert(0, student.get('fullname',''))
        self.name.grid(row=1,column=0,columnspan=2,sticky="ew",padx=4,pady=2)

        self.field("Số điện thoại", 2, 0)
        self.phone = Entry(self.body,"")
        self.phone.insert(0, student.get('phone',''))
        self.phone.grid(row=3,column=0,sticky="ew",padx=4,pady=2)

        self.field("Email", 2, 1)
        self.email = Entry(self.body,"")
        self.email.insert(0, student.get('email',''))
        self.email.grid(row=3,column=1,sticky="ew",padx=4,pady=2)

        self.field("Khoa", 4, 0)
        self.faculty = Entry(self.body,"")
        self.faculty.insert(0, student.get('faculty',''))
        self.faculty.grid(row=5,column=0,sticky="ew",padx=4,pady=2)

        self.field("Lớp", 4, 1)
        self.cls = Entry(self.body,"")
        self.cls.insert(0, student.get('class',''))
        self.cls.grid(row=5,column=1,sticky="ew",padx=4,pady=2)

        self.field("Đổi phòng (tùy chọn)", 6, 0, 2)
        self.room_var = ctk.StringVar(value=room_labels[0])
        self.room_dd  = Dropdown(self.body, room_labels, variable=self.room_var)
        self.room_dd.grid(row=7,column=0,columnspan=2,sticky="ew",padx=4,pady=2)

    def _submit(self):
        name = self.name.get().strip()
        if not name: _shake(self.ok_btn); return
        room_idx = list(self.room_dd.cget("values")).index(self.room_var.get()) - 1
        new_room  = self.rooms[room_idx]['id'] if room_idx >= 0 else None
        from models import database as db
        db.update_student(self.student['id'], name,
                          self.phone.get().strip(), self.email.get().strip(),
                          self.faculty.get().strip(), self.cls.get().strip(),
                          new_room)
        self._close()
        if self.on_done: self.on_done()


class AddStudentDialogUI(BaseDialog):
    def __init__(self, master, rooms_data, submit_callback):
        super().__init__(master, "🎓  Thêm sinh viên mới", 520, 560)
        self.submit_callback = submit_callback
        self.rooms_data = rooms_data
        room_labels = ["— Chưa phân phòng —"] + [
            f"{r['building_name']} – P.{r['room_number']} (còn {r['free_slots']} chỗ)"
            for r in rooms_data]

        self.field("Mã số sinh viên *", 0, 0); self.sid = Entry(self.body, "SV20240001")
        self.sid.grid(row=1,column=0,sticky="ew",padx=4,pady=2)
        self.field("Họ và tên *", 0, 1); self.name = Entry(self.body, "Nguyễn Văn A")
        self.name.grid(row=1,column=1,sticky="ew",padx=4,pady=2)

        self.field("Giới tính", 2, 0); self.gender = Dropdown(self.body, ["Nam","Nữ","Khác"])
        self.gender.grid(row=3,column=0,sticky="ew",padx=4,pady=2)
        self.field("Ngày sinh", 2, 1); self.dob = Entry(self.body, "YYYY-MM-DD")
        self.dob.grid(row=3,column=1,sticky="ew",padx=4,pady=2)

        self.field("Số điện thoại", 4, 0); self.phone = Entry(self.body, "09xxxxxxxx")
        self.phone.grid(row=5,column=0,sticky="ew",padx=4,pady=2)
        self.field("Email", 4, 1); self.email = Entry(self.body, "sv@email.com")
        self.email.grid(row=5,column=1,sticky="ew",padx=4,pady=2)

        self.field("Khoa", 6, 0); self.faculty = Entry(self.body, "Công nghệ thông tin")
        self.faculty.grid(row=7,column=0,sticky="ew",padx=4,pady=2)
        self.field("Lớp", 6, 1); self.cls = Entry(self.body, "CNTT2024A")
        self.cls.grid(row=7,column=1,sticky="ew",padx=4,pady=2)

        self.field("Phân phòng", 8, 0, 2)
        self.room_var = ctk.StringVar(value=room_labels[0])
        self.room_dd  = Dropdown(self.body, room_labels, variable=self.room_var)
        self.room_dd.grid(row=9,column=0,columnspan=2,sticky="ew",padx=4,pady=2)

        self.field("Ngày vào ở", 10, 0)
        self.checkin = Entry(self.body, "")
        self.checkin.insert(0, date.today().isoformat())
        self.checkin.grid(row=11,column=0,columnspan=2,sticky="ew",padx=4,pady=2)

    def _submit(self):
        sid  = self.sid.get().strip()
        name = self.name.get().strip()
        if not sid or not name: _shake(self.ok_btn); return
        room_idx = list(self.room_dd.cget("values")).index(self.room_var.get()) - 1
        room_id  = self.rooms_data[room_idx]['id'] if room_idx >= 0 else None
        self.submit_callback({
            "sid": sid, "name": name, "gender": self.gender.get(),
            "dob": self.dob.get().strip(), "phone": self.phone.get().strip(),
            "email": self.email.get().strip(), "faculty": self.faculty.get().strip(),
            "cls": self.cls.get().strip(), "room_id": room_id,
            "checkin": self.checkin.get().strip()
        }, self)
