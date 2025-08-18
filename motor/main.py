from motor.motor_controls import start_motor, stop_motor, location_reading
import time
import threading
from states import location_state, motor_state

stop_event = threading.Event()

def run(start_button):
    # reset state each run if needed
    location_state.update(pin_count=0, tracked_revs=0, last_reading=False)

    stop_event.clear()

    loc_thread = threading.Thread(target=location_reading, daemon=True)
    loc_thread.start()

    start_motor(start_button)
    time.sleep(motor_state['duration'])
    stop_motor(start_button)

    loc_thread.join(timeout=2)
    print("Experiment finished. Total revs:", location_state['tracked_revs'])
