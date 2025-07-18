import tkinter as tk
import threading
import cv2
import numpy as np
from picamera2 import Picamera2
import time
from PIL import Image, ImageTk

from motor_controls import adjust_speed, reverse_direction, start_motor, stop_motor
from helpers import calc_spin, update_tkinter_input_box

# === Motor Control Setup ===
spr = 25600
revs = 3
state = {
    'delay': 0.0025,
    'total_steps': spr * revs
}

def handle_enter(event=None):
    calc_spin(freq.get(), total_revs.get(), state, result_label, freq, total_revs)

# === GUI Setup ===
root = tk.Tk()
root.title("Motor Control & Angle Tracker")

# Input variables
inc_val = tk.StringVar(value="0.1")
checkbox_val = tk.IntVar()
angle_var = tk.StringVar(value="Angle: --")

# Widgets
result_label = tk.Label(root, text=f"Delay (us): {state['delay'] * 10e5:.0f} u_sec\nSteps: {int(state['total_steps'])}\nTotal Time: {state['delay'] * 2 * state['total_steps']:.1f} sec")
angle_label = tk.Label(root, textvariable=angle_var, font=("Helvetica", 14), fg="blue")

start_button = tk.Button(root, text="Start Motor", command=lambda: start_motor(state, checkbox_val))
stop_button = tk.Button(root, text="Stop Motor", command=stop_motor)
reverse_button = tk.Button(root, text="Reverse", command=reverse_direction)
speed_up_button = tk.Button(root, text="Speed Up", command=lambda: adjust_speed(state, 'u', result_label, inc_val, revs, freq, total_revs))
slow_down_button = tk.Button(root, text="Slow Down", command=lambda: adjust_speed(state, 'd', result_label, inc_val, revs, freq, total_revs))

inc_label = tk.Label(root, text="Incremental value for speed adjustments (in revs per minute)")
inc = tk.Spinbox(root, from_=0, to=10, increment=0.1, textvariable=inc_val)

freq_label = tk.Label(root, text="Enter frequency (in revolutions per minute):")
freq = tk.Entry(root, width=30)
revs_label = tk.Label(root, text="Enter total revolutions:")
total_revs = tk.Entry(root, width=30)

update_tkinter_input_box(freq, 30)
update_tkinter_input_box(total_revs, revs)

checkbox = tk.Checkbutton(root, text="Run motor until stopped", variable=checkbox_val, onvalue=1, offvalue=0)
input_button = tk.Button(root, text="Get Input", command=handle_enter)

# Image panel for video
video_label = tk.Label(root)
video_label.pack(pady=5)

# Pack other widgets
for w in [start_button, stop_button, reverse_button, speed_up_button, slow_down_button,
          inc_label, inc, freq_label, freq, revs_label, total_revs,
          checkbox, input_button, result_label, angle_label]:
    w.pack(pady=5)

root.bind("<Return>", handle_enter)
root.bind("<KP_Enter>", handle_enter)

# === Angle Tracking + Live Feed ===
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()
time.sleep(1)

frame = picam2.capture_array()
roi = cv2.selectROI("Select Top of Drum", frame, False, False)
cv2.destroyWindow("Select Top of Drum")
x, y, w, h = roi
angle_history = []

def smooth_angle(new_angle, history, N=10):
    history.append(new_angle)
    if len(history) > N:
        history.pop(0)
    return sum(history) / len(history)

def update_frame():
    frame = picam2.capture_array()
    roi_frame = frame[y:y+h, x:x+w]

    # Preprocess
    gray = cv2.cvtColor(roi_frame, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 80, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    display_frame = roi_frame.copy()
    largest = None

    for cnt in contours:
        if cv2.contourArea(cnt) > 1000 and len(cnt) > 5:
            if largest is None or cv2.contourArea(cnt) > cv2.contourArea(largest):
                largest = cnt

    if largest is not None:
        ellipse = cv2.fitEllipse(largest)
        cv2.ellipse(display_frame, ellipse, (0, 255, 0), 2)
        angle = ellipse[2]
        smoothed = smooth_angle(angle, angle_history)
        angle_var.set(f"Angle: {smoothed:.1f} deg")

    # Convert to ImageTk
    img = Image.fromarray(display_frame)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    root.after(100, update_frame)


# Start periodic video update
update_frame()

# Start GUI loop
root.mainloop()

