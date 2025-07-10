import tkinter as tk


from motor_controls import adjust_speed, reverse_direction, start_motor, stop_motor
from helpers import calc_spin, update_tkinter_input_box

# steps per revolution of the motor
# this setting is manually set on the driver
spr = 25600
revs = 3

state = {
    'delay': 0.0025,
    'total_steps': spr * revs
    }

def handle_enter(event=None):
    calc_spin(freq.get(), total_revs.get(), state, result_label, freq, total_revs)

# Tkinter UI
root = tk.Tk()
root.title("Motor Control")

# initial speed up/slow down increment value
inc_val = tk.StringVar(value="0.1")
# Variable to store the state of the Checkbutton
checkbox_val = tk.IntVar() 

result_label = tk.Label(root, text=f"Delay (us): {state['delay'] * 10e5:.0f} u_sec\nSteps: {int(state['total_steps'])}\nTotal Time: {state['delay'] * 2 * state['total_steps']:.1f} sec")

start_button = tk.Button(root, text="Start Motor", command=lambda: start_motor(state, checkbox_val))
start_button.pack(padx=20, pady=20)

stop_button = tk.Button(root, text="Stop Motor", command=stop_motor)
stop_button.pack(padx=20, pady=20)

reverse_button = tk.Button(root, text="Reverse", command=reverse_direction)
reverse_button.pack(padx=20, pady=20)

speed_up_button = tk.Button(root, text="Speed Up", command=lambda: adjust_speed(state, 'u', result_label, inc_val, revs, freq, total_revs))
speed_up_button.pack(padx=20, pady=20)

slow_down_button = tk.Button(root, text="Slow Down", command=lambda: adjust_speed(state, 'd', result_label, inc_val, revs, freq, total_revs))
slow_down_button.pack(padx=20, pady=20)

inc_label = tk.Label(root, text="Incremental value for speed adjustments (in revs per minute)")
inc_label.pack(padx=10, pady=10)
inc = tk.Spinbox(root, from_=0, to=10, increment=0.1, textvariable=inc_val)
inc.pack(padx=10, pady=10)

freq_label = tk.Label(root, text="Enter frequency (in revolutions per minute):")
freq_label.pack(pady=10)

freq = tk.Entry(root, width=30) # You can set the width in characters
freq.pack(pady=5)

revs_label = tk.Label(root, text="Enter total revolutions:")
revs_label.pack(pady=10)

total_revs = tk.Entry(root, width=30) 
total_revs.pack(pady=5)

update_tkinter_input_box(freq, 30)
update_tkinter_input_box(total_revs, revs)

checkbox = tk.Checkbutton(root, text="Run motor until stopped", variable=checkbox_val, onvalue=1, offvalue=0)
checkbox.pack(pady=5)


# Create a Button to trigger input retrieval
button = tk.Button(root, text="Get Input", command=lambda: calc_spin(freq.get(), total_revs.get(), state, result_label, freq, total_revs))
button.pack(pady=10)

result_label.pack(pady=10)

root.bind("<Return>", handle_enter)     # Main Enter key
root.bind("<KP_Enter>", handle_enter)   # Numpad Enter key
root.mainloop()
