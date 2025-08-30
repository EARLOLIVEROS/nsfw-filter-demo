import numpy as np
import skfuzzy as fuzz
import tkinter as tk
from tkinter import ttk
import random
import math


# ----------------------------------------------------------
#  FUZZY ENGINE
# ----------------------------------------------------------
class FuzzyHumidityCtrl:
    def __init__(self, setpoint: float = 50.0):
        self.setpoint = setpoint

        # Error universe (difference from target humidity)
        self.error_universe = np.arange(-50, 51, 1)

        # Fuzzy sets for humidity error
        self.dry_mf  = fuzz.trapmf(self.error_universe, [-50, -50, -15, 0])
        self.ok_mf   = fuzz.trimf(self.error_universe, [-15, 0, 15])
        self.wet_mf  = fuzz.trapmf(self.error_universe, [0, 15, 50, 50])

        # Singleton outputs (Sugeno style)
        self.out_centers = [-100, 0, 100]

    def compute(self, current_humidity: float) -> float:
        """Return crisp action ∈ [-100, 100]"""
        error = current_humidity - self.setpoint   # negative → dry, positive → wet

        # Membership degrees
        dry_level = fuzz.interp_membership(self.error_universe, self.dry_mf, error)
        ok_level  = fuzz.interp_membership(self.error_universe, self.ok_mf,  error)
        wet_level = fuzz.interp_membership(self.error_universe, self.wet_mf, error)

        # Sugeno defuzzification (weighted average of singletons)
        numerator = (dry_level * -100) + (ok_level * 0) + (wet_level * 100)
        denominator = dry_level + ok_level + wet_level + 1e-6
        action = numerator / denominator

        return max(-100, min(100, action))  # clamp


