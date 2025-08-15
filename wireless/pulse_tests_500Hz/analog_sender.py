# analog_sender.py
# here the pi sends data to the pico as to what to transmit to the xiao

import time
import random
import csv
import serial
from datetime import datetime

SERIAL_PORT = "/dev/ttyACM0"  # adjust if different
BAUD_RATE = 115200
LOG_FILE = "sent_analog.csv"
CHANNELS = ["A", "B"]
SEND_INTERVAL = 0.002  # 2 ms (500 Hz)

def normalize(voltage):
    """Clamp and normalize voltage to 0.0–1.0 range (assuming 3.3V max)"""
    return max(0.0, min(1.0, voltage / 3.3))

def run_analog_sender():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    print("[AnalogSender] Connected to Pico.")

    # Initialize log file
    try:
        with open(LOG_FILE, "x", newline="") as f:
            csv.writer(f).writerow(["timestamp", "channel", "voltage", "norm", "send_ms"])
    except FileExistsError:
        pass

    last_channel = None
    start_time = time.monotonic()

    try:
        while True:
            # Choose a different channel than last time
            channel = random.choice([c for c in CHANNELS if c != last_channel])
            last_channel = channel

            # Choose voltage (fixed or random)
            voltage = round(random.uniform(0.5, 2.8), 3)  # keep it in reasonable range
            norm = round(normalize(voltage), 4)

            # Build and send command
            cmd = f"{channel} {norm:.4f}\n"
            ser.write(cmd.encode())

            # Log with timestamp
            now = datetime.now().isoformat(timespec="milliseconds")
            send_ms = int((time.monotonic() - start_time) * 1000)

            with open(LOG_FILE, "a", newline="") as f:
                csv.writer(f).writerow([now, channel, voltage, norm, send_ms])

            # Debug print
            print(f"[AnalogSender] Sent: {cmd.strip()} @ {now}")

            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        print("\n[AnalogSender] Stopped.")
    finally:
        ser.close()

if __name__ == "__main__":
    run_analog_sender()
