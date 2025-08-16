# pi_ble_simple.py
# Subscribes to one characteristic (20 bytes/notify), logs to CSV and prints rows.
# CSV: seq,t_host_us,a0_0..a0_4,a1_0..a1_4

import asyncio, csv, time, signal, sys
from pathlib import Path
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "c0de0001-0000-4a6f-9e00-000000000001"
CHAR_UUID    = "c0de1000-0000-4a6f-9e00-000000000001"
TARGET_NAME  = "XiaoC3-Analog-100Hz"

seq = 0
csv_file = None
csv_writer = None
stop_event = asyncio.Event()

def make_csv():
    p = Path(f"ble_samples_{time.strftime('%Y%m%d_%H%M%S')}.csv")
    f = p.open("w", newline="")
    w = csv.writer(f)
    w.writerow(["seq","t_host_us"] + [f"a0_{i}" for i in range(5)] + [f"a1_{i}" for i in range(5)])
    f.flush()
    return f, w, p

def on_notify(_sender, data: bytearray):
    # Expect exactly 20 bytes: 10 x uint16 LE
    if len(data) != 20:
        return
    global seq
    # unpack without struct to keep it simple/fast
    vals = [data[i] | (data[i+1] << 8) for i in range(0, 20, 2)]
    a0 = vals[0:5]
    a1 = vals[5:10]
    t_us = time.monotonic_ns() // 1000  # host timestamp
    row = [seq, t_us] + a0 + a1
    csv_writer.writerow(row)
    csv_file.flush()
    print(",".join(str(x) for x in row))
    sys.stdout.flush()
    seq += 1

async def find_device():
    devs = await BleakScanner.discover(timeout=5.0)
    for d in devs:
        if d.name == TARGET_NAME:
            return d
    # fallback by advertised UUID
    for d in devs:
        for u in (getattr(d, "metadata", {}) or {}).get("uuids", []) or []:
            if u.lower() == SERVICE_UUID.lower():
                return d
    return None

async def main():
    global csv_file, csv_writer
    csv_file, csv_writer, path = make_csv()
    print(f"# Writing to {path}")

    dev = await find_device()
    if not dev:
        print("Device not found. Is it advertising as XiaoC3-Analog-100Hz?", file=sys.stderr)
        return

    print(f"# Connecting to {dev.address} ({dev.name}) ...")
    async with BleakClient(dev) as client:
        await client.start_notify(CHAR_UUID, on_notify)
        print("# Subscribed. Streaming... Ctrl+C to stop.")
        await stop_event.wait()
        try:
            await client.stop_notify(CHAR_UUID)
        except Exception:
            pass

def _sigint(*_):
    stop_event.set()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, _sigint)
    try:
        asyncio.run(main())
    finally:
        try:
            if csv_file and not csv_file.closed:
                csv_file.close()
        except Exception:
            pass
