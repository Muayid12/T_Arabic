import customtkinter as ctk
import arabic_reshaper
from bidi.algorithm import get_display
import pyperclip
import tkinter as tk
import ctypes
import json
import os
import keyboard


DEFAULT_STATUS = f"⌨️ اكتب بالعربية..."

# ===== إعداد الواجهة =====
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.overrideredirect(True)
app.attributes("-topmost", True)
app.wm_attributes("-alpha", 0.7)
app.config(bg="#202124")

# ===== حفظ واسترجاع الموقع =====
position_file = "position.json"

def load_position():
    if os.path.exists(position_file):
        try:
            with open(position_file, "r") as f:
                pos = json.load(f)
                app.geometry(f"270x130+{pos['x']}+{pos['y']}")
        except:
            app.geometry("270x130+100+100")
    else:
        app.geometry("270x130+100+100")

def save_position():
    try:
        geo = app.geometry()
        parts = geo.split("+")
        if len(parts) >= 3:
            x, y = parts[1], parts[2]
            with open(position_file, "w") as f:
                json.dump({"x": int(x), "y": int(y)}, f)
    except:
        pass

load_position()

# ===== Win32 constants =====
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x20
WS_EX_LAYERED = 0x80000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

hwnd = ctypes.windll.user32.GetParent(app.winfo_id())
click_through_enabled = False

# ===== إخفاء من Alt+Tab =====
style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

def toggle_click_through():
    global click_through_enabled
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if not click_through_enabled:
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
        click_btn.configure(text="🖱️ Click-Through: ON", fg_color="#1b5e20")
        click_through_enabled = True
    else:
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_TRANSPARENT)
        click_btn.configure(text="🖱️ Click-Through: OFF", fg_color="#2b2b2b")
        click_through_enabled = False

def close_app():
    save_position()
    app.destroy()
    os._exit(0)

# ===== شريط علوي =====
title_bar = tk.Frame(app, bg="#202124", height=26)
title_bar.pack(fill="x", side="top")

close_btn = tk.Canvas(title_bar, width=14, height=14, bg="#202124", highlightthickness=0)
close_btn.create_oval(2, 2, 12, 12, fill="#ff5f57", outline="#ff5f57")
close_btn.bind("<Button-1>", lambda e: close_app())
close_btn.place(relx=1.0, x=-24, y=6, anchor="ne")

def start_move(e):
    app.x, app.y = e.x, e.y

def stop_move(e):
    save_position()
    app.x = app.y = None

def on_motion(e):
    x = e.x_root - app.x
    y = e.y_root - app.y
    app.geometry(f"+{x}+{y}")

title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", on_motion)

# ===== واجهة النص =====
frame = ctk.CTkFrame(app, fg_color="#202124", corner_radius=10)
frame.pack(expand=True, fill="both", padx=8, pady=(0, 6))

entry = tk.Text(frame, height=3, width=25, font=("Segoe UI", 12),
                bg="#2b2b2b", fg="white", insertbackground="white",
                wrap="word", relief="flat", bd=0)
entry.pack(pady=(6, 2), padx=6)
entry.tag_configure("right", justify="right")
entry.tag_add("right", "1.0", "end")

status = ctk.CTkLabel(frame, text=DEFAULT_STATUS, font=("Segoe UI", 11))
status.pack(pady=(0, 3))

click_btn = ctk.CTkButton(frame, text="🖱️ Click-Through: OFF", command=toggle_click_through,
                          width=200, height=26, fg_color="#2b2b2b", hover_color="#3a3a3a")
click_btn.pack(pady=(0, 3))

# ===== معالجة الأحرف ر و ز =====
def fix_raa_zay(text):
    connected_letters = "بتثجحخسشصضطظعغفقكلمنهي"
    result = ""
    for i, ch in enumerate(text):
        if ch in ["ر", "ز"] and i > 0 and text[i - 1] in connected_letters:
            result += "ـ" + ch
        else:
            result += ch
    return result

# ===== نسخ تلقائي =====
def auto_fix_copy(e=None):
    text = entry.get("1.0", tk.END).strip()
    if text:
        text = fix_raa_zay(text)
        reshaped = arabic_reshaper.reshape(text)
        fixed = get_display(reshaped)
        pyperclip.copy(" " + fixed)
        status.configure(text="✅ تم النسخ تلقائيًا", text_color="lightgreen")
    else:
        status.configure(text=DEFAULT_STATUS, text_color="gray")

def align_right_live(e=None):
    entry.tag_add("right", "1.0", "end")
    auto_fix_copy()

entry.bind("<KeyRelease>", align_right_live)

# ===== زر Delete لحذف النص =====
def clear_text(event=None):
    entry.delete("1.0", "end")
    status.configure(text="🗑️ تم الحذف", text_color="gray")

app.bind("<Delete>", clear_text)

# ===== Global Hotkey =====
keyboard.add_hotkey('-', toggle_click_through)

app.protocol("WM_DELETE_WINDOW", close_app)
app.mainloop()
