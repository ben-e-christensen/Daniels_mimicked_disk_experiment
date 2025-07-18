import csv
import os
from datetime import datetime
import time
from helpers import get_next_session_folder
from states import file_state
# Directory to save captured frames

file_state['CURRENT_DIR'], file_state['index'] = get_next_session_folder(file_state['BASE_DIR'])

today = time.strftime("%Y-%m-%d_%H:%M", time.localtime())
print("file_state['CURRENT_DIR'] =", file_state['CURRENT_DIR'])

log_path = f"{file_state['CURRENT_DIR']}/readings.csv"

# Create file and write headers if it doesn't exist
if not os.path.exists(log_path):
    with open(log_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Voltage (V)', 'Angle (deg)', 'Frame'])

def log_data(voltage=None, angle=None, img=None):
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 10000:03d}"
    with open(log_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([formatted_time, voltage, angle, img])
