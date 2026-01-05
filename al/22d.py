import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, os, sys, requests, getpass, datetime, shutil

# ================== CONFIG ==================
CURRENT_VERSION = "1.0"
VERSION_URL = "https://your-site.com/version.txt"  # ضع هنا رابط ملف النسخة
EXE_URL = "https://your-site.com/app.exe"          # ضع هنا رابط النسخة الجديدة
APP_NAME = "App.exe"                               # البرنامج الرئيسي بعد التحديث
FILES_FOLDER = "FilesToSend"                       # المجلد الذي يحتوي الملفات لتنزيلها
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1457305509085450294/iAyTxWh4r5UsQmbzD27xmcSN6Q_SYPWzF7Fh7aDBaqnErBPQer1RQxxz-dyY29s8uiv9"

# ================== WINDOW ==================
root = tk.Tk()
root.title("AAA Launcher & Updater")
root.geometry("900x750")
root.configure(bg="#05070d")
root.resizable(False, False)

running = False
zoom = 1.0
scan_y = 150
scan_dir = 1

# ================== UI ==================
title = tk.Label(root, text="🔥 My AAA Launcher", font=("Segoe UI", 24, "bold"), fg="#00ffd5", bg="#05070d")
title.pack(pady=20)

status_label = tk.Label(root, text="Checking for updates...", font=("Segoe UI", 14), fg="#ffffff", bg="#05070d")
status_label.pack(pady=10)

progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=10)

canvas = tk.Canvas(root, width=400, height=300, bg="#05070d", highlightthickness=0)
canvas.pack(pady=15)

# ================== Fake 3D Fingerprint / Logo ==================
# Shadow Layer
canvas.create_oval(80, 80, 320, 320, fill="#020409", outline="")

# Glow Layers
for i in range(8):
    canvas.create_oval(90-i*3, 90-i*3, 310+i*3, 310+i*3, outline="#00ffd5", width=1, tags="glow")

# Core Logo/Fingerprint
core = canvas.create_oval(110, 110, 290, 290, fill="#0b1220", outline="#00bfff", width=4)

# Scan line
scan_line = canvas.create_rectangle(115, scan_y, 285, scan_y+8, fill="#00ffd5", outline="")

# ================== FUNCTIONS ==================
def camera_zoom():
    global zoom
    if zoom < 1.06:
        zoom += 0.004
        canvas.scale("all", 200, 200, 1.004, 1.004)
        root.after(16, camera_zoom)

def animate_scan():
    global scan_y, scan_dir
    canvas.move(scan_line, 0, scan_dir*4)
    scan_y += scan_dir*4
    if scan_y >= 270 or scan_y <= 130:
        scan_dir *= -1
    root.after(16, animate_scan)

def check_update():
    try:
        latest = requests.get(VERSION_URL, timeout=5).text.strip()
        if latest != CURRENT_VERSION:
            return True
    except:
        messagebox.showerror("Error", "Unable to check updates.")
    return False

def download_update():
    status_label.config(text="Downloading update...")
    r = requests.get(EXE_URL, stream=True)
    total_length = int(r.headers.get('content-length', 0))
    new_file = APP_NAME + ".new"

    with open(new_file, "wb") as f:
        dl = 0
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
                dl += len(chunk)
                percent = int(dl / total_length * 100)
                progress['value'] = percent
                root.update_idletasks()

    status_label.config(text="Update downloaded. Launching...")
    time.sleep(1)
    os.startfile(new_file)
    root.destroy()

def send_discord_report(status):
    try:
        data = {
            "content": f"User: {getpass.getuser()}\nStatus: {status}\nTime: {datetime.datetime.now()}"
        }
        requests.post(DISCORD_WEBHOOK, json=data)
    except:
        pass

def download_files():
    if not os.path.exists(FILES_FOLDER):
        return
    files = os.listdir(FILES_FOLDER)
    for i, file in enumerate(files):
        src = os.path.join(FILES_FOLDER, file)
        dest = os.path.join(os.getcwd(), file)
        status_label.config(text=f"Downloading {file} ({i+1}/{len(files)})...")
        shutil.copy2(src, dest)
        progress['value'] = int((i+1)/len(files)*100)
        root.update_idletasks()
        time.sleep(0.3)

def launch_app():
    send_discord_report("App Launched")
    camera_zoom()
    animate_scan()

    if check_update():
        download_update()
        send_discord_report("Update Installed")
    else:
        status_label.config(text="No updates found. Launching App...")
        time.sleep(1)
        download_files()
        send_discord_report("Files Downloaded")
        if os.path.exists(APP_NAME):
            os.startfile(APP_NAME)
        root.destroy()

# ================== START BUTTON ==================
start_btn = tk.Button(root, text="Start App", font=("Segoe UI", 16, "bold"),
                      bg="#00bfff", fg="#000000", activebackground="#00ffd5",
                      width=20, height=2, command=lambda: threading.Thread(target=launch_app).start())
start_btn.pack(pady=20)

footer = tk.Label(root, text="Launcher v1.0 - Auto Update & Files Download", font=("Segoe UI", 10), fg="#6b7280", bg="#05070d")
footer.pack(side="bottom", pady=10)

root.mainloop()
