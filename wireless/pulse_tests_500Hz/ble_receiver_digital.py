import asyncio, os, csv
from datetime import datetime
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "Seeed_BLE"
CHAR_UUID   = "abcdefab-1234-5678-1234-abcdefabcdef"
LOG_FILE    = "ble_digital.csv"

def host_time_only():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

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

    # CSV header
    if not os.path.exists(LOG_FILE):
      with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(["host_time", "xiao_time_ms", "channel", "state"])

    async with BleakClient(dev) as client:
      print("[BLE Rx] Connected.")

      def handle(_, data: bytearray):
        line = data.decode(errors="ignore").strip()
        # entries like: "123456,A0,HIGH,A1,LOW;123458,A0,LOW,A1,LOW;..."
        packets = [e for e in line.split(";") if e]
        host_ts = host_time_only()

        with open(LOG_FILE, "a", newline="") as f:
          w = csv.writer(f)
          for p in packets:
            parts = p.split(",")
            # Expect exactly 5 tokens: t_ms, "A0", state, "A1", state
            if len(parts) != 5:
              continue
            try:
              t_ms = int(parts[0])
              a0_state = parts[2].upper()
              a1_state = parts[4].upper()
            except:
              continue

            # Write one row per pin for simplicity
            w.writerow([host_ts, t_ms, "A0", a0_state])
            w.writerow([host_ts, t_ms, "A1", a1_state])

            print(f"[BLE Rx] {host_ts}  t={t_ms}  A0={a0_state}  A1={a1_state}")

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
