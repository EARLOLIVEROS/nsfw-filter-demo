import tkinter as tk
from tkinter import ttk
import math

# ---------- FUZZY CONTROLLERS ----------
class FuzzyDehumidifier:
    def muLOW(self, rh):   return 0 if rh >= 50 else 1 if rh <= 30 else (50 - rh) / 20
    def muCOMFORT(self, rh): return 0 if rh <= 40 or rh >= 70 else (rh - 40) / 15 if rh <= 55 else (70 - rh) / 15
    def muHIGH(self, rh):  return 0 if rh <= 60 else 1 if rh >= 80 else (rh - 60) / 20
    def compute(self, rh):
        low, com, high = self.muLOW(rh), self.muCOMFORT(rh), self.muHIGH(rh)
        return max(0, min((low * 0.1 + com * 0.5 + high * 0.95) / (low + com + high + 1e-9), 1))

class FuzzyHumidifier:
    def __init__(self): self.last_rh = 45
    def mu_low(self, rh):  return 0 if rh >= 55 else 1 if rh <= 35 else (55 - rh) / 20
    def mu_ok(self, rh):   return 0 if rh <= 40 or rh >= 60 else (rh - 40) / 10 if rh <= 50 else (60 - rh) / 10
    def mu_high(self, rh): return 0 if rh <= 45 else 1 if rh >= 70 else (rh - 45) / 25
    def compute(self, rh):
        low, ok, high = self.mu_low(rh), self.mu_ok(rh), self.mu_high(rh)
        base = (low * 0.95 + ok * 0.45 + high * 0.05) / (low + ok + high + 1e-9)
        d = max(-0.08, min(0.08, (rh - self.last_rh) / 20))
        power = max(0, min(base - d, 1))
        self.last_rh = self.last_rh * 0.6 + rh * 0.4
        return power

