# ble_receiver.py
import asyncio
from bleak import BleakScanner, BleakClient
from datetime import datetime
import os

DEVICE_NAME = "Seeed_BLE"
CHAR_UUID = "abcdefab-1234-5678-1234-abcdefabcdef"
LOG_FILE = "ble_pulses.csv"

async def main():
    print("[BLEReceiver] Scanning for BLE device…")
    device = None
    for _ in range(3):
        devices = await BleakScanner.discover(timeout=5)
        for d in devices:
            if d.name == DEVICE_NAME:
                device = d
                print(f"[BLEReceiver] Found: {d.address}")
                break
        if device: break
    if not device:
        print("[BLEReceiver] Xiao not found.")
        return

    # Create CSV with header if needed
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("host_timestamp_iso,pin,start_ms,duration_ms\n")

    async with BleakClient(device) as client:
        print("[BLEReceiver] Connected.")

        def handle(_, data: bytearray):
            msg = data.decode().strip()
            ts = datetime.now().isoformat(timespec="seconds")
            print(f"[BLEReceiver] {ts}  {msg}")
            with open(LOG_FILE, "a") as f:
                f.write(f"{ts},{msg}\n")

        await client.start_notify(CHAR_UUID, handle)
        print("[BLEReceiver] Listening… Ctrl+C to exit.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await client.stop_notify(CHAR_UUID)
            print("[BLEReceiver] Stopped.")

def run_ble_receiver():
    asyncio.run(main())

if __name__ == "__main__":
    run_ble_receiver()
