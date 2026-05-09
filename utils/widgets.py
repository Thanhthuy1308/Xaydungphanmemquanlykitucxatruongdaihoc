
import tkinter as tk
import customtkinter as ctk

from utils.theme import C, FONT_FAMILY

class Table(ctk.CTkFrame):
    """
    Scrollable table.
    columns: list of (header_text, width_px)
    rows: list of list/tuple of cell values
    on_select(row_index, row_data): callback when row clicked
    action_col: if True, last column is reserved for action buttons
    """
    def __init__(self, master, columns, rows=None, on_select=None,
                 action_col=False, page_size=None, **kwargs):
        kwargs.setdefault("fg_color", C["card"])
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)

        self.columns = columns
        self.on_select = on_select
        self.action_col = action_col
        self.page_size = page_size
        self._current_page = 0
        self._rows_data = []
        self._row_frames = []

        # ── Header ─────
        header = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0, height=36)
        header.pack(fill="x", padx=0, pady=(0, 0))
        header.pack_propagate(False)
        hinner = ctk.CTkFrame(header, fg_color="transparent")
        hinner.place(relx=0, rely=0, relwidth=1, relheight=1)
        for i, (col_name, col_w) in enumerate(columns):
            ctk.CTkLabel(hinner, text=col_name.upper(),
                         font=ctk.CTkFont(FONT_FAMILY, 10, "bold"),
                         text_color=C["text2"],
                         width=col_w, anchor="w").grid(row=0, column=i, padx=(8,4), pady=6, sticky="w")

        self.page_bar = None
        self.prev_btn = None
        self.next_btn = None
        self.page_lbl = None
        if self.page_size:
            self.page_bar = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=0, height=42)
            self.page_bar.pack(fill="x", side="bottom")
            self.page_bar.pack_propagate(False)
            self.prev_btn = ctk.CTkButton(
                self.page_bar, text="<", width=34, height=28,
                fg_color=C["card2"], hover_color=C["primary3"],
                text_color=C["primary"], corner_radius=8,
                command=lambda: self._change_page(-1)
            )
            self.prev_btn.pack(side="right", padx=(4, 0), pady=7)
            self.page_lbl = ctk.CTkLabel(
                self.page_bar, text="Trang 1/1",
                font=ctk.CTkFont(FONT_FAMILY, 12),
                text_color=C["text2"]
            )
            self.page_lbl.pack(side="right", padx=8, pady=7)
            self.next_btn = ctk.CTkButton(
                self.page_bar, text=">", width=34, height=28,
                fg_color=C["card2"], hover_color=C["primary3"],
                text_color=C["primary"], corner_radius=8,
                command=lambda: self._change_page(1)
            )
            self.next_btn.pack(side="right", padx=(0, 10), pady=7)

        # ── Scrollable area ─────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=C["card"], corner_radius=0)
        self.scroll.pack(fill="both", expand=True)
        self.scroll.grid_columnconfigure(0, weight=1)

        if rows:
            self.load(rows)

    def load(self, rows):
        self._rows_data = rows
        self._current_page = 0
        self._render_page()

    def _total_pages(self):
        if not self.page_size:
            return 1
        return max(1, (len(self._rows_data) + self.page_size - 1) // self.page_size)

    def _change_page(self, step):
        total_pages = self._total_pages()
        new_page = min(max(self._current_page + step, 0), total_pages - 1)
        if new_page != self._current_page:
            self._current_page = new_page
            self._render_page()

    def _visible_rows(self):
        if not self.page_size:
            return 0, self._rows_data
        start = self._current_page * self.page_size
        return start, self._rows_data[start:start + self.page_size]

    def _update_page_bar(self):
        if not self.page_size:
            return
        total_pages = self._total_pages()
        if self._current_page >= total_pages:
            self._current_page = total_pages - 1
        self.page_lbl.configure(text=f"Trang {self._current_page + 1}/{total_pages}")
        self.prev_btn.configure(state="normal" if self._current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if self._current_page < total_pages - 1 else "disabled")

    def _render_page(self):
        for f in self._row_frames:
            f.destroy()
        self._row_frames.clear()

        self._update_page_bar()
        try:
            self.scroll._parent_canvas.yview_moveto(0)
        except Exception:
            pass

        if not self._rows_data:
            empty = ctk.CTkFrame(self.scroll, fg_color="transparent")
            empty.pack(fill="x", pady=30)
            ctk.CTkLabel(empty, text="Không có dữ liệu",
                         font=ctk.CTkFont(FONT_FAMILY, 13),
                         text_color=C["text3"]).pack()
            self._row_frames.append(empty)
            return

        start_idx, rows = self._visible_rows()
        for visible_idx, row in enumerate(rows):
            idx = start_idx + visible_idx
            bg = C["card"] if visible_idx % 2 == 0 else C["bg"]
            rf = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=0, height=40)
            rf.pack(fill="x")
            rf.pack_propagate(False)

            inner = ctk.CTkFrame(rf, fg_color="transparent")
            inner.place(relx=0, rely=0, relwidth=1, relheight=1)

            for col_i, (_, col_w) in enumerate(self.columns):
                cell_val = row[col_i] if col_i < len(row) else ""
                if isinstance(cell_val, ctk.CTkBaseClass):
                    cell_val.grid(row=0, column=col_i, padx=(8,4), pady=4, sticky="w")
                else:
                    text = str(cell_val) if cell_val is not None else "—"
                    if self.action_col and col_i == len(self.columns) - 1 and text.strip():
                        btn_fg, btn_hover, btn_text = C["primary"], C["accent"], C["white"]
                        if "Hủy" in text or "Xóa" in text:
                            btn_fg, btn_hover, btn_text = C["rose_bg"], "#FECACA", C["rose"]
                        elif "Thu" in text or "Xử lý" in text:
                            btn_fg, btn_hover, btn_text = C["green_bg"], "#A7F3D0", C["green"]
                        btn = ctk.CTkButton(
                            inner,
                            text=text.replace("👁", "").strip(),
                            width=max(col_w - 10, 70),
                            height=28,
                            corner_radius=8,
                            fg_color=btn_fg,
                            hover_color=btn_hover,
                            text_color=btn_text,
                            font=ctk.CTkFont(FONT_FAMILY, 11, "bold"),
                            command=lambda i=idx, r=row: self.on_select(i, r) if self.on_select else None
                        )
                        btn.grid(row=0, column=col_i, padx=(8,4), pady=5, sticky="w")
                    else:
                        lbl = ctk.CTkLabel(inner, text=text, width=col_w, anchor="w",
                                           font=ctk.CTkFont(FONT_FAMILY, 12),
                                           text_color=C["text"])
                        lbl.grid(row=0, column=col_i, padx=(8,4), pady=4, sticky="w")

            # hover
            def on_enter(e, f=rf, bg=bg):
                f.configure(fg_color=C["primary3"])
                for child in f.winfo_children():
                    _set_bg(child, C["primary3"])
            def on_leave(e, f=rf, bg=bg):
                f.configure(fg_color=bg)
                for child in f.winfo_children():
                    _set_bg(child, bg)
            def on_click(e, i=idx, r=row):
                if self.on_select:
                    self.on_select(i, r)

            rf.bind("<Enter>", on_enter)
            rf.bind("<Leave>", on_leave)
            rf.bind("<Button-1>", on_click)
            inner.bind("<Button-1>", on_click)

            sep = ctk.CTkFrame(self.scroll, fg_color=C["border"], height=1)
            sep.pack(fill="x")
            self._row_frames.append(rf)
            self._row_frames.append(sep)

def _set_bg(widget, color):
    if isinstance(widget, ctk.CTkButton):
        return
    try:
        widget.configure(fg_color=color)
    except:
        pass
    for child in widget.winfo_children():
        _set_bg(child, color)
