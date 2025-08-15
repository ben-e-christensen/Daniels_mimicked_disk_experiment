# ble_receiver.py
import asyncio, os, csv
from datetime import datetime
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "Seeed_BLE"
CHAR_UUID   = "abcdefab-1234-5678-1234-abcdefabcdef"
LOG_FILE    = "ble_readings.csv"

def host_time():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

async def main():
    print("[BLE Rx] Scanning for Xiao…")
    dev = None
    for _ in range(3):
        for d in await BleakScanner.discover(timeout=5):
            if d.name == DEVICE_NAME:
                dev = d
                print(f"[BLE Rx] Found: {d.address}")
                break
        if dev: break
    if not dev:
        print("[BLE Rx] Xiao not found.")
        return

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["host_time","xiao_time_ms","channel","voltage"])

    async with BleakClient(dev) as client:
        print("[BLE Rx] Connected.")

        def handle(_, data: bytearray):
            line = data.decode(errors="ignore").strip()
            # entries like: "t,A0,1.234,A1,0.567; t,A0,1.210,A1,0.580; ..."
            entries = [e for e in line.split(";") if e]
            host_ts = host_time()
            with open(LOG_FILE, "a", newline="") as f:
                w = csv.writer(f)
                for entry in entries:
                    parts = entry.split(",")
                    if len(parts) != 5:
                        continue
                    try:
                        t_ms = int(parts[0])
                        # parts[1] == "A0", parts[3] == "A1"
                        v0 = float(parts[2])
                        v1 = float(parts[4])
                    except:
                        continue
                    w.writerow([host_ts, t_ms, "A0", v0])
                    w.writerow([host_ts, t_ms, "A1", v1])
                    print(f"[BLE Rx] {host_ts}  t={t_ms}  A0={v0:.3f}  A1={v1:.3f}")

        await client.start_notify(CHAR_UUID, handle)
        print("[BLE Rx] Listening… Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await client.stop_notify(CHAR_UUID)
            print("[BLE Rx] Stopped.")

if __name__ == "__main__":
    asyncio.run(main())
