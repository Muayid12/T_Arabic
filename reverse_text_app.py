import customtkinter as ctk 
import arabic_reshaper
from bidi.algorithm import get_display
import pyperclip
import tkinter as tk
import ctypes
import json
import os
import time
from pynput import keyboard
import speech_recognition as sr
import threading
import sounddevice as sd  
import numpy as np 

DEFAULT_STATUS = f"✅ Active - ابدا الكتابة"

# ===== Settings Management =====
settings_file = "settings.json"
position_file = "position.json"

default_settings = {
    "toggle_active_key": "home",
    "toggle_clickthrough_key": "minus",
    "clear_text_key": "delete",
    "voice_input_key": "f9",  
    "double_tap_delay": 0.5,
    "voice_language": "ar-SA"  
}

def load_settings():
    """Load settings from JSON file, create if doesn't exist"""
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_settings, **loaded}
        except:
            pass
    # Create default settings file
    save_settings(default_settings)
    return default_settings.copy()

def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
    except:
        pass

settings = load_settings()

# ===== إعداد الواجهة =====
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.overrideredirect(True)
app.attributes("-topmost", False)
app.wm_attributes("-alpha", 0.7)
app.config(bg="#202124")

# ===== حفظ واسترجاع الموقع =====
def load_position():
    if os.path.exists(position_file):
        try:
            with open(position_file, "r") as f:
                pos = json.load(f)
                app.geometry(f"270x130+{pos['x']}+{pos['y']}")
        except:
            app.geometry("270x145+100+100")
    else:
        # Create default position file
        with open(position_file, "w") as f:
            json.dump({"x": 100, "y": 100}, f)
        app.geometry("270x145+100+100")

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
is_active = True  # Start as active
previous_window = None
last_home_press = 0
double_tap_delay = settings["double_tap_delay"]
is_listening = False  # Track if currently recording
stop_listening = False  # Flag to stop recording

# ===== إخفاء من Alt+Tab =====
style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

def toggle_click_through():
    global click_through_enabled
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not click_through_enabled:
            new_style = style | WS_EX_TRANSPARENT | WS_EX_LAYERED
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            click_through_enabled = True
            print("Click-through enabled")
        else:
            new_style = style & ~WS_EX_TRANSPARENT
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            click_through_enabled = False
            print("Click-through disabled")
        # Force window to update its style
        ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 
                                          0x0001 | 0x0002 | 0x0004 | 0x0020)
    except Exception as e:
        print(f"Error toggling click-through: {e}")

def close_app():
    save_position()
    listener.stop()
    app.destroy()
    os._exit(0)

# ===== شريط علوي =====
title_bar = tk.Frame(app, bg="#202124", height=26)
title_bar.pack(fill="x", side="top")

close_btn = tk.Canvas(title_bar, width=14, height=14, bg="#202124", highlightthickness=0)
close_btn.create_oval(2, 2, 12, 12, fill="#ff5f57", outline="#ff5f57")
close_btn.bind("<Button-1>", lambda e: close_app())
close_btn.place(relx=1.0, x=-24, y=6, anchor="ne")

# Settings button
settings_btn = tk.Canvas(title_bar, width=14, height=14, bg="#202124", highlightthickness=0)
settings_btn.create_oval(2, 2, 12, 12, fill="#4a90e2", outline="#4a90e2")
settings_btn.place(relx=1.0, x=-44, y=6, anchor="ne")

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
                wrap="word", relief="flat", bd=0, state="normal")
entry.pack(pady=(6, 2), padx=6)
entry.tag_configure("right", justify="right")
entry.tag_add("right", "1.0", "end")

status = ctk.CTkLabel(frame, text=DEFAULT_STATUS, font=("Segoe UI", 11), text_color="lightgreen")
status.pack(pady=(0, 3))

# ===== Settings Window =====
def open_settings():
    settings_win = ctk.CTkToplevel(app)
    settings_win.title("Keybind Settings")
    settings_win.geometry("350x300")
    settings_win.attributes("-topmost", True)
    
    ctk.CTkLabel(settings_win, text="Edit settings.json to customize:", 
                 font=("Segoe UI", 12, "bold")).pack(pady=10)
    
    info_text = f"""

تفعيل أو إيقاف: {settings['toggle_active_key']}
تفعيل ميزة النقر عبر التطبيق أو لا: {settings['toggle_clickthrough_key']}
مسح النص: {settings['clear_text_key']}
تسجيل صوت: {settings['voice_input_key']}
التأخير بين الضغطتين (بالثواني): {settings['double_tap_delay']}

Toggle Active: {settings['toggle_active_key']} 
Toggle Click-Through: {settings['toggle_clickthrough_key']}
Clear Text: {settings['clear_text_key']}
Voice Input: {settings['voice_input_key']}
Double-Tap Delay: {settings['double_tap_delay']}s
Voice Language: {settings['voice_language']}

    """
    
    ctk.CTkLabel(settings_win, text=info_text, font=("Segoe UI", 12), 
                 justify="left").pack(pady=5)
    
    ctk.CTkButton(settings_win, text="Close & Restart App to Apply", 
                  command=settings_win.destroy).pack(pady=10)

