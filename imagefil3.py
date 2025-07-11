import os
import shutil
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pyzipper  # 📦 For password-protected ZIP

# 🔑 Replace with your DeepAI API key
API_KEY = '19dbbe14-fa2c-4f89-be2e-1bf905cd1ae7'

# ⚠️ Common NSFW filename keywords
SUSPICIOUS_KEYWORDS = ['nsfw', 'nude', 'xxx', 'adult', '18+', 'porn']

# ✅ Check filename
def is_filename_suspicious(filename):
    return any(word in filename.lower() for word in SUSPICIOUS_KEYWORDS)

# 🔍 Check image via DeepAI NSFW API
def is_image_nsfw(image_path):
    try:
        r = requests.post(
            "https://api.deepai.org/api/nsfw-detector",
            files={'image': open(image_path, 'rb')},
            headers={'api-key': API_KEY}
        )
        result = r.json()
        score = result.get("output", {}).get("nsfw_score", 0)
        return score > 0.6
    except:
        return False

# 🔒 Zip the quarantine folder with password
def zip_quarantine_folder(folder_path, password):
    quarantine_path = os.path.join(folder_path, "quarantine")
    zip_path = os.path.join(folder_path, "quarantine.zip")

    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_LZMA) as zipf:
        zipf.setpassword(password.encode())
        zipf.setencryption(pyzipper.WZ_AES, nbits=256)

        for root, _, files in os.walk(quarantine_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=quarantine_path)
                zipf.write(file_path, arcname=arcname)

    shutil.rmtree(quarantine_path)

# 🔎 Scan folder
def scan_images(folder_path):
    quarantine_path = os.path.join(folder_path, "quarantine")
    os.makedirs(quarantine_path, exist_ok=True)

    total_scanned = 0
    moved_count = 0

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue

        total_scanned += 1
        suspicious = is_filename_suspicious(file)
        nsfw = is_image_nsfw(file_path)

        if suspicious or nsfw:
            shutil.move(file_path, os.path.join(quarantine_path, file))
            moved_count += 1

    clean_count = total_scanned - moved_count

    if moved_count > 0:
        password = simpledialog.askstring("Password", "Enter password to lock quarantine.zip:", show='*')
        if password:
            zip_quarantine_folder(folder_path, password)
            msg = f"✅ Scan Complete!\n\n" \
                  f"🖼 Scanned: {total_scanned} images\n" \
                  f"🚫 Moved to 'quarantine.zip': {moved_count}\n" \
                  f"✅ Clean images left: {clean_count}"
        else:
            msg = f"⚠️ No password entered.\n\n" \
                  f"Scanned: {total_scanned} images\n" \
                  f"Moved to 'quarantine/' (not zipped): {moved_count}\n" \
                  f"Clean images left: {clean_count}"
    else:
        msg = f"🎉 Scan Complete!\n\nNo NSFW or suspicious files found.\nTotal scanned: {total_scanned}"

    messagebox.showinfo("Scan Result", msg)

# 📂 Folder picker
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        scan_images(folder)

# 🪟 GUI setup
window = tk.Tk()
window.title("Safe Viewer - NSFW Image Scanner")
window.geometry("380x170")
window.resizable(False, False)

label = tk.Label(window, text="Click to scan a folder for NSFW images", pady=20)
label.pack()

button = tk.Button(window, text="Select Folder & Scan", command=select_folder, bg="green", fg="white", padx=10, pady=5)
button.pack()

window.mainloop()