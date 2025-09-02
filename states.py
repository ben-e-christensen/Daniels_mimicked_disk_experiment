# state.py
from threading import Lock
spr = 6400
root_delay = 30 / spr


motor_state = {
    'root_delay': root_delay,
    'delay': root_delay,
    'rpm': 1,
    'running': False,
    'duration': 300,
    'target_rpm': 1,
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
    "BASE_DIR": "/media/ben/A0B4-33AC/disk_experiment",
    "CURRENT_DIR": "",
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
}