# ----------------------------------------------------------
#  MIST PARTICLE CLASS
# ----------------------------------------------------------
class MistParticle:
    def __init__(self, x, y, vx, vy, size, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.canvas_id = None

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age += 1
        
        # Add some drift and size change
        self.vx *= 0.98  # friction
        self.vy *= 0.98
        self.vy -= 0.1   # slight upward movement
        
        return self.age < self.lifetime

    def get_alpha(self):
        return max(0, 1 - (self.age / self.lifetime))


# ----------------------------------------------------------
#  GUI
# ----------------------------------------------------------
class SmartHumidityGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Living Room Humidity Controller")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")

        self.ctrl = FuzzyHumidityCtrl(setpoint=50.0)
        self.mist_particles = []
        self.animation_running = True

        # Main layout
        self.setup_ui()
        self.draw_living_room()
        
        # Start animation
        self.animate()

    def setup_ui(self):
        # Left control panel
        left_frame = tk.Frame(self.root, bg="#34495e", padx=15, pady=15)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Title
        title_label = tk.Label(left_frame, text="Fuzzy Logic\nHumidity Control", 
                              font=("Arial", 16, "bold"), fg="#ecf0f1", bg="#34495e")
        title_label.pack(pady=(0, 20))

        # Current humidity slider
        tk.Label(left_frame, text="Current Humidity (%)", 
                font=("Arial", 10, "bold"), fg="#ecf0f1", bg="#34495e").pack()
        self.hum_scale = ttk.Scale(
            left_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self.update_display, length=200
        )
        self.hum_scale.set(40)
        self.hum_scale.pack(fill=tk.X, pady=5)

        # Current humidity display
        self.lbl_current = tk.Label(left_frame, text="40%", 
                                   font=("Arial", 12, "bold"), fg="#3498db", bg="#34495e")
        self.lbl_current.pack(pady=5)

        # Set-point slider
        tk.Label(left_frame, text="Target Humidity (%)", 
                font=("Arial", 10, "bold"), fg="#ecf0f1", bg="#34495e").pack(pady=(20, 0))
        self.target_scale = ttk.Scale(
            left_frame, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self.update_setpoint, length=200
        )
        self.target_scale.set(50)
        self.target_scale.pack(fill=tk.X, pady=5)

        # Target humidity display
        self.lbl_target = tk.Label(left_frame, text="50%", 
                                  font=("Arial", 12, "bold"), fg="#e74c3c", bg="#34495e")
        self.lbl_target.pack(pady=5)

        # Action display
        self.lbl_action = tk.Label(left_frame, text="Action: 0.0", 
                                  font=("Arial", 12, "bold"), fg="#f39c12", bg="#34495e")
        self.lbl_action.pack(pady=(20, 10))

        # Device status
        self.lbl_devices = tk.Label(left_frame, text="Both OFF", 
                                   font=("Arial", 10), fg="#95a5a6", bg="#34495e")
        self.lbl_devices.pack()

        # Canvas for living room
        canvas_frame = tk.Frame(self.root, bg="#2c3e50")
        canvas_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.canvas = tk.Canvas(canvas_frame, width=450, height=400, 
                               bg="#ecf0f1", highlightthickness=0)
        self.canvas.pack()

    def draw_living_room(self):
        # Room walls
        self.canvas.create_rectangle(20, 20, 430, 380, outline="#34495e", width=4, fill="#f8f9fa")
        
        # Floor
        self.canvas.create_rectangle(20, 320, 430, 380, fill="#8d6e63", outline="#5d4037", width=2)
        
        # Add some furniture
        # Sofa
        self.canvas.create_rectangle(50, 280, 150, 320, fill="#795548", outline="#5d4037", width=2)
        self.canvas.create_rectangle(40, 260, 160, 285, fill="#6d4c41", outline="#5d4037", width=2)
        
        # Coffee table
        self.canvas.create_rectangle(180, 290, 250, 320, fill="#a0855b", outline="#795548", width=2)
        
        # TV stand
        self.canvas.create_rectangle(350, 290, 420, 320, fill="#424242", outline="#212121", width=2)
        self.canvas.create_rectangle(360, 250, 410, 290, fill="#000000", outline="#424242", width=2)
        
        # Window
        self.canvas.create_rectangle(300, 30, 380, 120, fill="#87ceeb", outline="#4682b4", width=2)
        self.canvas.create_line(340, 30, 340, 120, fill="#4682b4", width=2)
        self.canvas.create_line(300, 75, 380, 75, fill="#4682b4", width=2)
        
        # Plant
        self.canvas.create_oval(380, 270, 410, 290, fill="#8bc34a", outline="#689f38", width=2)
        self.canvas.create_rectangle(390, 290, 400, 320, fill="#795548", outline="#5d4037", width=1)
        
        # Humidifier/Dehumidifier device (center of room)
        self.device_x, self.device_y = 225, 200
        self.device = self.canvas.create_oval(self.device_x - 25, self.device_y - 25, 
                                            self.device_x + 25, self.device_y + 25, 
                                            fill="#95a5a6", outline="#7f8c8d", width=3)
        
        # Device details
        self.canvas.create_oval(self.device_x - 15, self.device_y - 15, 
                               self.device_x + 15, self.device_y + 15, 
                               fill="#bdc3c7", outline="#95a5a6", width=2)
        
        # Power indicator (small circle)
        self.power_indicator = self.canvas.create_oval(self.device_x - 5, self.device_y - 5, 
                                                      self.device_x + 5, self.device_y + 5, 
                                                      fill="#95a5a6", outline="white", width=1)

    def create_mist_particles(self, device_type, power):
        """Create mist particles based on device type and power"""
        if power < 10:
            return
            
        num_particles = int(power / 10)  # More power = more particles
        
        for _ in range(num_particles):
            # Start from device center with some randomness
            x = self.device_x + random.uniform(-10, 10)
            y = self.device_y + random.uniform(-10, 10)
            
            if device_type == "humidifier":
                # Blue mist particles going upward and outward
                vx = random.uniform(-1, 1)
                vy = random.uniform(-3, -1)
                color = "#3498db"
                size = random.uniform(3, 8)
                lifetime = random.randint(50, 100)
            else:  # dehumidifier
                # Orange particles going downward (representing extracted moisture)
                vx = random.uniform(-0.5, 0.5)
                vy = random.uniform(0.5, 2)
                color = "#e67e22"
                size = random.uniform(2, 5)
                lifetime = random.randint(30, 60)
            
            particle = MistParticle(x, y, vx, vy, size, color, lifetime)
            self.mist_particles.append(particle)

    def update_particles(self):
        """Update and draw all mist particles"""
        active_particles = []
        
        for particle in self.mist_particles:
            if particle.update():
                alpha = particle.get_alpha()
                # Calculate color with alpha
                if particle.color == "#3498db":  # blue
                    intensity = int(255 * alpha)
                    color = f"#{52:02x}{152:02x}{219:02x}"
                else:  # orange
                    intensity = int(255 * alpha)
                    color = f"#{230:02x}{126:02x}{34:02x}"
                
                # Remove old particle from canvas
                if particle.canvas_id:
                    self.canvas.delete(particle.canvas_id)
                
                # Draw new particle
                size = particle.size * alpha
                if size > 0.5:
                    particle.canvas_id = self.canvas.create_oval(
                        particle.x - size/2, particle.y - size/2,
                        particle.x + size/2, particle.y + size/2,
                        fill=color, outline=""
                    )
                    active_particles.append(particle)
            else:
                # Remove expired particle
                if particle.canvas_id:
                    self.canvas.delete(particle.canvas_id)
        
        self.mist_particles = active_particles

    def update_setpoint(self, _):
        self.ctrl.setpoint = self.target_scale.get()
        self.lbl_target.config(text=f"{self.target_scale.get():.0f}%")
        self.update_display()

    def update_display(self, _=None):
        h = self.hum_scale.get()
        self.lbl_current.config(text=f"{h:.0f}%")
        
        action = self.ctrl.compute(h)

        # Update device visual and create particles
        if action < -10:
            device_type = "dehumidifier"
            power = abs(action)
            dev_text = f"Dehumidifier ON ({power:.0f}% power)"
            self.canvas.itemconfig(self.device, fill="#e67e22")  # orange
            self.canvas.itemconfig(self.power_indicator, fill="#d35400")  # dark orange
            self.create_mist_particles(device_type, power)
            
        elif action > 10:
            device_type = "humidifier"
            power = action
            dev_text = f"Humidifier ON ({power:.0f}% power)"
            self.canvas.itemconfig(self.device, fill="#3498db")  # blue
            self.canvas.itemconfig(self.power_indicator, fill="#2980b9")  # dark blue
            self.create_mist_particles(device_type, power)
            
        else:
            dev_text = "Both OFF"
            self.canvas.itemconfig(self.device, fill="#95a5a6")  # gray
            self.canvas.itemconfig(self.power_indicator, fill="#7f8c8d")  # dark gray

        self.lbl_action.config(text=f"Action: {action:+.1f}")
        self.lbl_devices.config(text=dev_text)

    def animate(self):
        """Main animation loop"""
        if self.animation_running:
            self.update_particles()
            self.root.after(50, self.animate)  # ~20 FPS

    def run(self):
        self.root.mainloop()
        self.animation_running = False


# ----------------------------------------------------------
if __name__ == "__main__":
    SmartHumidityGUI().run()