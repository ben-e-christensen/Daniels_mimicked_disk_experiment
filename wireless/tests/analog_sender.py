# analog_sender.py

import serial
import time
import random

SERIAL_PORT = "/dev/ttyACM0"  # Adjust as needed
BAUD_RATE = 115200
FREQ_HZ = 30  # Adjustable frequency (30 Hz = 1 reading every ~33 ms)

def run_analog_sender():
    interval = 60 / FREQ_HZ
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"[AnalogSender] Sending at {FREQ_HZ} Hz...")
        while True:
            channel = random.choice(["A", "B"])
            voltage = round(random.uniform(0.5, 3.3), 3)
            ser.write(f"{channel},{voltage}\n".encode())
            print(f"[AnalogSender] Sent: {channel} = {voltage:.3f} V")
            time.sleep(interval)

if __name__ == "__main__":
    run_analog_sender()
