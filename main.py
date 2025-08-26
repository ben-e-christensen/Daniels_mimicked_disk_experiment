import threading
from gui.gui_module import run_gui
from camera.camera_module import start_camera_loop
import atexit



def main():
    try:       
        print("Starting camera thread...")
        threading.Thread(target=start_camera_loop, daemon=True).start()
        run_gui()

if __name__ == '__main__':
    main()
