#helpers.py
import tkinter as tk
import os
import re
import time
# Directory to save captured frames
today = time.strftime("%Y-%m-%d_%H:%M", time.localtime())


def calc_spin(freq, revs, state, result_label, freq_tk, total_revs_tk):
    steps_per_rev = 25600
    steps_per_sec = float(freq) / 60 * steps_per_rev
    delay_seconds = 1.0 / (steps_per_sec * 2.0)
    steps = float(revs) * steps_per_rev
    state['delay'] = delay_seconds
    state['total_steps'] = int(steps)
    
    update_ui(state, result_label)
    update_tkinter_input_box(freq_tk, freq)
    update_tkinter_input_box(total_revs_tk, revs)

    
def update_ui(state, result_label):
    result_label.config(text=f"Delay (us): {state['delay'] * 10e5:.0f} u_sec\nSteps: {state['total_steps']}\nTotal Time: {state['delay'] * 2 * state['total_steps']:.1f} sec")
    
def update_tkinter_input_box(input_box, val):
    input_box.delete(0, tk.END)
    if isinstance(val, float):
        val = round(val,3)
    input_box.insert(0, val)

def get_next_session_folder(base_dir):
    os.makedirs(base_dir, exist_ok=True)

    existing = [
        name for name in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, name)) and re.match(r"session\d+", name)
    ]

    # Extract numbers from session folder names
    indices = [int(re.findall(r"\d+", name)[0]) for name in existing]
    next_index = max(indices, default=0) + 1

    folder_name = f"session{next_index}_{today}"
    full_path = os.path.join(base_dir, folder_name)

    # Make folders: datasets/sessionX/ and datasets/sessionX/images/
    os.makedirs(os.path.join(full_path, "images"), exist_ok=True)

    return full_path, next_index



