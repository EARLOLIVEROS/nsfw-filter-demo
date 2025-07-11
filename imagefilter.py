import os
import shutil
import requests
import tkinter as tk
from tkinter import filedialog, messagebox

# 🔑 Replace with your DeepAI API key
API_KEY = '19dbbe14-fa2c-4f89-be2e-1bf905cd1ae7'

# ⚠️ Common NSFW filename keywords
SUSPICIOUS_KEYWORDS = ['nsfw', 'nude', 'xxx', 'adult', '18+', 'porn']

# 🧠 Check if filename looks suspicious
def is_filename_suspicious(filename):
    return any(word in filename.lower() for word in SUSPICIOUS_KEYWORDS)

# 🔍 Check image using DeepAI NSFW API
def is_image_nsfw(image_path):
    try:
        r = requests.post(
            "https://api.deepai.org/api/nsfw-detector",
            files={'image': open(image_path, 'rb')},
            headers={'api-key': API_KEY}
        )
        result = r.json()
        score = result.get("output", {}).get("nsfw_score", 0)
        return score > 0.6  # Threshold for NSFW
    except:
        return False

# 🚀 Main scan function
def scan_images(folder_path):
    quarantine_path = os.path.join(folder_path, "quarantine")
    os.makedirs(quarantine_path, exist_ok=True)

    moved_count = 0

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue

        suspicious = is_filename_suspicious(file)
        nsfw = is_image_nsfw(file_path)

        if suspicious or nsfw:
            shutil.move(file_path, os.path.join(quarantine_path, file))
            moved_count += 1

    messagebox.showinfo("Scan Complete", f"{moved_count} file(s) moved to quarantine.")

# 📂 Folder picker
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        scan_images(folder)

# 🪟 Simple Tkinter GUI
window = tk.Tk()
window.title("Safe Viewer - NSFW Image Filter")
window.geometry("350x150")
window.resizable(False, False)

label = tk.Label(window, text="Click the button to select a folder of images:", pady=20)
label.pack()

button = tk.Button(window, text="Select Folder & Scan", command=select_folder, bg="green", fg="white", padx=10, pady=5)
button.pack()

window.mainloop()
