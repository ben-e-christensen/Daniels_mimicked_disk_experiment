import threading
import time
import os
import signal
import sys
from states import file_state, location_state, motor_info_state

# --- Import the 'live' versions of your modules ---
# (You will need to create/adapt these files)
from camera.camera_module import start_camera_loop
from BLE.client.ble_plotter import run_ble_in_thread
from location.location_module import locator
from location.motor_info_server import run_motor_info_server

# --- This stop_event is the single source of truth for shutdown ---
stop_event = threading.Event()

def shutdown_handler(signum, frame):
    """Gracefully handle shutdown signals (like Ctrl+C)."""
    if not stop_event.is_set():
        print("\nShutdown signal received. Stopping all threads...")
        stop_event.set()
    # Give threads a moment to react before exiting.
    time.sleep(0.5)
    sys.exit(0)

# Register the shutdown handler for standard termination signals
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


def handle_ints_from_motor_server(ints):
    """Placeholder for handling messages from the motor info server."""
    # This function is required by run_motor_info_server
    print(f"-> Received from motor server: {ints}")


def main():
    """Main entry point for the headless 'live' data acquisition application."""
    print("--- Starting Live Data Acquisition ---")

    # --- Setup Save Directory ---
    today = time.strftime("%Y-%m-%d_%H_%M", time.localtime())
    save_dir = f"{file_state['BASE_DIR']}/{today}"
    os.makedirs(save_dir, exist_ok=True)
    file_state['CURRENT_DIR'] = save_dir
    print(f"Data will be saved in: {save_dir}")

    # --- Define Threads ---
    # Note: Ensure all your target functions are updated to accept a `stop_event`
    
    # 1. Camera Thread
    camera_thread = threading.Thread(
        target=start_camera_loop,
        daemon=True
    )

    # 2. BLE Thread 
    csv_path = os.path.join(file_state['CURRENT_DIR'], "ble_samples.csv")
    ble_thread = threading.Thread(
        target=run_ble_in_thread,
        args=(csv_path, stop_event),
        daemon=True
    )

    # 3. Locator Thread
    locator_thread = threading.Thread(
        target=locator,
        daemon=True
    )

    # 4. Motor Info Server Thread
    motor_server_thread = threading.Thread(
        target=run_motor_info_server,
        args=(stop_event,),
        kwargs={"on_message": handle_ints_from_motor_server, "period": 0.5},
        daemon=True
    )

    # --- Start All Threads ---
    print("Starting all threads...")
    camera_thread.start()
    ble_thread.start()
    locator_thread.start()
    motor_server_thread.start()

    print("\n--- All systems running. Press Ctrl+C to stop. ---")
    
    # Keep the main thread alive to listen for the shutdown signal.
    # The shutdown_handler will catch Ctrl+C and exit the script.
    while not stop_event.is_set():
        time.sleep(1)

if __name__ == '__main__':
    main()
