import tkinter as tk
from tkinter import ttk, messagebox
import os
import ctypes
import win32com.client
import json
import sys

# ---------------- SETTINGS ----------------
SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"hidden_apps": []}
    return {"hidden_apps": []}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Greška", f"Nije moguće spremiti settings: {e}")

settings = load_settings()
# ------------------------------------------

# Definiranje ShellExecute funkcije koja pokreće aplikacije
shell32 = ctypes.windll.shell32
ShellExecuteW = shell32.ShellExecuteW
ShellExecuteW.restype = ctypes.c_int
ShellExecuteW.argtypes = [
    ctypes.c_int, ctypes.c_wchar_p, ctypes.c_wchar_p,
    ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int,
]
SW_SHOWNORMAL = 1

# RECT struktura za radnu površinu
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

def get_work_area():
    """Vrati radnu površinu (bez taskbara)."""
    rect = RECT()
    SPI_GETWORKAREA = 0x0030
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect

def get_start_menu_apps():
    """Skupi aplikacije skenirajući prečace (.lnk) u Start izborniku."""
    apps = {}
    start_menu_paths = [
        os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Start Menu\\Programs'),
        os.path.join(os.environ['PROGRAMDATA'], 'Microsoft\\Windows\\Start Menu\\Programs')
    ]
    WshShell = win32com.client.Dispatch("WScript.Shell")
    for start_path in start_menu_paths:
        if not os.path.exists(start_path):
            continue
        for root, dirs, files in os.walk(start_path):
            for file in files:
                if file.endswith('.lnk'):
                    lnk_path = os.path.join(root, file)
                    try:
                        shortcut = WshShell.CreateShortcut(lnk_path)
                        target_path = shortcut.TargetPath
                        if target_path and target_path.endswith('.exe'):
                            app_name = os.path.splitext(file)[0]
                            if (app_name not in apps
                                and app_name not in settings.get("hidden_apps", [])):
                                apps[app_name] = {'path': target_path, 'args': None}
                    except Exception:
                        continue
    return dict(sorted(apps.items()))

def get_all_apps_list():
    """Vrati listu svih aplikacija (bez filtriranja)."""
    apps = []
    start_menu_paths = [
        os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Start Menu\\Programs'),
        os.path.join(os.environ['PROGRAMDATA'], 'Microsoft\\Windows\\Start Menu\\Programs')
    ]
    WshShell = win32com.client.Dispatch("WScript.Shell")
    for start_path in start_menu_paths:
        if not os.path.exists(start_path):
            continue
        for root, dirs, files in os.walk(start_path):
            for file in files:
                if file.endswith('.lnk'):
                    try:
                        shortcut = WshShell.CreateShortcut(os.path.join(root, file))
                        target_path = shortcut.TargetPath
                        if target_path and target_path.endswith('.exe'):
                            app_name = os.path.splitext(file)[0]
                            if app_name not in apps:
                                apps.append(app_name)
                    except Exception:
                        continue
    return sorted(apps)

def launch_app(app_data):
    """Pokreni odabranu aplikaciju koristeći ShellExecute."""
    if app_data:
        app_path = app_data['path']
        app_args = app_data['args']
        try:
            ShellExecuteW(0, "open", app_path, app_args, None, SW_SHOWNORMAL)
            root.iconify()
        except Exception as e:
            print(f"Greška: {e}")

# Funkcija za pomicanje klizača
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# --- Settings prozor ---
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Postavke - Sakrij aplikacije")
    settings_window.geometry("400x500")

    # onemogući interakciju s glavnim prozorom dok je Settings otvoren
    settings_window.transient(root)
    settings_window.grab_set()

    apps_all = get_all_apps_list()
    hidden = set(settings.get("hidden_apps", []))
    vars_dict = {}

    # Glavni frame
    main_frame = ttk.Frame(settings_window)
    main_frame.grid(row=0, column=0, sticky="nsew")
    settings_window.grid_rowconfigure(0, weight=1)
    settings_window.grid_columnconfigure(0, weight=1)

    # Canvas i scrollbar
    canvas = tk.Canvas(main_frame, borderwidth=0, background="#f0f0f0")
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Frame unutar canvas-a
    scroll_frame = ttk.Frame(canvas)
    window_id = canvas.create_window((0,0), window=scroll_frame, anchor="nw")

    # Prilagodi širinu frame-a širini canvas-a
    def on_canvas_configure(event):
        canvas.itemconfig(window_id, width=event.width)
        # stretch scroll_frame da popuni visinu canvas-a
        if scroll_frame.winfo_height() < event.height:
            scroll_frame.config(height=event.height)
    canvas.bind("<Configure>", on_canvas_configure)

    # Update scrollregion kad se promijeni veličina frame-a
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", on_frame_configure)

    # Dodavanje checkboxova u scroll_frame
    for app in apps_all:
        var = tk.BooleanVar(value=(app in hidden))
        chk = ttk.Checkbutton(scroll_frame, text=app, variable=var)
        chk.pack(anchor="w", padx=5, pady=2, fill="x")  # fill="x" da se proteže horizontalno
        vars_dict[app] = var

    # Scroll kotačić miša
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    settings_window.bind_all("<MouseWheel>", _on_mousewheel)

    # Spremi i restartaj aplikaciju
    def save_and_restart():
        selected = [app for app, var in vars_dict.items() if var.get()]
        settings["hidden_apps"] = selected
        save_settings(settings)
        settings_window.destroy()
        root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    btn_save = ttk.Button(settings_window, text="Spremi i Restartaj", command=save_and_restart)
    btn_save.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

    # Tipka "Prikaži sve"
    def show_all():
        for var in vars_dict.values():
            var.set(False)
    btn_show_all = ttk.Button(settings_window, text="Prikaži sve", command=show_all)
    btn_show_all.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