settings_btn.bind("<Button-1>", lambda e: open_settings())

# ===== معالجة الأحرف ر و ز =====
def fix_raa_zay(text):
    result = ""
    for ch in text:
        if ch in ["ر", "ز"]:
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
        update_status()
    else:
        update_status()

def align_right_live(e=None):
    entry.tag_add("right", "1.0", "end")
    auto_fix_copy()

entry.bind("<KeyRelease>", align_right_live)

# ===== Clear Text Function =====
def clear_text(event=None):
    if is_active:
        entry.delete("1.0", "end")
        status.configure(text="🗑️ تم الحذف", text_color="gray")

# ===== Update Status Display =====
def update_status():
    if is_listening:
        status.configure(text="🎤 جاري الاستماع...", text_color="orange")
    elif is_active:
        text = entry.get("1.0", tk.END).strip()
        if text:
            status.configure(text="✅ نشط - تم النسخ", text_color="lightgreen")
        else:
            status.configure(text="✅ نشط - اكتب الآن", text_color="lightgreen")
    else:
        status.configure(text=f"⌨️ Press {settings['toggle_active_key']} twice to activate", 
                        text_color="gray")

# ===== Voice Input Function - FIXED VERSION =====
def stop_voice_recording():
    """Stop the current voice recording"""
    global stop_listening
    stop_listening = True
    status.configure(text="⏹️ جاري الإيقاف...", text_color="orange")

def voice_to_text():
    """Convert voice to text using Google Speech Recognition - FIXED for EXE packaging"""
    global is_listening, stop_listening
    
    if not is_active:
        return
    
    # Clear text before starting new recording
    entry.delete("1.0", "end")
    stop_listening = False
    
    def listen_thread():
        global is_listening, stop_listening
        recognizer = sr.Recognizer()
        
        try:
            is_listening = True
            app.after(0, update_status)
            
            print("Listening... Press F9 again to stop")
            
            # Recording parameters
            RATE = 16000
            CHANNELS = 1
            recorded_frames = []
            
            # Callback to collect audio
            def audio_callback(indata, frames, time_info, status_flag):
                if status_flag:
                    print(f"Audio status: {status_flag}")
                if not stop_listening:
                    recorded_frames.append(indata.copy())
            
            # Start recording stream using sounddevice
            with sd.InputStream(samplerate=RATE, channels=CHANNELS, 
                              dtype='int16', callback=audio_callback):
                # Keep recording until stopped
                while not stop_listening:
                    sd.sleep(100)  # Check every 100ms
            
            # Process recorded audio
            if recorded_frames:
                print("Processing audio...")
                app.after(0, lambda: status.configure(text="⏳ جاري المعالجة...", text_color="yellow"))
                
                # Concatenate all recorded frames
                audio_data = np.concatenate(recorded_frames, axis=0)
                
                # Convert to bytes (int16 format)
                audio_bytes = audio_data.tobytes()
                
                # Create AudioData object for speech_recognition
                audio = sr.AudioData(audio_bytes, RATE, 2)  # 2 bytes per sample (int16)
                
                # Recognize speech using Google
                text = recognizer.recognize_google(audio, language=settings['voice_language'])
                print(f"Recognized: {text}")
                
                # Insert text into entry
                app.after(0, lambda: insert_voice_text(text))
            else:
                print("No audio recorded")
                app.after(0, lambda: status.configure(text="⚠️ لم يتم تسجيل صوت", text_color="red"))
                app.after(2000, update_status)
                
        except sr.UnknownValueError:
            print("Could not understand audio")
            app.after(0, lambda: status.configure(text="⚠️ لم يتم فهم الصوت", text_color="red"))
            app.after(2000, update_status)
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            app.after(0, lambda: status.configure(text="❌ خطأ في الاتصال", text_color="red"))
            app.after(2000, update_status)
        except Exception as e:
            print(f"Microphone error: {e}")
            # More detailed error for debugging
            import traceback
            error_details = traceback.format_exc()
            print(error_details)
            # Save error to file for user debugging
            try:
                with open("microphone_error.txt", "w", encoding="utf-8") as f:
                    f.write(error_details)
            except:
                pass
            app.after(0, lambda: status.configure(text="❌ خطأ في المايك", text_color="red"))
            app.after(2000, update_status)
        finally:
            is_listening = False
            stop_listening = False
            app.after(0, update_status)
    
    # Run in separate thread to avoid blocking UI
    thread = threading.Thread(target=listen_thread, daemon=True)
    thread.start()

def insert_voice_text(text):
    """Insert voice-recognized text into entry"""
    if is_active:
        # Check if text contains Arabic characters
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        
        if has_arabic:
            # Process as Arabic text (apply reshaping)
            entry.insert("1.0", text)
            align_right_live()
        else:
            # Insert as English (left-to-right, no reshaping)
            entry.insert("1.0", text)
            # Don't apply Arabic processing, just copy as-is
            pyperclip.copy(text)
            update_status()

