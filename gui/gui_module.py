import tkinter as tk
from tkinter import TclError
from PIL import Image, ImageTk
from motor.motor_controls import stop_motor, find_origin
from motor.main import run
from helpers import calc_spin
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
from queue import Queue
import cv2

# Import the shared queues and stop_event from the BLE module
from BLE.test_client.ble_plotter import data_queue_a0, data_queue_a1, stop_event

from states import motor_state

# --- PLOTTING Globals ---
data_buffer_a0 = []
data_buffer_a1 = []
time_buffer = []
buffer_size = 500  # Number of data points to display

# --- VIDEO Globals ---
video_queue = Queue()
video_label = None
tk_img = None # A global reference to prevent garbage collection
DISPLAY_W, DISPLAY_H = 480, 480

# --- Matplotlib and Tkinter Setup ---
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
fig.suptitle("Live Data Stream from BLE Device", fontsize=16)

# First subplot (A0 data)
ax[0].set_title("Analog Channel 0")
ax[0].set_xlabel("Data Point Index")
ax[0].set_ylabel("Sensor Value")
ax[0].grid(True)
line_a0, = ax[0].plot([], [], 'r-')

# Second subplot (A1 data)
ax[1].set_title("Analog Channel 1")
ax[1].set_xlabel("Data Point Index")
ax[1].set_ylabel("Sensor Value")
ax[1].grid(True)
line_a1, = ax[1].plot([], [], color='#87CEEB')

def update_plot():
    """
    Checks the queues for new data and updates both Matplotlib plots.
    """
    new_data_count = 0
    while not data_queue_a0.empty() and not data_queue_a1.empty():
        data_point_a0 = data_queue_a0.get()
        data_point_a1 = data_queue_a1.get()
        
        data_buffer_a0.append(data_point_a0)
        data_buffer_a1.append(data_point_a1)
        time_buffer.append(len(time_buffer))
        new_data_count += 1

    if new_data_count > 0:
        if len(data_buffer_a0) > buffer_size:
            data_buffer_a0[:] = data_buffer_a0[-buffer_size:]
            data_buffer_a1[:] = data_buffer_a1[-buffer_size:]
            time_buffer[:] = list(range(len(data_buffer_a0)))

        line_a0.set_xdata(time_buffer)
        line_a0.set_ydata(data_buffer_a0)
        line_a1.set_xdata(time_buffer)
        line_a1.set_ydata(data_buffer_a1)

        ax[0].set_xlim(0, buffer_size)
        ax[1].set_xlim(0, buffer_size)
        if data_buffer_a0:
            ax[0].set_ylim(min(data_buffer_a0) - 50, max(data_buffer_a0) + 50)
            ax[1].set_ylim(min(data_buffer_a1) - 50, max(data_buffer_a1) + 50)
        
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        canvas.draw_idle()

    root.after(50, update_plot)

def update_video():
    """Checks the video queue and updates the video label with a new frame (resized)."""
    global tk_img
    if not video_queue.empty():
        pil_img = None
        # Drain queue so we always show the most recent frame
        while not video_queue.empty():
            pil_img = video_queue.get_nowait()

        if pil_img is not None:
            # Resize to fixed dimensions
            pil_img = pil_img.resize((DISPLAY_W, DISPLAY_H), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img, master=video_label)
            video_label.configure(image=tk_img)
            video_label.image = tk_img  # keep ref

    root.after(15, update_video)


def handle_enter(event=None):
    run_button_clicked()

def run_button_clicked():
    motor_state['duration'] = float(duration.get()) * 60
    motor_state['rpm'] = int(rpm.get())
    motor_state['delay'] = motor_state['root_delay'] / motor_state['rpm']
    threading.Thread(target=run, args=(start_button,), daemon=True).start()
    
# Function to get ROI and then start camera loop
def run_camera_roi_selection():
    from camera.camera_module import start_camera_loop, picam2 # Import here to avoid circular dependencies
    
    # Temporarily start the camera to get a frame for ROI selection
    picam2.start()
    time.sleep(1)
    frame = picam2.capture_array()
    
    # Blocking GUI call in the main thread
    roi = cv2.selectROI("Select Top of Drum", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select Top of Drum")
    
    # Store ROI in a shared state or a shared queue if needed
    x, y, w, h = roi
    
    # Now start the camera thread with the selected ROI
    threading.Thread(target=start_camera_loop, args=(stop_event, video_queue, x, y, w, h), daemon=True).start()
    
    # Stop the camera from the main thread
    picam2.stop()

# Main control window
root = tk.Tk()
root.title("Motor Controls")
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False))

# Data display window
data_window = tk.Toplevel(root)
data_window.title("Live Data & Camera Feed")
data_window.protocol("WM_DELETE_WINDOW", root.destroy) # Close both windows

# GUI widgets for main window
start_button = tk.Button(root, text="Start Motor", command=run_button_clicked)
find_button = tk.Button(root, text="Go to Origin", command=find_origin)
stop_button = tk.Button(root, text="Stop Motor", command=lambda: stop_motor(start_button))
camera_button = tk.Button(root, text="Select Camera ROI", command=run_camera_roi_selection)

rpm_label = tk.Label(root, text="Enter revolutions per minute:")
rpm = tk.Entry(root)
rpm.insert(0, motor_state['rpm'])

duration_label = tk.Label(root, text="Enter time in minutes:")
duration = tk.Entry(root)
duration.insert(0, "5")

for w in [start_button, stop_button, find_button, camera_button, duration_label, duration, rpm_label, rpm]:
    w.pack(pady=5)
    w.pack(padx=10)

# Widgets for the data window
canvas = FigureCanvasTkAgg(fig, master=data_window)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

video_label = tk.Label(data_window)
video_label.pack()

def run_gui():
    root.after(50, update_plot)
    root.after(15, update_video)
    root.mainloop()

if __name__ == "__main__":
    run_gui()