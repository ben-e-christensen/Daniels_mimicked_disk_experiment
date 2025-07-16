import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Motor Control & Angle Tracker")

# GUI state vars
angle_var = tk.StringVar(value="Angle: --")
voltage_var = tk.StringVar(value="Voltage: --")
current_image = None  # To avoid GC of image

# Widgets
angle_label = tk.Label(root, textvariable=angle_var, font=("Helvetica", 14), fg="blue")
voltage_label = tk.Label(root, textvariable=voltage_var, font=("Helvetica", 12), fg="green")
video_label = tk.Label(root)

# Pack them
angle_label.pack(pady=5)
voltage_label.pack(pady=5)
video_label.pack(pady=5)


def update_angle(angle_text):
    angle_var.set(angle_text)

def update_voltage(voltage_text):
    voltage_var.set(voltage_text)

def update_video(pil_img):
    global current_image
    current_image = ImageTk.PhotoImage(pil_img)
    video_label.config(image=current_image)

def run_gui():
    root.mainloop()