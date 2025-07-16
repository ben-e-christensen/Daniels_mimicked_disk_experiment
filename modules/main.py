import threading
from gui_module import run_gui
from voltmeter_module import start_voltmeter_loop
from camera_module import start_camera_loop

if __name__ == '__main__':
    threading.Thread(target=start_voltmeter_loop, daemon=True).start()
    threading.Thread(target=start_camera_loop, daemon=True).start()
    run_gui()