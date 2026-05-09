import customtkinter as ctk
from utils.theme import *

class BaseDialog(ctk.CTkToplevel):
    def __init__(self, master, title, width=500, height=500):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.update_idletasks()
        try:
            x = master.winfo_rootx() + (master.winfo_width()  - width)  // 2
            y = master.winfo_rooty() + (master.winfo_height() - height) // 2
            self.geometry(f"+{x}+{y}")
        except: pass
        # delay grab_set để tránh lag / lúc vào được lúc không
        self.after(80, self._init_grab)

        tb = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0, height=50)
        tb.pack(fill="x"); tb.pack_propagate(False)
        ctk.CTkLabel(tb, text=title,
                     font=ctk.CTkFont(FONT_FAMILY, 15, "bold"),
                     text_color=C["text"]).pack(side="left", padx=20, pady=12)

        footer = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0, height=56)
        footer.pack(fill="x", side="bottom"); footer.pack_propagate(False)
        GhostBtn(footer, "✕  Hủy", command=self._close, width=100).pack(side="left", padx=16, pady=10)
        self.ok_btn = PrimaryBtn(footer, "✓  Lưu", command=self._submit, width=120)
        self.ok_btn.pack(side="right", padx=16, pady=10)

        self.body = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        self.body.pack(fill="both", expand=True, padx=20, pady=16)
        self.body.grid_columnconfigure((0,1), weight=1)

    def _init_grab(self):
        try: self.lift(); self.focus_force(); self.grab_set()
        except: pass

    def _close(self):
        try: self.grab_release()
        except: pass
        self.destroy()

    def field(self, label, row, col=0, colspan=1):
        ctk.CTkLabel(self.body, text=label,
                     font=ctk.CTkFont(FONT_FAMILY, 11, "bold"),
                     text_color=C["text2"]
                     ).grid(row=row*2, column=col, columnspan=colspan,
                            sticky="w", pady=(8,2), padx=4)

    def _submit(self):
        pass

class ConfirmDialog(ctk.CTkToplevel):
    """Hộp xác nhận Yes/No dùng chung."""
    def __init__(self, master, message, on_confirm,
                 title="Xác nhận", confirm_text="✓  Xác nhận", danger=False):
        super().__init__(master)
        self.title(title)
        self.geometry("380x190")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.on_confirm = on_confirm
        self.update_idletasks()
        try:
            x = master.winfo_rootx() + (master.winfo_width()  - 380) // 2
            y = master.winfo_rooty() + (master.winfo_height() - 190) // 2
            self.geometry(f"+{x}+{y}")
        except: pass
        self.after(60, self._init_grab)

        ctk.CTkLabel(self, text="⚠️" if danger else "❓",
                     font=ctk.CTkFont(size=32)).pack(pady=(20,4))
        ctk.CTkLabel(self, text=message,
                     font=ctk.CTkFont(FONT_FAMILY, 13),
                     text_color=C["text"],
                     wraplength=340, justify="center").pack(padx=24)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=16)
        ctk.CTkButton(row, text="✕  Hủy", width=110, height=36,
                      fg_color=C["card2"], hover_color=C["primary3"],
                      text_color=C["text2"], corner_radius=8,
                      font=ctk.CTkFont(FONT_FAMILY, 13),
                      command=self._close).pack(side="left", padx=8)
        ok_c  = C["rose"]    if danger else C["primary"]
        ok_hv = "#A52820"    if danger else C["accent"]
        ctk.CTkButton(row, text=confirm_text, width=130, height=36,
                      fg_color=ok_c, hover_color=ok_hv,
                      text_color=C["white"], corner_radius=8,
                      font=ctk.CTkFont(FONT_FAMILY, 13, "bold"),
                      command=self._ok).pack(side="left", padx=8)
        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._close())

    def _init_grab(self):
        try: self.lift(); self.focus_force(); self.grab_set()
        except: pass

    def _close(self):
        try: self.grab_release()
        except: pass
        self.destroy()

    def _ok(self):
        self._close()
        if self.on_confirm: self.on_confirm()

def _shake(widget):
    widget.configure(fg_color=C["rose"])
    widget.after(200, lambda: widget.configure(fg_color=C["primary"]))
