# state.py
from threading import Lock
from datetime import datetime
spr = 6400
root_delay = 30 / spr

BASE_DIR ="//media/ben/Extreme SSD/disk_experiment/"
now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.") 

motor_state = {
    'root_delay': root_delay,
    'delay': root_delay,
    'rpm': 3,
    'running': False,
    'duration': 300,
    'target_rpm': 3,
    'at_max_speed': False
}

accelerator_state = {
    'adjust_period': 0.1,
    'increment': 0.0025,
    'running': True,
    'tolerance': 0.1
}

shared_state = {
    "voltage": None
}

file_state = {

    "CURRENT_DIR": BASE_DIR + now,
    "index": -1
}

blob_state = {
    "area": None,
    "center": [0,0],
    "angle": None
}

state_lock = Lock()

location_state = {
    'pin_count': 0,
    'tracked_revs': 0,
    'last_reading': False,
    'angle_coordinate': 0
}