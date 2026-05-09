import customtkinter as ctk
from utils.theme import *
from utils.widgets import Table
from views.base_dialog import BaseDialog, ConfirmDialog, _shake

def fmt_money(v):
    try: return f"{float(v):,.0f}đ"
    except: return "0đ"

class RoomsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._rooms = []
        self._page_size = 10
        self._current_page = 0
        self._build()

    def set_controller(self, ctrl): self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=72, corner_radius=0,
                          border_width=1, border_color=C["border"])
        tb.pack(fill="x"); tb.pack_propagate(False)
        title_box = ctk.CTkFrame(tb, fg_color="transparent")
        title_box.pack(side="left", padx=22, pady=13)
        SectionTitle(title_box, "Phòng ở").pack(anchor="w")
        ctk.CTkLabel(title_box, text="Danh sách phòng ký túc xá",
                     font=ctk.CTkFont(FONT_FAMILY, 11),
                     text_color=C["text3"]).pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(tb, text="+  Thêm phòng", command=self._on_add_click,
                      height=36, width=128, corner_radius=8,
                      fg_color=C["primary"], hover_color=C["accent"],
                      text_color=C["white"], font=ctk.CTkFont(FONT_FAMILY,12,"bold")
                      ).pack(side="right", padx=18, pady=18)

        bar = ctk.CTkFrame(self, fg_color=C["card"], corner_radius=8,
                           border_width=1, border_color=C["border"], height=56)
        bar.pack(fill="x", padx=18, pady=(14, 10))
        bar.pack_propagate(False)

        self._bld_var = ctk.StringVar(value="Tất cả tòa")
        self._bld_dd  = Dropdown(bar, ["Tất cả tòa"], variable=self._bld_var,
                                  command=lambda _: self._on_filter(), width=150)
        self._bld_dd.pack(side="left", padx=(12,8), pady=10)

        self.status_var = ctk.StringVar(value="Tất cả")
        Dropdown(bar, ["Tất cả","Còn trống","Đang ở","Bảo trì"],
                 variable=self.status_var,
                 command=lambda _: self._on_filter(), width=130).pack(side="left", padx=(0,8), pady=10)

        self.floor_var = ctk.StringVar(value="Tất cả tầng")
        self.floor_dd = Dropdown(bar, ["Tất cả tầng"] + [f"Tầng {i}" for i in range(1,11)],
                 variable=self.floor_var,
                 command=lambda _: self._on_filter(), width=140)
        self.floor_dd.pack(side="left", padx=(0,8), pady=10)

        self.count_lbl = ctk.CTkLabel(bar, text="",
                                       font=ctk.CTkFont(FONT_FAMILY,12),
                                       text_color=C["text2"])
        self.count_lbl.pack(side="left", padx=8)

        self.next_page_btn = ctk.CTkButton(bar, text=">", width=36, height=32,
                                           command=lambda: self._change_page(1),
                                           fg_color=C["card2"], hover_color=C["primary3"],
                                           text_color=C["primary"], corner_radius=8)
        self.next_page_btn.pack(side="right", padx=(4, 12), pady=12)

        self.page_lbl = ctk.CTkLabel(bar, text="Trang 1/1",
                                     font=ctk.CTkFont(FONT_FAMILY,12),
                                     text_color=C["text2"])
        self.page_lbl.pack(side="right", padx=6, pady=12)

        self.prev_page_btn = ctk.CTkButton(bar, text="<", width=36, height=32,
                                           command=lambda: self._change_page(-1),
                                           fg_color=C["card2"], hover_color=C["primary3"],
                                           text_color=C["primary"], corner_radius=8)
        self.prev_page_btn.pack(side="right", padx=(4, 0), pady=12)

        self.rooms_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.rooms_container.pack(fill="both", expand=True, padx=18, pady=(0,18))

    def set_building_options(self, buildings):
        opts = ["Tất cả tòa"] + [b['name'] for b in buildings]
        self._bld_dd.configure(values=opts)
        self._buildings = buildings

    def _on_filter(self):
        if self.controller:
            bname = self._bld_var.get()
            bid = None
            if bname != "Tất cả tòa":
                m = [b for b in getattr(self,'_buildings',[]) if b['name']==bname]
                if m: bid = m[0]['id']
            floor = self.floor_var.get()
            floor_num = None if floor == "Tất cả tầng" else int(floor.split()[-1])
            self.controller.load_data(self.status_var.get(), bid, floor_num)

    def _on_add_click(self):
        if self.controller: self.controller.show_add_dialog()

    def _on_row_click(self, idx, row):
        if self.controller: self.controller.show_detail(idx)

    def update_table(self, rooms, rows):
        self._rooms = rooms
        self._current_page = 0
        self.render_cards(rooms)

    def get_rooms(self): return self._rooms

    def _total_pages(self):
        return max(1, (len(self._rooms) + self._page_size - 1) // self._page_size)

    def _change_page(self, step):
        total_pages = self._total_pages()
        new_page = min(max(self._current_page + step, 0), total_pages - 1)
        if new_page != self._current_page:
            self._current_page = new_page
            self.render_cards(self._rooms)

    def _update_pagination(self):
        total_pages = self._total_pages()
        if self._current_page >= total_pages:
            self._current_page = total_pages - 1

        total_rooms = len(self._rooms)
        if total_rooms:
            shown_start = self._current_page * self._page_size + 1
            shown_end = min(shown_start + self._page_size - 1, total_rooms)
            count_text = f"{shown_start}-{shown_end} / {total_rooms} phòng"
        else:
            count_text = "0 phòng"

        self.count_lbl.configure(text=count_text)
        self.page_lbl.configure(text=f"Trang {self._current_page + 1}/{total_pages}")
        self.prev_page_btn.configure(state="normal" if self._current_page > 0 else "disabled")
        self.next_page_btn.configure(state="normal" if self._current_page < total_pages - 1 else "disabled")

    def _card_columns(self):
        width = self.rooms_container.winfo_width()
        if width <= 1 or width >= 980:
            return 5
        if width >= 760:
            return 4
        return 3

    def _status_style(self, status):
        styles = {
            "available": ("Còn trống", C["green"], C["green_bg"]),
            "occupied": ("Đang ở", C["rose"], C["rose_bg"]),
            "maintenance": ("Bảo trì", C["amber"], C["amber_bg"]),
        }
        return styles.get(status, ("Không rõ", C["text2"], C["card2"]))

    def _bind_card_events(self, widget, enter, leave, click):
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
        if not isinstance(widget, ctk.CTkButton):
            widget.bind("<Button-1>", click)
        for child in widget.winfo_children():
            self._bind_card_events(child, enter, leave, click)

    def render_cards(self, rooms):

        for w in self.rooms_container.winfo_children():
            w.destroy()

        self._update_pagination()
        try:
            self.rooms_container._parent_canvas.yview_moveto(0)
        except Exception:
            pass

        if not rooms:
            ctk.CTkLabel(self.rooms_container, text="Không có phòng phù hợp",
                         font=ctk.CTkFont(FONT_FAMILY, 13),
                         text_color=C["text3"]).pack(pady=40)
            return

        grid = ctk.CTkFrame(
            self.rooms_container,
            fg_color="transparent"
        )

        grid.pack(
            fill="x",
            padx=2,
            pady=(0, 8)
        )

        columns = self._card_columns()
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1, uniform="room_cards")

        start = self._current_page * self._page_size
        end = start + self._page_size
        for offset, room in enumerate(rooms[start:end]):
            idx = start + offset

            current_people = room.get("current_occupants", room.get("current_occupancy", 0))
            max_people = room.get("capacity", 0)

            price = room.get("price", 0)

            status = room.get("status", "available")

            building = room.get("building_name") or ""
            building_code = building.split()[-1].upper() if building else ""

            gender = "Nam" if building_code in ["A", "C"] else "Nữ"

            room_type = "VIP" if str(room.get("type", "")).lower() == "vip" else "Thường"

            status_text, status_color, status_bg = self._status_style(status)
            occupancy = min(current_people / max_people, 1) if max_people else 0

            row = offset // columns
            col = offset % columns
            card = ctk.CTkFrame(
                grid,
                fg_color=C["card"],
                corner_radius=8,
                border_width=1,
                border_color=C["border"],
                width=176,
                height=178
            )

            card.grid(
                row=row,
                column=col,
                padx=7,
                pady=7,
                sticky="nsew"
            )

            card.grid_propagate(False)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(12, 0))
            ctk.CTkLabel(
                top,
                text=str(room.get("room_number", "")),
                font=ctk.CTkFont(FONT_FAMILY, 20, "bold"),
                text_color=C["text"]
            ).pack(side="left")
            ctk.CTkLabel(
                top,
                text=f"  {status_text}  ",
                fg_color=status_bg,
                corner_radius=6,
                font=ctk.CTkFont(FONT_FAMILY, 10, "bold"),
                text_color=status_color
            ).pack(side="right", pady=1)

            ctk.CTkLabel(
                card,
                text=f"{building} - {room_type} - {gender}",
                font=ctk.CTkFont(FONT_FAMILY, 11),
                text_color=C["text2"]
            ).pack(anchor="w", padx=12, pady=(5, 0))

            stats = ctk.CTkFrame(card, fg_color="transparent")
            stats.pack(fill="x", padx=12, pady=(12, 0))

            left = ctk.CTkFrame(stats, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(left, text="Sức chứa", font=ctk.CTkFont(FONT_FAMILY, 10),
                         text_color=C["text3"]).pack(anchor="w")
            ctk.CTkLabel(left, text=f"{current_people}/{max_people} người",
                         font=ctk.CTkFont(FONT_FAMILY, 13, "bold"),
                         text_color=C["text"]).pack(anchor="w")

            right = ctk.CTkFrame(stats, fg_color="transparent")
            right.pack(side="right", fill="x")
            ctk.CTkLabel(right, text="Giá thuê", font=ctk.CTkFont(FONT_FAMILY, 10),
                         text_color=C["text3"]).pack(anchor="e")
            ctk.CTkLabel(right, text=fmt_money(price),
                         font=ctk.CTkFont(FONT_FAMILY, 13, "bold"),
                         text_color=C["text"]).pack(anchor="e")

            progress = ctk.CTkProgressBar(
                card,
                height=6,
                corner_radius=4,
                fg_color=C["card2"],
                progress_color=status_color
            )
            progress.pack(fill="x", padx=12, pady=(8, 0))
            progress.set(occupancy)

            detail_btn = ctk.CTkButton(
                card,
                text="Chi tiết",
                height=32,
                corner_radius=8,
                fg_color=C["primary"],
                hover_color=C["accent"],
                command=lambda i=idx: self._on_row_click(i, None),
                font=ctk.CTkFont(FONT_FAMILY, 12, "bold")
            )

            detail_btn.pack(
                side="bottom",
                fill="x",
                padx=12,
                pady=12
            )

            def enter(e, c=card):
                c.configure(
                    fg_color=C["card2"],
                    border_color=C["primary2"]
                )

            def leave(e, c=card):
                c.configure(
                    fg_color=C["card"],
                    border_color=C["border"]
                )

            self._bind_card_events(card, enter, leave, lambda e, i=idx: self._on_row_click(i, None))



class RoomDetailDialog(ctk.CTkToplevel):
    """Chi tiết phòng — xem SV đang ở, sửa, xóa."""
    def __init__(self, master, room, controller):
        super().__init__(master)
        self.room = room
        self.controller = controller
        self._dialog_w = 820
        self._dialog_h = 580
        self.title(f"Phòng {room['room_number']} — {room['building_name']}")
        self.geometry(f"{self._dialog_w}x{self._dialog_h}")
        self.minsize(760, 520)
        self.resizable(True, True)
        self.configure(fg_color=C["bg"])
        self.update_idletasks()
        try:
            x = master.winfo_rootx()+(master.winfo_width()-self._dialog_w)//2
            y = master.winfo_rooty()+(master.winfo_height()-self._dialog_h)//2
            self.geometry(f"{self._dialog_w}x{self._dialog_h}+{x}+{y}")
        except: pass
        self.after(70, self._init_grab)
        self._build()

    def _init_grab(self):
        try: self.lift(); self.focus_force(); self.grab_set()
        except: pass

    def _close(self):
        try: self.grab_release()
        except: pass
        self.destroy()

    def _build(self):
        r = self.room
        hdr = ctk.CTkFrame(self, fg_color=C["primary"], corner_radius=0, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"🚪  Phòng {r['room_number']} — {r['building_name']}",
                     font=ctk.CTkFont(FONT_FAMILY,14,"bold"),
                     text_color=C["white"]).pack(side="left", padx=16, pady=14)

        body = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        body.pack(fill="both", expand=True, padx=18, pady=12)
        body.grid_columnconfigure((0,1), weight=1)

        # Info grid
        ic = ctk.CTkFrame(body, fg_color=C["card"], corner_radius=8,
                          border_width=1, border_color=C["border"])
        ic.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 8))
        ig = ctk.CTkFrame(ic, fg_color="transparent")
        ig.pack(fill="x", padx=14, pady=12)
        for i in range(4): ig.grid_columnconfigure(i, weight=1)
        st_lbl = {"available":"✓ Trống","occupied":"● Đang ở","maintenance":"⚠ Bảo trì"}
        infos = [("Tòa nhà",r['building_name']),("Số phòng",r['room_number']),
                 ("Tầng",str(r['floor'])),("Loại","VIP" if r['type']=='vip' else "Thường"),
                 ("Sức chứa",f"{r['capacity']} người"),
                 ("Đang ở",f"{r['current_occupants']}/{r['capacity']}"),
                 ("Giá thuê",fmt_money(r['price'])),
                 ("Trạng thái",st_lbl.get(r['status'],r['status']))]
        for i,(k,v) in enumerate(infos):
            ctk.CTkLabel(ig,text=k,font=ctk.CTkFont(FONT_FAMILY,10,"bold"),
                         text_color=C["text3"]).grid(row=(i//4)*2,column=i%4,sticky="w",padx=6,pady=(4,0))
            ctk.CTkLabel(ig,text=str(v),font=ctk.CTkFont(FONT_FAMILY,13),
                         text_color=C["text"]).grid(row=(i//4)*2+1,column=i%4,sticky="w",padx=6,pady=(0,4))

        # Sinh viên trong phòng
        sc = ctk.CTkFrame(body, fg_color=C["card"], corner_radius=8,
                          border_width=1, border_color=C["border"])
        sc.grid(row=1,column=0,columnspan=2,sticky="ew",padx=4,pady=4)
        ctk.CTkLabel(sc,text="👥  Sinh viên đang ở",
                     font=ctk.CTkFont(FONT_FAMILY,13,"bold"),
                     text_color=C["text"]).pack(anchor="w",padx=14,pady=(10,6))
        from models import database as db
        occupants = db.get_students_in_room(r['id'])
        if occupants:
            Table(sc,[("MSSV",130),("Họ và tên",280),("SĐT",140),("Ngày vào",130)],
                  rows=[[s['student_id'],s['fullname'],s.get('phone','—'),s.get('checkin_date','—')]
                        for s in occupants]).pack(fill="both",expand=True,padx=10,pady=(0,10))
        else:
            ctk.CTkLabel(sc,text="Phòng trống",font=ctk.CTkFont(FONT_FAMILY,12),
                         text_color=C["text3"]).pack(pady=14)

        # Footer
        foot = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0, height=56)
        foot.pack(fill="x", side="bottom"); foot.pack_propagate(False)
        ctk.CTkButton(foot, text="✕  Đóng", width=90, height=34,
                      fg_color=C["card2"], hover_color=C["primary3"],
                      text_color=C["text2"], corner_radius=8,
                      command=self._close).pack(side="left", padx=12, pady=11)
        ctk.CTkButton(foot, text="🗑  Xóa phòng", width=120, height=34,
                      fg_color=C["rose_bg"], hover_color="#FECACA",
                      text_color=C["rose"], corner_radius=8,
                      font=ctk.CTkFont(FONT_FAMILY,12,"bold"),
                      command=self._delete).pack(side="right", padx=6, pady=11)
        ctk.CTkButton(foot, text="✏  Sửa phòng", width=120, height=34,
                      fg_color=C["blue_bg"], hover_color="#DBEAFE",
                      text_color=C["blue"], corner_radius=8,
                      font=ctk.CTkFont(FONT_FAMILY,12,"bold"),
                      command=self._edit).pack(side="right", padx=6, pady=11)

    def _edit(self):
        self._close()
        if self.controller: self.controller.show_edit_dialog(self.room)

    def _delete(self):
        if self.room['current_occupants'] > 0:
            import tkinter.messagebox as mb
            mb.showwarning("Không thể xóa",
                           f"Phòng đang có {self.room['current_occupants']} sinh viên!")
            return
        if self.controller: self.controller.confirm_delete_room(self, self.room)


class AddRoomDialogUI(BaseDialog):
    def __init__(self, master, buildings_data, submit_callback, prefill=None):
        title = "✏  Sửa phòng" if prefill else "🚪  Thêm phòng mới"
        super().__init__(master, title, 480, 400)
        self.submit_callback = submit_callback
        self.buildings = buildings_data
        self.prefill   = prefill
        b_labels = [b['name'] for b in buildings_data] or ["Chưa có tòa nhà"]

        self.field("Tòa nhà *", 0, 0, 2)
        self.bld_var = ctk.StringVar(value=b_labels[0])
        self.bld = Dropdown(self.body, b_labels, variable=self.bld_var)
        self.bld.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

        self.field("Số phòng *", 2, 0);  self.rnum  = Entry(self.body, "101")
        self.rnum.grid(row=3, column=0, sticky="ew", padx=4, pady=2)
        self.field("Tầng *", 2, 1);       self.floor = Entry(self.body, "1")
        self.floor.grid(row=3, column=1, sticky="ew", padx=4, pady=2)

        self.field("Sức chứa", 4, 0);    self.cap   = Entry(self.body, "4")
        self.cap.grid(row=5, column=0, sticky="ew", padx=4, pady=2)
        self.field("Loại phòng", 4, 1)
        self.rtype = Dropdown(self.body, ["standard","vip"])
        self.rtype.grid(row=5, column=1, sticky="ew", padx=4, pady=2)

        self.field("Giá thuê (đ/tháng)", 6, 0, 2)
        self.price = Entry(self.body, "500000")
        self.price.grid(row=7, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

        self.field("Trạng thái", 8, 0, 2)
        self.status = Dropdown(self.body, ["available","occupied","maintenance"])
        self.status.grid(row=9, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

        if prefill:
            self.ok_btn.configure(text="✓  Lưu thay đổi")
            # pre-fill building
            bn = prefill.get('building_name','')
            if bn in b_labels: self.bld_var.set(bn)
            self.rnum.delete(0,"end");  self.rnum.insert(0, prefill.get('room_number',''))
            self.floor.delete(0,"end"); self.floor.insert(0, str(prefill.get('floor',1)))
            self.cap.delete(0,"end");   self.cap.insert(0, str(prefill.get('capacity',4)))
            self.rtype.set(prefill.get('type','standard'))
            self.price.delete(0,"end"); self.price.insert(0, str(int(prefill.get('price',500000))))
            self.status.set(prefill.get('status','available'))

    def _submit(self):
        rnum = self.rnum.get().strip()
        if not rnum or not self.buildings: _shake(self.ok_btn); return
        try:
            idx   = list(self.bld.cget("values")).index(self.bld_var.get())
            bid   = self.buildings[idx]['id']
            floor = int(self.floor.get() or 1)
            cap   = int(self.cap.get() or 4)
            price = float(self.price.get().replace(',','') or 500000)
        except: _shake(self.ok_btn); return
        self.submit_callback(
            {"bid": bid, "rnum": rnum, "floor": floor, "cap": cap,
             "rtype": self.rtype.get(), "price": price, "status": self.status.get()},
            self
        )
