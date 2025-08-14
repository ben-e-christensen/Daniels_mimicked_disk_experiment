# main.py
import threading
from pulse_sender import run_pulse_sender
from ble_receiver import run_ble_receiver

def start_all():
    sender_thread = threading.Thread(target=run_pulse_sender, daemon=True)
    ble_thread = threading.Thread(target=run_ble_receiver, daemon=True)

    sender_thread.start()
    ble_thread.start()

    print("[Main] Threads started. Ctrl+C to exit.")
    try:
        while True:
            pass  # or do other stuff
    except KeyboardInterrupt:
        print("\n[Main] Shutting down…")

if __name__ == "__main__":
    start_all()
