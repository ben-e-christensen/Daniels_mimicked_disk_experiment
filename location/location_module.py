from gpiozero import OutputDevice, DigitalInputDevice
from states import location_state
import time

location = DigitalInputDevice(11, pull_up=False)
flag = False

# looks to see if the inductor is over screw on start up
if location.is_active:
    location_state['last_reading'] = True

def locator():
    while True:
        if location.is_active:
            if location_state['pin_count'] != 1 and not location_state['last_reading']:
                location_state['pin_count'] += 1
                if location_state['flag'] == False:
                    location_state['flag'] = True
                    print('Recording...')
                print('pin found!')
            elif not location_state['last_reading']:
                location_state['tracked_revs'] += 1
                location_state['pin_count'] = 0
                print(f"Rev Clocked. Total Revs: {location_state['tracked_revs']}")
            location_state['last_reading'] = True
        else:
            location_state['last_reading'] = False
        time.sleep(0.05)

