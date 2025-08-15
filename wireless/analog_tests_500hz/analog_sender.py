# analog_sender.py
import time, csv, random
import serial
from datetime import datetime

SERIAL_PORT = "/dev/ttyUSB0"   # Huzzah usually shows as /dev/ttyUSB0 (adjust if needed)
BAUD = 115200
RATE_HZ = 0.5                   # start slow; increase later
V_MIN, V_MAX = 0.2, 3.0        # safe-ish range for DAC output

LOG_FILE = "sent_analog.csv"

def host_time():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

def run():
    # init CSV
    try:
        with open(LOG_FILE, "x", newline="") as f:
            csv.writer(f).writerow(["host_time", "channel", "voltage", "send_ms"])
    except FileExistsError:
        pass

    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
    print(f"[Sender] Connected to {SERIAL_PORT}. Rate={RATE_HZ} Hz")
    interval = 1.0 / RATE_HZ
    t0 = time.monotonic()
    last_ch = None

    try:
        while True:
            ch = random.choice([c for c in ("A","B") if c != last_ch])
            last_ch = ch
            v = round(random.uniform(V_MIN, V_MAX), 3)
            cmd = f"{ch} {v:.3f}\n".encode()
            ser.write(cmd)
            now_ms = int((time.monotonic() - t0) * 1000)

            with open(LOG_FILE, "a", newline="") as f:
                csv.writer(f).writerow([host_time(), ch, v, now_ms])

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[Sender] Stopped.")
    finally:
        ser.close()

if __name__ == "__main__":
    run()
