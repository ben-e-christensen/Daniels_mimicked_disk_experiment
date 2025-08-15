# ble_receiver.py
import asyncio
from bleak import BleakScanner, BleakClient
from datetime import datetime
import csv
import os

DEVICE_NAME = "Seeed_BLE"
CHAR_UUID = "abcdefab-1234-5678-1234-abcdefabcdef"
LOG_FILE = "ble_readings.csv"

async def main():
    print("[BLEReceiver] Scanning for Xiao…")
    device = None
    for _ in range(3):
        for d in await BleakScanner.discover(timeout=5):
            if d.name == DEVICE_NAME:
                device = d
                print(f"[BLEReceiver] Found: {d.address}")
                break
        if device: break

    if not device:
        print("❌ Xiao not found. Is it powered + advertising?")
        return

    # Create CSV file if needed
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["host_timestamp", "channel", "time_ms", "voltage"])

    async with BleakClient(device) as client:
        print("[BLEReceiver] Connected.")

        def handle(_, data: bytearray):
            try:
                ts = datetime.now().isoformat(timespec="milliseconds")
                line = data.decode().strip()
                entries = line.split(";")
                with open(LOG_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    for entry in entries:
                        if not entry: continue
                        ch, t_ms, v = entry.split(",")
                        writer.writerow([ts, ch, int(t_ms), float(v)])
                        print(f"[BLEReceiver] {ts}  {ch} {v} V at {t_ms} ms")
            except Exception as e:
                print("❌ Parse error:", e)

        await client.start_notify(CHAR_UUID, handle)
        print("[BLEReceiver] Listening… Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await client.stop_notify(CHAR_UUID)
            print("[BLEReceiver] Stopped.")

if __name__ == "__main__":
    asyncio.run(main())