# --- About ---
def open_about():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.resizable(False, False)
    about_window.geometry("250x140")

    # onemogući interakciju s glavnim prozorom dok je About otvoren
    about_window.transient(root)
    about_window.grab_set()

    # Centriraj prozor iznad glavnog
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    about_width = 250
    about_height = 140
    x = root_x + (root_width - about_width) // 2
    y = root_y + (root_height - about_height) // 2
    about_window.geometry(f"{about_width}x{about_height}+{x}+{y}")

    # Frame za sadržaj
    frame = ttk.Frame(about_window)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Label sa tekstom
    label_text = "Quick Launcher\nIzrađen u Pythonu\n@2025\nDavor"
    label = tk.Label(frame, text=label_text, justify="center", font=("Segoe UI", 10))
    label.pack(expand=True, fill="both")

    # Tipka zatvori
    btn_close = ttk.Button(frame, text="Zatvori", command=about_window.destroy)
    btn_close.pack(pady=(5, 0))


# --- Glavni prozor ---
root = tk.Tk()
root.title("Quick Launcher")
root.resizable(False, False)

menu_bar = tk.Menu(root)
menu_bar.add_command(label="Postavke", command=open_settings)
menu_bar.add_command(label="About", command=open_about)
root.config(menu=menu_bar)

installed_apps = get_start_menu_apps()

# Odredi optimalan broj stupaca na temelju dimenzija ekrana
screen_width = root.winfo_screenwidth()
button_width_in_pixels = 10 * 8 + 10
num_columns = max(1, (screen_width // 2) // button_width_in_pixels)

# Stvori privremeni okvir za izračun dimenzija
temp_frame = ttk.Frame(root)
for i, (app_name, app_data) in enumerate(installed_apps.items()):
    row = i // num_columns
    column = i % num_columns
    temp_button = tk.Button(temp_frame, text=app_name,
                           width=10, height=3, wraplength=70)
    temp_button.grid(row=row, column=column, padx=5, pady=5)
temp_frame.update_idletasks()
required_width = temp_frame.winfo_reqwidth()
required_height = temp_frame.winfo_reqheight()
temp_frame.destroy()

required_width += 20
required_height += 20

max_width = int(screen_width * 0.5)
max_height = int(root.winfo_screenheight() * 0.5)

window_width = min(required_width, max_width)
window_height = min(required_height, max_height)

if required_height > max_height:
    root.geometry(f"{max_width}x{max_height}")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)

    canvas = tk.Canvas(main_frame, borderwidth=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    button_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=button_frame, anchor="nw")
    root.bind_all("<MouseWheel>", on_mousewheel)

    for i, (app_name, app_data) in enumerate(installed_apps.items()):
        row = i // num_columns
        column = i % num_columns
        app_data['name'] = app_name
        button = tk.Button(button_frame, text=app_name,
                           command=lambda data=app_data: launch_app(data),
                           width=10, height=3, wraplength=70)
        button.grid(row=row, column=column, padx=5, pady=5)

    button_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

else:
    root.geometry(f"{window_width}x{window_height}")

    button_frame = ttk.Frame(root)
    button_frame.pack(fill='both', expand=True, padx=10, pady=10)

    for i, (app_name, app_data) in enumerate(installed_apps.items()):
        row = i // num_columns
        column = i % num_columns
        app_data['name'] = app_name
        button = tk.Button(button_frame, text=app_name,
                           command=lambda data=app_data: launch_app(data),
                           width=10, height=3, wraplength=70)
        button.grid(row=row, column=column, padx=5, pady=5)
    button_frame.update_idletasks()

# Pozicioniranje iznad taskbara
#root.update_idletasks()
#work_area = get_work_area()
#x = work_area.left
#y = work_area.bottom - root.winfo_height()
#root.geometry(f"{root.winfo_width()}x{root.winfo_height()}+{x}+{y}")

root.update_idletasks()
work_area = get_work_area()

window_width = root.winfo_width()
window_height = root.winfo_height()
x = work_area.left
y = work_area.bottom - window_height - 60  # podigni prozor 50px iznad taskbara

root.geometry(f"{window_width}x{window_height}+{x}+{y}")


root.mainloop()
