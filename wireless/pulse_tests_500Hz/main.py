# main.py

import threading
from analog_sender import run_analog_sender
from ble_receiver import main as run_ble_receiver_async
import asyncio

def run_ble_receiver():
    asyncio.run(run_ble_receiver_async())

def main():
    sender_thread = threading.Thread(target=run_analog_sender, daemon=True)
    ble_thread = threading.Thread(target=run_ble_receiver, daemon=True)

    print("[Main] Starting analog sender and BLE receiver threads...")
    sender_thread.start()
    ble_thread.start()

    try:
        while True:
            pass  # keep main thread alive
    except KeyboardInterrupt:
        print("\n[Main] Ctrl+C detected — shutting down.")
        # Threads will stop automatically since they're daemonized

if __name__ == "__main__":
    main()
