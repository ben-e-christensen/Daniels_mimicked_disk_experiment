# ble/ble_thread.py
import threading, asyncio, time
import os
from states import file_state

# IMPORTANT: import in the MAIN thread so the signal.signal call in your script
# doesn't raise "ValueError: signal only works in main thread".
import BLE.client.reciever as br  # adjust import path if file is elsewhere

csv_path = os.path.join(file_state['CURRENT_DIR'], "ble_samples.csv")

def _forward_stop(stop_event):
    """Mirror your app's stop_event into the module's global stop_flag."""
    while not stop_event.is_set():
        time.sleep(0.1)
    br.stop_flag = True

def _runner(name, address, csv_path):
    """Run the original async entrypoint exactly like your script's main()."""
    asyncio.run(br.run(name, address, csv_path))

def start_ble_in_thread(stop_event,
                        name=br.DEFAULT_NAME,
                        address=None,
                        csv_path=None):
    """
    Start your existing ble_receiver in a background daemon thread.
    Returns the Thread object.
    """
    # watcher flips br.stop_flag when your app requests shutdown
    threading.Thread(target=_forward_stop, args=(stop_event,), daemon=True).start()

    t = threading.Thread(target=_runner, args=(name, address, csv_path), daemon=True)
    t.start()
    return t