# ---------- GUI ----------
class SmartClimateApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Climate – Dehumidifier / Humidifier")
        self.geometry("640x620")
        self.minsize(500, 550)
        self.configure(bg="#fff0f6")
        self.mode = tk.StringVar(value="dehumidifier")
        self.dehumid_ctrl = FuzzyDehumidifier()
        self.humid_ctrl = FuzzyHumidifier()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)   # stage row

        # Header + toggle
        hdr = tk.Frame(self, bg="#fff0f6")
        hdr.grid(row=0, column=0, pady=(10, 5))
        tk.Label(hdr, text="Smart Climate", font=("Segoe UI", 18, "bold"),
                 fg="#6b2b3d", bg="#fff0f6").pack()
        self.toggle_btn = ttk.Button(hdr, text="Switch to Humidifier", command=self.toggle_mode)
        self.toggle_btn.pack(pady=4)

        # Stage (canvas)
        stage = tk.Frame(self, bg="#ffeaf2", bd=1, relief="solid")
        stage.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        stage.columnconfigure(0, weight=1)
        stage.rowconfigure(1, weight=1, minsize=300)

        self.badge = tk.Label(stage, text="Room Humidity: 45%", font=("Segoe UI", 11),
                              fg="#6b2b3d", bg="#fff7fa", bd=1, relief="solid", padx=12, pady=4)
        self.badge.grid(row=0, column=0, pady=5)

        self.canvas = tk.Canvas(stage, bg="#ffeaf2", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        self.canvas.bind("<Configure>", self._on_resize)

        # Slider
        self.slider = ttk.Scale(self, from_=20, to=90, orient=tk.HORIZONTAL,
                                command=self.update_display, length=400)
        self.slider.set(45)
        self.slider.grid(row=2, column=0, sticky="ew", padx=40, pady=10)

        # Value label
        self.value_lbl = tk.Label(self, text="45%", fg="#6b2b3d", bg="#fff0f6", font=("Consolas", 12))
        self.value_lbl.grid(row=3, column=0)

        # Description
        self.desc_lbl = tk.Label(self, text="", font=("Segoe UI", 9), fg="#9b4b63",
                                 bg="#fff0f6", justify="center", wraplength=480)
        self.desc_lbl.grid(row=4, column=0, pady=(8, 15))

        self.angle = 0
        self._build_objects()
        self.update_display()
        self.after(50, self.animate)

    # ---------- MODE ----------
    def toggle_mode(self):
        self.mode.set("humidifier" if self.mode.get() == "dehumidifier" else "dehumidifier")
        self.toggle_btn.config(text="Switch to Dehumidifier" if self.mode.get() == "humidifier"
                               else "Switch to Humidifier")
        self.update_display()

    def _build_objects(self):
        cx, cy, r = 200, 200, 100
        # Fan
        self.fan_housing = self.canvas.create_oval(0, 0, 0, 0, fill="#ffd9e9", outline="#ffb4cf", width=6)
        self.fan_blades = [self.canvas.create_polygon(0, 0, 0, 0, 0, 0, 0, 0,
                                                      fill="#ffa7c7", outline="#ff6fa3") for _ in range(4)]
        self.fan_center = self.canvas.create_oval(0, 0, 0, 0, fill="#ff6fa3", outline="#ffb9d3", width=3)
        # Mist
        self.mist_lines = [self.canvas.create_line(0, 0, 0, 0, fill="#e6f0ff", width=2, state="hidden")
                           for _ in range(3)]

    def _on_resize(self, event):
        self.update_display()

    def update_display(self, _=None):
        rh = float(self.slider.get())
        power = (self.dehumid_ctrl.compute(rh) if self.mode.get() == "dehumidifier"
                 else self.humid_ctrl.compute(rh))

        self.badge.config(text=f"Room Humidity: {rh:.0f}%")
        self.value_lbl.config(text=f"{rh:.0f}%  |  Power: {power:.2f}")

        if self.mode.get() == "dehumidifier":
            self.desc_lbl.config(text="• IF humidity HIGH → strong drying\n"
                                      "• IF humidity COMFORTABLE → medium drying\n"
                                      "• IF humidity LOW → weak drying")
            self._draw_fan(power)
        else:
            self.desc_lbl.config(text="• Low humidity → more moisture\n"
                                      "• Near target → output tapers smoothly")
            self._draw_mist(power)

    def _draw_fan(self, power):
        for ln in self.mist_lines:
            self.canvas.itemconfigure(ln, state="hidden")
        for it in [self.fan_housing, self.fan_center] + self.fan_blades:
            self.canvas.itemconfigure(it, state="normal")

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 20
        self.canvas.coords(self.fan_housing, cx-r, cy-r, cx+r, cy+r)
        self.canvas.coords(self.fan_center, cx-18, cy-18, cx+18, cy+18)
        blade, inner = r * 0.85, r * 0.3
        off = math.radians(8)
        for idx, bl in enumerate(self.fan_blades):
            theta = math.radians(self.angle + idx*90)
            pts = [(cx + inner * math.cos(theta-off), cy + inner * math.sin(theta-off)),
                   (cx + blade * math.cos(theta-off), cy + blade * math.sin(theta-off)),
                   (cx + blade * math.cos(theta+off), cy + blade * math.sin(theta+off)),
                   (cx + inner * math.cos(theta+off), cy + inner * math.sin(theta+off))]
            flat = [c for pair in pts for c in pair]
            self.canvas.coords(bl, *flat)

    def _draw_mist(self, power):
        for it in [self.fan_housing, self.fan_center] + self.fan_blades:
            self.canvas.itemconfigure(it, state="hidden")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        base_y = cy + 55
        lengths, xs = [80, 60, 65], [cx, cx-15, cx+15]
        for ln, x, L in zip(self.mist_lines, xs, lengths):
            if power > 0.05:
                self.canvas.itemconfigure(ln, state="normal")
                self.canvas.coords(ln, x, base_y, x, base_y - L*power)
            else:
                self.canvas.itemconfigure(ln, state="hidden")

    def animate(self):
        if self.mode.get() == "dehumidifier":
            speed = 5 + self.dehumid_ctrl.compute(float(self.slider.get())) * 25
            self.angle = (self.angle + speed) % 360
            self.update_display()
        self.after(50, self.animate)

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    SmartClimateApp().run()