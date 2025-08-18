from gpiozero import OutputDevice, InputDevice
import time
import threading

from states import location_state


location = InputDevice(11)

stop_event = threading.Event()

def location_reading():
    try:
        while True:
            print('reading..')
            if location:
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
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

def locate(step, state):
    print('locate called')
    state['running'] = True
    while location:
        step.on()
        time.sleep(state['delay'])
        step.off()
        time.sleep(state['delay'])