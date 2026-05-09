
import customtkinter as ctk

C = {
    "bg":        "#F5F7FB",
    "bg2":       "#FFFFFF",
    "card":      "#FFFFFF",
    "card2":     "#F8FAFC",
    "border":    "#E5E7EB",
    "primary":   "#2563EB",
    "primary2":  "#38BDF8",
    "primary3":  "#DBEAFE",
    "accent":    "#1D4ED8",
    "text":      "#111827",
    "text2":     "#4B5563",
    "text3":     "#9CA3AF",
    "green":     "#059669",
    "green_bg":  "#D1FAE5",
    "amber":     "#B45309",
    "amber_bg":  "#FEF3C7",
    "rose":      "#DC2626",
    "rose_bg":   "#FEE2E2",
    "blue":      "#2563EB",
    "blue_bg":   "#DBEAFE",
    "white":     "#FFFFFF",
    "shadow":    "#00000014",
}

FONT_FAMILY = "Segoe UI"

def setup_theme():
    ctk.set_appearance_mode("light")
    try:
        ctk.set_default_color_theme("blue")
    except Exception:
        try:
            ctk.set_default_color_theme("blue")
        except Exception:
            pass

# ── REUSABLE WIDGETS ─────────────────────────────────────────────────────────

class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", C["card"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", C["border"])
        super().__init__(master, **kwargs)

class SectionTitle(ctk.CTkLabel):
    def __init__(self, master, text, **kwargs):
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 16, "bold"))
        kwargs.setdefault("text_color", C["text"])
        super().__init__(master, text=text, **kwargs)

class Label(ctk.CTkLabel):
    def __init__(self, master, text, size=13, bold=False, color=None, **kwargs):
        kwargs["font"] = ctk.CTkFont(FONT_FAMILY, size, "bold" if bold else "normal")
        kwargs["text_color"] = color or C["text"]
        super().__init__(master, text=text, **kwargs)

class MutedLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kwargs):
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 12))
        kwargs.setdefault("text_color", C["text3"])
        super().__init__(master, text=text, **kwargs)

class PrimaryBtn(ctk.CTkButton):
    def __init__(self, master, text, command=None, width=120, **kwargs):
        kwargs.setdefault("fg_color", C["primary"])
        kwargs.setdefault("hover_color", C["accent"])
        kwargs.setdefault("text_color", C["white"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 13, "bold"))
        kwargs.setdefault("height", 36)
        super().__init__(master, text=text, command=command, width=width, **kwargs)

class GhostBtn(ctk.CTkButton):
    def __init__(self, master, text, command=None, width=100, **kwargs):
        kwargs.setdefault("fg_color", C["card2"])
        kwargs.setdefault("hover_color", C["primary3"])
        kwargs.setdefault("text_color", C["primary"])
        kwargs.setdefault("border_color", C["border"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 12))
        kwargs.setdefault("height", 32)
        super().__init__(master, text=text, command=command, width=width, **kwargs)

class DangerBtn(ctk.CTkButton):
    def __init__(self, master, text, command=None, width=90, **kwargs):
        kwargs.setdefault("fg_color", C["rose_bg"])
        kwargs.setdefault("hover_color", "#FECACA")
        kwargs.setdefault("text_color", C["rose"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 12))
        kwargs.setdefault("height", 30)
        super().__init__(master, text=text, command=command, width=width, **kwargs)

class SuccessBtn(ctk.CTkButton):
    def __init__(self, master, text, command=None, width=90, **kwargs):
        kwargs.setdefault("fg_color", C["green_bg"])
        kwargs.setdefault("hover_color", "#A7F3D0")
        kwargs.setdefault("text_color", C["green"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 12))
        kwargs.setdefault("height", 30)
        super().__init__(master, text=text, command=command, width=width, **kwargs)

class Entry(ctk.CTkEntry):
    def __init__(self, master, placeholder='', **kwargs):
        kwargs.setdefault("fg_color", C["white"])
        kwargs.setdefault("border_color", C["border"])
        kwargs.setdefault("text_color", C["text"])
        kwargs.setdefault("placeholder_text_color", C["text3"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 36)
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 13))
        super().__init__(master, placeholder_text=placeholder, **kwargs)

class Dropdown(ctk.CTkOptionMenu):
    def __init__(self, master, values, **kwargs):
        kwargs.setdefault("fg_color", C["white"])
        kwargs.setdefault("button_color", C["primary3"])
        kwargs.setdefault("button_hover_color", C["primary2"])
        kwargs.setdefault("dropdown_fg_color", C["white"])
        kwargs.setdefault("dropdown_hover_color", C["card2"])
        kwargs.setdefault("text_color", C["text"])
        kwargs.setdefault("dropdown_text_color", C["text"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 36)
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 13))
        super().__init__(master, values=values, **kwargs)

class TextBox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", C["white"])
        kwargs.setdefault("border_color", C["border"])
        kwargs.setdefault("text_color", C["text"])
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", ctk.CTkFont(FONT_FAMILY, 13))
        super().__init__(master, **kwargs)

def stat_card(master, icon, value, label, color_key="primary", row=0, col=0):
    colors = {
        "primary": (C["primary"], C["card2"]),
        "green": (C["green"], C["green_bg"]),
        "amber": (C["amber"], C["amber_bg"]),
        "rose": (C["rose"], C["rose_bg"]),
        "blue": (C["blue"], C["blue_bg"]),
    }
    fg, bg = colors.get(color_key, colors["primary"])
    f = ctk.CTkFrame(master, fg_color=bg, corner_radius=8, border_width=1, border_color=C["border"])
    f.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
    ctk.CTkLabel(f, text=icon, font=ctk.CTkFont(size=26)).pack(pady=(14,2))
    ctk.CTkLabel(f, text=str(value), font=ctk.CTkFont(FONT_FAMILY, 22, "bold"), text_color=fg).pack()
    ctk.CTkLabel(f, text=label, font=ctk.CTkFont(FONT_FAMILY, 11), text_color=C["text2"]).pack(pady=(0,12))
    return f

def badge(master, text, kind="blue"):
    colors = {
        "green": (C["green_bg"], C["green"]),
        "amber": (C["amber_bg"], C["amber"]),
        "rose":  (C["rose_bg"], C["rose"]),
        "blue":  (C["blue_bg"], C["blue"]),
        "pink":  (C["card2"], C["primary"]),
        "gray":  ("#F3F4F6", "#6B7280"),
    }
    bg, fg = colors.get(kind, colors["blue"])
    lbl = ctk.CTkLabel(master, text=f"  {text}  ", fg_color=bg, text_color=fg, corner_radius=6, font=ctk.CTkFont(FONT_FAMILY, 11, "bold"))
    return lbl
