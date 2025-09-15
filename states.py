# state.py
from threading import Lock

motor_info_state = {
    'delay': 30/6400,
    'spr': 6400,
    'angles_per_step': 360 / 6400
}


file_state = {
    "BASE_DIR": "/media/ben/Extreme SSD/disk_experiment",
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
    'flag': False,
    'pin_count': 0,
    'tracked_revs': 0,
    'last_reading': False,
    'a0_angle': 0,
    'a1_angle': 0,
}