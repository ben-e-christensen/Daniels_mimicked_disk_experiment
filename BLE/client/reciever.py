#!/usr/bin/env python3
# ble_receiver.py — subscribe to ESP32 notify packets and (optionally) log CSV
#
# Packet format (20 bytes): 10 x uint16 LE
#   [A0_0..A0_4, A1_0..A1_4]  (each 0..4095 if 12-bit ADC)
#
# Usage examples:
#   python3 ble_receiver.py
#   python3 ble_receiver.py --name ESP32-Analog-100Hz --csv samples.csv
#   python3 ble_receiver.py --address 12:34:56:78:9A:BC

import argparse, asyncio, csv, signal, struct, sys, time, os
from datetime import datetime
from bleak import BleakClient, BleakScanner, BleakError

DEFAULT_NAME = "ESP32-Analog-100Hz"  # set this to your NAME in main.py
CHAR_UUID = "c0de1000-0000-4a6f-9e00-000000000001"
PACK = struct.Struct("<10H")  # 10 unsigned 16-bit, little-endian

# Global stop flag (you can mirror this from a higher-level stop_event in a thread)
stop_flag = False
def _sigint(_sig, _frm):
    global stop_flag
    stop_flag = True
signal.signal(signal.SIGINT, _sigint)

async def find_device(name: str | None, address: str | None, timeout: float = 8.0):
    if address:
        # Fast-path: return a dummy object with the given address
        class D: pass
        d = D()
        d.address = address
        d.name = "(address-specified)"
        return d
    print(f"[i] Scanning for {name!r} …")
    devs = await BleakScanner.discover(timeout=timeout)
    target = next((d for d in devs if d.name == name), None)
    if not target:
        print("[!] Device not found.")
    else:
        print(f"[✓] Found: {target.address} ({target.name})")
    return target

async def run(name: str, address: str | None, csv_path: str | None):
    """Core BLE receive loop. If csv_path is provided, logs each packet line-by-line."""
    # ---- CSV setup (optional) ----
    csv_file = None
    csv_writer = None
    if csv_path:
        # Ensure parent directory exists (handles absolute or relative paths)
        os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
        # Line-buffered so each row is written immediately
        csv_file = open(csv_path, "w", newline="", buffering=1)
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "iso_time", "epoch_s",
            "a0_0","a0_1","a0_2","a0_3","a0_4",
            "a1_0","a1_1","a1_2","a1_3","a1_4"
        ])
        print(f"[i] Logging to {csv_path}")

    # ---- Resolve device ----
    device = await find_device(name if not address else None, address)
    if not device:
        if csv_file:
            csv_file.close()
        return

    # ---- Notification callback ----
    async def on_notify(_handle, data: bytearray):
        now = time.time()
        try:
            vals = PACK.unpack(data)
        except struct.error:
            print(f"[!] Bad packet length: {len(data)}")
            return

        a0 = vals[:5]
        a1 = vals[5:]

        # Light console print; safe at ~100 Hz
        print(f"{now:.3f}  A0:{list(a0)}  A1:{list(a1)}")

        if csv_writer:
            csv_writer.writerow([
                datetime.utcfromtimestamp(now).isoformat(),
                f"{now:.6f}",
                *a0, *a1
            ])
            # extra safety: ensure the line is on disk even in threads or odd FS
            csv_file.flush()

    # ---- Connect / subscribe / loop until stopped ----
    while not stop_flag:
        try:
            print(f"[i] Connecting to {device.address} …")
            async with BleakClient(device.address, timeout=10.0) as client:
                print("[✓] Connected. Subscribing …")
                await client.start_notify(CHAR_UUID, on_notify)

                while not stop_flag and client.is_connected:
                    await asyncio.sleep(0.1)

                print("[i] Stopping notify …")
                try:
                    await client.stop_notify(CHAR_UUID)
                except Exception:
                    pass

        except BleakError as e:
            print(f"[!] BLE error: {e}")
        except Exception as e:
            print(f"[!] Error: {e}")

        if stop_flag:
            break

        print("[i] Disconnected. Reconnecting in 2s …")
        await asyncio.sleep(2.0)

    if csv_file:
        csv_file.close()
        print("[i] CSV closed.")

def main():
    ap = argparse.ArgumentParser(description="ESP32 BLE receiver")
    ap.add_argument("--name", default=DEFAULT_NAME, help="Advertised device name to find")
    ap.add_argument("--address", default=None, help="BLE MAC address (skips scanning by name)")
    ap.add_argument("--csv", default=None, help="Optional CSV output path")
    args = ap.parse_args()
    asyncio.run(run(args.name, args.address, args.csv))

if __name__ == "__main__":
    main()
