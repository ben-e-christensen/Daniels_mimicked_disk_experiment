import tkinter as tk
from gpiozero import OutputDevice
from time import sleep, time
import threading

# Setup GPIO pins using gpiozero
step = OutputDevice(2)
direction = OutputDevice(3)

direction.on()




# Stepper parameters
spr = 400     # steps per revolution
revs = 3
total_steps = spr * revs
delay = 0.0025  # seconds (2500 microseconds)

def motor_control():

    start_time = time()

    for _ in range(total_steps):
        step.on()
        sleep(delay)
        step.off()
        sleep(delay)

    elapsed = time() - start_time
    print("Loop duration:", elapsed, "seconds")
    
def reverse_direction():
    print("reversing!")
    direction.value = not direction.value
    

def start_motor():
    thread = threading.Thread(target=motor_control)
    thread.start()
    
def get_input():
    """Function to retrieve text from the entry box."""
    frequency = freq.get()

    revs = total_revs.get()

    calc_spin(frequency, revs)

    print("get_input running")
    print(f"User entered: {frequency}, {revs}")

def calc_spin(freq, revs):
    if float(freq) <= 0:
        print("Frequency must be greater than zero.")
        return

    steps_per_rev = 400.0  # typical for many stepper motors
    steps_per_sec = float(freq) * steps_per_rev
    delay_seconds = 1.0 / (steps_per_sec * 2.0)
    delay_microseconds = float(delay_seconds * 1_000_000)

    total_steps = float(revs) * steps_per_rev

    print(f"Steps/sec: {steps_per_sec}")
    print(f"Delay (us): {delay_microseconds}")
    print(f"Total steps: {total_steps}")

    return delay_microseconds, total_steps

# Tkinter UI
root = tk.Tk()
root.title("Motor Control")

start_button = tk.Button(root, text="Start Motor", command=start_motor)
start_button.pack(padx=20, pady=20)

reverse_button = tk.Button(root, text="Reverse", command=reverse_direction)
reverse_button.pack(padx=20, pady=20)

freq_label = tk.Label(root, text="Enter frequency (in revolutions per second):")
freq_label.pack(pady=10)

freq = tk.Entry(root, width=30) # You can set the width in characters
freq.pack(pady=5)

revs_label = tk.Label(root, text="Enter total revolutions:")
revs_label.pack(pady=10)

total_revs = tk.Entry(root, width=30) 
total_revs.pack(pady=5)

# Create a Button to trigger input retrieval
button = tk.Button(root, text="Get Input", command=get_input)
button.pack(pady=10)


root.mainloop()
