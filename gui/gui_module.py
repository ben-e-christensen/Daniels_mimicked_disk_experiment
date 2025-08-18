# gui_and_controls.py
import threading
import tkinter as tk
from PIL import Image, ImageTk

from motor.motor_controls import stop_motor, find_origin
from motor.main import run
from helpers import calc_spin

from states import motor_state
from camera.camera_module import start_camera_loop  # <-- import the camera thread entrypoint

# ----- Tk setup -----
root = tk.Tk()
root.title("Motor Control & Angle Tracker")
root.lift(); root.attributes("-topmost", True); root.after(100, lambda: root.attributes("-topmost", False))

angle_var = tk.StringVar(value="Angle: --")
current_image = None

start_button = tk.Button(root, text="Start")
find_button  = tk.Button(root, text="Go to Origin", command=find_origin)
stop_button  = tk.Button(root, text="Stop", command=lambda: stop_motor(start_button))

rpm_label = tk.Label(root, text="Enter revolutions per minute:")
rpm = tk.Entry(root)
rpm.insert(0, motor_state["rpm"])

duration_label = tk.Label(root, text="Enter time in minutes:")
duration = tk.Entry(root)
duration.insert(0, "5")

angle_label = tk.Label(root, textvariable=angle_var)
video_label = tk.Label(root)  # where frames will be displayed

for w in [start_button, stop_button, find_button, duration_label, duration, rpm_label, rpm, angle_label, video_label]:
    w.pack(pady=5, padx=10)

def run_button_clicked():
    motor_state["duration"] = float(duration.get()) * 60
    motor_state["rpm"] = int(rpm.get())
    motor_state["delay"] = motor_state["root_delay"] / motor_state["rpm"]
    threading.Thread(target=run, args=(start_button,), daemon=True).start()

start_button.config(command=run_button_clicked)

# ----- Safe-updaters (must run on Tk main thread) -----
def _update_video_on_tk(frame_rgb):
    """frame_rgb: numpy array RGB (H,W,3)"""
    global current_image
    pil_img = Image.fromarray(frame_rgb)
    current_image = ImageTk.PhotoImage(pil_img)
    video_label.config(image=current_image)
    video_label.image = current_image  # prevent GC

def _update_angle_on_tk(a):
    angle_var.set(f"Angle: {a:.1f}°")

# ----- Callbacks provided to the camera thread -----
def on_frame(frame_rgb):
    # Schedule the actual widget update on the Tk thread
    root.after(0, _update_video_on_tk, frame_rgb)

def on_angle(a):
    root.after(0, _update_angle_on_tk, a)

# ----- Start/stop camera thread -----
stop_cam = threading.Event()

def start_camera_thread():
    threading.Thread(
        target=start_camera_loop,
        args=(on_frame, on_angle, stop_cam),
        kwargs={"save_frames": False},  # set True if you want saving behavior
        daemon=True
    ).start()

def on_close():
    stop_cam.set()
    root.after(100, root.destroy)

root.protocol("WM_DELETE_WINDOW", on_close)

# Kick it off
start_camera_thread()

def run_gui():
    root.mainloop()

if __name__ == "__main__":
    run_gui()
