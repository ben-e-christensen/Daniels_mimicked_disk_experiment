# state.py
from threading import Lock

motor_state = {
    'delay': 0.0025,
    'spr': 6400,
    'revs': 3,
    'total_steps': 25600 * 3,
    'running': False,
}

shared_state = {
    "voltage": None
}

file_state = {
    "BASE_DIR": "/home/ben/Documents/disk_experiment",
    "CURRENT_DIR": "",
    "index": -1
}

blob_state = {
    "area": None,
    "center": [0,0],
    "angle": None
}

state_lock = Lock()