# ===== Helper Functions =====
def set_entry_focus():
    try:
        entry.focus_force()
        entry.mark_set("insert", "1.0")
        entry.icursor(0)
    except:
        pass

def bring_window_forward():
    global previous_window
    previous_window = ctypes.windll.user32.GetForegroundWindow()
    app.attributes("-topmost", True)
    app.deiconify()
    app.lift()
    hwnd_app = ctypes.windll.user32.GetParent(app.winfo_id())
    ctypes.windll.user32.ShowWindow(hwnd_app, 9)
    ctypes.windll.user32.SetForegroundWindow(hwnd_app)
    ctypes.windll.user32.BringWindowToTop(hwnd_app)

def send_window_back():
    global previous_window
    app.attributes("-topmost", False)
    if previous_window:
        try:
            current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
            foreground_thread = ctypes.windll.user32.GetWindowThreadProcessId(previous_window, None)
            if current_thread != foreground_thread:
                ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, True)
                ctypes.windll.user32.SetForegroundWindow(previous_window)
                ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, False)
            else:
                ctypes.windll.user32.SetForegroundWindow(previous_window)
        except:
            pass
    app.lower()

# ===== Toggle Active Function =====
def toggle_active():
    global is_active, previous_window
    if is_active:
        entry.delete("1.0", "end")
        entry.configure(state="disabled")
        is_active = False
        update_status()
        send_window_back()
    else:
        entry.configure(state="normal")
        is_active = True
        bring_window_forward()
        hwnd_app = ctypes.windll.user32.GetParent(app.winfo_id())
        try:
            current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
            foreground_thread = ctypes.windll.user32.GetWindowThreadProcessId(
                ctypes.windll.user32.GetForegroundWindow(), None
            )
            if current_thread != foreground_thread:
                ctypes.windll.user32.AttachThreadInput(foreground_thread, current_thread, True)
                ctypes.windll.user32.SetForegroundWindow(hwnd_app)
                ctypes.windll.user32.AttachThreadInput(foreground_thread, current_thread, False)
            else:
                ctypes.windll.user32.SetForegroundWindow(hwnd_app)
        except:
            ctypes.windll.user32.SetForegroundWindow(hwnd_app)
        app.focus_force()
        app.update()
        entry.focus_set()
        app.after(10, set_entry_focus)
        app.after(50, set_entry_focus)
        app.after(100, set_entry_focus)
        update_status()

# ===== Key Mapping Helper =====
def get_key_from_string(key_str):
    """Convert string to pynput key object"""
    key_str = key_str.lower().strip()
    
    # Special keys
    special_keys = {
        'home': keyboard.Key.home,
        'end': keyboard.Key.end,
        'insert': keyboard.Key.insert,
        'delete': keyboard.Key.delete,
        'page_up': keyboard.Key.page_up,
        'page_down': keyboard.Key.page_down,
        'backspace': keyboard.Key.backspace,
        'enter': keyboard.Key.enter,
        'tab': keyboard.Key.tab,
        'esc': keyboard.Key.esc,
        'space': keyboard.Key.space,
        'minus': '-',
    }
    
    # F keys
    for i in range(1, 13):
        special_keys[f'f{i}'] = getattr(keyboard.Key, f'f{i}')
    
    if key_str in special_keys:
        return special_keys[key_str]
    
    # Return single character for letter/number keys
    if len(key_str) == 1:
        return key_str
    
    return None

# ===== Global Hotkeys with pynput =====
def on_press(key):
    try:
        
        key_str = None
        if hasattr(key, 'char') and key.char:
            key_str = key.char.lower()
        elif hasattr(key, 'name'):
            key_str = key.name.lower()
        
        
        toggle_key = get_key_from_string(settings['toggle_active_key'])
        if (isinstance(toggle_key, str) and key_str == toggle_key) or \
           (not isinstance(toggle_key, str) and key == toggle_key):
            app.after(0, toggle_active)
            return
        
        
        clickthrough_key = get_key_from_string(settings['toggle_clickthrough_key'])
        if (isinstance(clickthrough_key, str) and key_str == clickthrough_key) or \
           (not isinstance(clickthrough_key, str) and key == clickthrough_key):
            print(f"Click-through key pressed: {key_str}")
            app.after(0, toggle_click_through)
            return
        
       
        clear_key = get_key_from_string(settings['clear_text_key'])
        if (isinstance(clear_key, str) and key_str == clear_key) or \
           (not isinstance(clear_key, str) and key == clear_key):
            app.after(0, clear_text)
            return
        
      
        voice_key = get_key_from_string(settings['voice_input_key'])
        if (isinstance(voice_key, str) and key_str == voice_key) or \
           (not isinstance(voice_key, str) and key == voice_key):
            if is_listening:
                # Stop recording
                app.after(0, stop_voice_recording)
            else:
                # Start recording
                app.after(0, voice_to_text)
            return
            
    except Exception as e:
        print(f"Error in on_press: {e}")

# Start keyboard listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Start with window visible and active
app.after(100, lambda: (bring_window_forward(), set_entry_focus()))

app.protocol("WM_DELETE_WINDOW", close_app)
app.mainloop()