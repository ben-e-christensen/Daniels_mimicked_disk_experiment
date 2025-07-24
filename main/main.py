import threading
from modules.gui_module import run_gui
from modules.voltmeter_module import start_voltmeter_loop
from modules.camera_module import start_camera_loop
import atexit
from helpers import html_generator
from states import file_state

def on_exit():
    print('on_exit running')
    try:
        html_generator(file_state['CURRENT_DIR'], file_state['index'])
    except Exception as e:
        print("Error in on_exit:", e)


def main():
    try:
        print("Starting voltmeter thread...")
        threading.Thread(target=start_voltmeter_loop, daemon=True).start()

        print("Starting camera thread...")
        threading.Thread(target=start_camera_loop, daemon=True).start()

        run_gui()
    except KeyboardInterrupt:
        print("\nInterrupted! Cleaning up...")
        on_exit()


if __name__ == '__main__':
    main()

atexit.register(on_exit)
