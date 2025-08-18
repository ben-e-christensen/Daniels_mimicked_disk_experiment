from gpiozero import OutputDevice, DigitalInputDevice
import time
import threading
from states import location_state, motor_state, accelerator_state
import tkinter as tk

stop_event = threading.Event()
stop_event = threading.Event()


step = OutputDevice(2)
direction = OutputDevice(3)
location = None
direction.on()

# initiates the gpio pin to inductor probe
def init_location():
    global location
    location = DigitalInputDevice(11, pull_up=False)
    print("GPIO 11 ready")

# closes pin between runs
def close_location():
    global location
    if location is not None:
        location.close()
        location = None
        print("GPIO 11 released")
    
stop_event = threading.Event()

def motor_control():
    if motor_state['running'] == True:
        return
    start_time = time.time()
    motor_state['running'] = True
    accel = True if motor_state['target_rpm'] - motor_state['rpm'] > 0 else False

    while not stop_event.is_set():
        step.on()
        time.sleep(motor_state['delay'])
        step.off()
        time.sleep(motor_state['delay'])

        if abs(motor_state['target_rpm'] - motor_state['rpm']) <= accelerator_state['increment']:
            motor_state['rpm'] = motor_state['target_rpm']
            motor_state['delay'] = motor_state['root_delay'] / motor_state['rpm']
            break
        else:
            if accel:
                motor_state['rpm'] += accelerator_state['increment']
            else:
                motor_state['rpm'] -= accelerator_state['increment']

            motor_state['delay'] = motor_state['root_delay'] / motor_state['rpm']


    while not stop_event.is_set():
        step.on()
        time.sleep(motor_state['delay'])
        step.off()
        time.sleep(motor_state['delay'])
    print(motor_state['rpm'])
    motor_state['running'] = False
    elapsed = time.time() - start_time
    print("Loop duration:", elapsed, "seconds")

def start_motor(start_button):
    # go to origin
    # accelerate 
    start_button.config(state="disabled")
    stop_event.clear()
    thread = threading.Thread(target=motor_control, daemon=True)
    thread.start()

def stop_motor(start_button):
    stop_event.set()
    close_location()
    motor_state['rpm'] = 3
    start_button.config(state="normal")


def location_reading():
    init_location()
    while not stop_event.is_set():
        if location.is_active:
            if location_state['pin_count'] != 1 and not location_state['last_reading']:
                location_state['pin_count'] += 1
                print('pin found!')
            elif not location_state['last_reading']:
                location_state['tracked_revs'] += 1
                location_state['pin_count'] = 0
                print(f"Rev Clocked. Total Revs: {location_state['tracked_revs']}")
            location_state['last_reading'] = True
        else:
            location_state['last_reading'] = False
        time.sleep(0.01)



def locate():
    try:
        location = DigitalInputDevice(11, pull_up=False)
        motor_state['running'] = True
        steps = -1
        flag = False
        while not stop_event.is_set():
            step.on();  time.sleep(motor_state['root_delay']/3)
            step.off(); time.sleep(motor_state['root_delay']/3)

            # READ THE PIN CORRECTLY
            if location.is_active:
                steps += 1
                flag = True
            elif (not location.is_active) and flag:
                # passed the mark → go back halfway
                direction.off()
                for _ in range(int(steps/2)):
                    step.on();  time.sleep(motor_state['root_delay']/3)
                    step.off(); time.sleep(motor_state['root_delay']/3)
                direction.on()
                stop_event.set()   # request exit
                break
    finally:
        direction.on()
        motor_state['running'] = False
        try:
            location.close()
        except Exception:
            pass

def find_origin():
    if motor_state['running']:
        return
    stop_event.clear()
    threading.Thread(target=locate, daemon=True).start()




    
    
    

