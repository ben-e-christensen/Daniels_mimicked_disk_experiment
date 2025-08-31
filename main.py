# main.py (relevant bits)
import threading, time, os, signal, sys, atexit
from states import file_state
from gui.gui_module import run_gui
from camera.camera_module import start_camera_loop
from BLE.client.receiver_thread import start_ble_in_thread

today = time.strftime("%Y-%m-%d_%H_%M", time.localtime())
save_dir = f"{file_state['BASE_DIR']}/{today}"
os.makedirs(save_dir, exist_ok=True)
file_state['CURRENT_DIR'] = save_dir

stop_event = threading.Event()

def _shutdown(*_):
    stop_event.set()
    time.sleep(0.2)
    sys.exit(0)

signal.signal(signal.SIGINT, _shutdown)
signal.signal(signal.SIGTERM, _shutdown)
atexit.register(_shutdown)

def main():
    print("Starting camera thread...")
    threading.Thread(target=start_camera_loop, args=(stop_event,), daemon=True).start()

    print("Starting BLE thread...")
    csv_path = os.path.join(file_state['CURRENT_DIR'], "ble_samples.csv")
    # If you know the MAC, set address="AA:BB:CC:DD:EE:FF" to skip scanning
    start_ble_in_thread(stop_event,
                        name="ESP32-Analog-100Hz",
                        address=None,
                        csv_path=csv_path)

    run_gui()  # keep GUI on main thread

if __name__ == '__main__':
    main()
