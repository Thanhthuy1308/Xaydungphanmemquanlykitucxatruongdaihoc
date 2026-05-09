import customtkinter as ctk
from utils.theme import *
from views.base_dialog import BaseDialog, ConfirmDialog, _shake

class BuildingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.controller = None
        self._build()

    def set_controller(self, ctrl): self.controller = ctrl

    def _build(self):
        tb = ctk.CTkFrame(self, fg_color=C["bg2"], height=56, corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        SectionTitle(tb, "🏢  Tòa nhà").pack(side="left", padx=20, pady=16)
        ctk.CTkButton(tb, text="+  Thêm tòa nhà", command=self._on_add_click,
                      height=34, width=140, corner_radius=8, border_width=2, border_color=C["primary"],
                      fg_color="transparent", hover_color=C["primary3"],
                      text_color=C["primary"], font=ctk.CTkFont(FONT_FAMILY,12,"bold")
                      ).pack(side="right", padx=16, pady=11)
        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        self.grid_frame.pack(fill="both", expand=True, padx=14, pady=14)

    def _on_add_click(self):
        if self.controller: self.controller.show_add_dialog()

    def update_grid(self, buildings):
        for w in self.grid_frame.winfo_children(): w.destroy()
        if not buildings:
            ctk.CTkLabel(self.grid_frame, text="Chưa có tòa nhà nào",
                         font=ctk.CTkFont(FONT_FAMILY,13), text_color=C["text3"]).pack(pady=40)
            return
        for i in range(3): self.grid_frame.grid_columnconfigure(i, weight=1)
        for i, b in enumerate(buildings):
            pct = int(b['occupied']/b['total_rooms']*100) if b['total_rooms'] else 0
            c_card = ctk.CTkFrame(self.grid_frame, fg_color=C["card"],
                                   corner_radius=12, border_width=1, border_color=C["border"])
            c_card.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")

            # header row with edit/delete buttons
            hdr = ctk.CTkFrame(c_card, fg_color="transparent")
            hdr.pack(fill="x", padx=12, pady=(14,0))
            ctk.CTkLabel(hdr, text="🏢", font=ctk.CTkFont(size=28)).pack(side="left")
            ctk.CTkButton(hdr, text="🗑", width=28, height=28,
                          fg_color=C["rose_bg"], hover_color="#FECACA",
                          text_color=C["rose"], corner_radius=6,
                          command=lambda b=b: self._on_delete(b)).pack(side="right", padx=(2,0))
            ctk.CTkButton(hdr, text="✏", width=34, height=30, border_width=1, border_color=C["blue"],
                          fg_color="transparent", hover_color="#DBEAFE",
                          text_color=C["blue"], corner_radius=6,
                          command=lambda b=b: self._on_edit(b)).pack(side="right", padx=2)

            Label(c_card, b['name'], size=16, bold=True).pack(anchor="w", padx=14, pady=(6,2))
            MutedLabel(c_card, b.get('description') or "Không có mô tả").pack(anchor="w", padx=14, pady=(0,10))

            sr = ctk.CTkFrame(c_card, fg_color=C["bg"], corner_radius=8)
            sr.pack(fill="x", padx=12, pady=(0,8))
            for val, lbl in [(b['total_rooms'],"Tổng phòng"),(b['occupied'] or 0,"Đang ở"),(b['floors'],"Số tầng")]:
                f = ctk.CTkFrame(sr, fg_color="transparent")
                f.pack(side="left", expand=True, pady=8)
                Label(f, str(val), size=18, bold=True, color=C["primary"]).pack()
                MutedLabel(f, lbl).pack()

            bar_bg = ctk.CTkFrame(c_card, fg_color=C["bg2"], height=8, corner_radius=4)
            bar_bg.pack(fill="x", padx=12, pady=(0,4))
            ctk.CTkFrame(bar_bg, fg_color=C["primary2"], height=8, corner_radius=4
                         ).place(relx=0, rely=0, relheight=1, relwidth=max(pct/100, 0.02))
            MutedLabel(c_card, f"Lấp đầy: {pct}%").pack(pady=(0,14))

            detail = ctk.CTkFrame(c_card, fg_color=C["bg2"], corner_radius=10)
            ctk.CTkLabel(detail, text=f"Khu: {b.get('description','')}\nSố tầng: {b.get('floors',0)}\nTổng phòng: {b.get('total_rooms',0)}", justify="left",
                         font=ctk.CTkFont(FONT_FAMILY,12), text_color=C["text2"]).pack(anchor="w", padx=10, pady=10)
            detail.place(relx=0.5, rely=0.5, anchor="center")
            detail.place_forget()

            c_card.bind("<Enter>", lambda e, d=detail: d.place(relx=0.5, rely=0.5, anchor="center"))
            c_card.bind("<Leave>", lambda e, d=detail: d.place_forget())

    def _on_edit(self, b):
        if self.controller: self.controller.show_edit_dialog(b)

    def _on_delete(self, b):
        if (b['occupied'] or 0) > 0:
            import tkinter.messagebox as mb
            mb.showwarning("Không thể xóa",
                           f"Tòa {b['name']} còn {b['occupied']} phòng đang có sinh viên!")
            return
        if self.controller:
            self.controller.confirm_delete(self, b)

class AddBuildingDialogUI(BaseDialog):
    def __init__(self, master, submit_callback, prefill=None):
        title = "✏  Sửa tòa nhà" if prefill else "🏢  Thêm tòa nhà mới"
        super().__init__(master, title, 440, 300)
        self.submit_callback = submit_callback
        self.prefill = prefill

        self.field("Tên tòa nhà *", 0, 0, 2)
        self.name = Entry(self.body, "Tòa D")
        self.name.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=2)

        self.field("Số tầng", 2, 0)
        self.floors = Entry(self.body, "5")
        self.floors.grid(row=5, column=0, sticky="ew", padx=4, pady=2)

        self.field("Mô tả", 2, 1)
        self.desc = Entry(self.body, "Khu nam / nữ / hỗn hợp")
        self.desc.grid(row=5, column=1, sticky="ew", padx=4, pady=2)

        if prefill:
            self.ok_btn.configure(text="✓  Lưu thay đổi")
            self.name.delete(0,"end");   self.name.insert(0, prefill.get('name',''))
            self.floors.delete(0,"end"); self.floors.insert(0, str(prefill.get('floors',5)))
            self.desc.delete(0,"end");   self.desc.insert(0, prefill.get('description',''))

    def _submit(self):
        name = self.name.get().strip()
        if not name: _shake(self.ok_btn); return
        try: floors = int(self.floors.get() or 5)
        except: floors = 5
        self.submit_callback(
            {"name": name, "floors": floors, "desc": self.desc.get().strip()},
            self
        )
