from gpiozero import OutputDevice
from time import sleep, time
import threading

stop_event = threading.Event()

step = OutputDevice(2)
direction = OutputDevice(3)
direction.on()

def calc_spin(freq, revs, state):
    steps_per_rev = state['spr']
    steps_per_sec = float(freq) / 60 * steps_per_rev
    delay_seconds = 1.0 / (steps_per_sec * 2.0)
    steps = float(revs) * steps_per_rev
    state['delay'] = delay_seconds
    state['total_steps'] = int(steps)
    


def motor_control(state, run_time):
    start_time = time()
    state['running'] = True
    if(run_time):
        while True:
            if stop_event.is_set():
                state['running'] = False
                print("Motor stopped.")
                break
            step.on()
            sleep(state['delay'])
            step.off()
            sleep(state['delay'])
    else: 
        for _ in range(state['total_steps']):
            if stop_event.is_set():
                state['running'] = False
                print("Motor stopped.")
                break
            step.on()
            sleep(state['delay'])
            step.off()
            sleep(state['delay'])
            
    elapsed = time() - start_time
    print("Loop duration:", elapsed, "seconds")
    
def start_motor(state):
    stop_event.clear()
    thread = threading.Thread(target=motor_control, args=(state, True))
    thread.start()

def stop_motor():
    stop_event.set()
    
    
    