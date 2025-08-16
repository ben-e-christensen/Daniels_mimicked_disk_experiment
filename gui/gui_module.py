import tkinter as tk
from PIL import Image, ImageTk
from motor.motor_module import start_motor, stop_motor
from helpers import calc_spin

from states import motor_state


def handle_enter(event=None):
    calc_spin(motor_state)

root = tk.Tk()
root.title("Motor Control & Angle Tracker")
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False))

# GUI state vars
angle_var = voltage_var = current_image = angle_label = voltage_label = video_label = None

start_button = tk.Button(root, text="Start Motor", command=lambda: start_motor(motor_state))

stop_button = tk.Button(root, text="Stop Motor", command=stop_motor)

rpm_label = tk.Label(root, text="Enter revolutions per minute:")
rpm = tk.Entry(root)
rpm.insert(0, "1")

duration_label = tk.Label(root, text="Enter time in minutes:")
duration = tk.Entry(root)
duration.insert(0, "5")



for w in [start_button, stop_button, duration_label, duration, rpm_label, rpm]:
    w.pack(pady=5)
    w.pack(padx=10)

root.bind("<Return>", handle_enter)
root.bind("<KP_Enter>", handle_enter)

# def update_angle(angle_text):
#     angle_var.set(angle_text)

# def update_video(pil_img):
#     global current_image
#     current_image = ImageTk.PhotoImage(pil_img)
    #video_label.config(image=current_image)
    #video_label.image = current_image 


def run_gui():
    root.mainloop()

if __name__ == "__main__":
    run_gui()
