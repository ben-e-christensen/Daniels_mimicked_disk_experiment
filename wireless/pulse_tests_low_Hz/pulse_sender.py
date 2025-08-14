# pulse_sender.py
import time
import random
import csv
from datetime import datetime
from gpiozero import OutputDevice

PINS = [23, 24, 25]
devices = {pin: OutputDevice(pin, active_high=True, initial_value=False) for pin in PINS}
LOG_FILE = "gpio_pulses.csv"

def run_pulse_sender():
    # Create file with header if not present
    try:
        with open(LOG_FILE, "x", newline="") as f:
            csv.writer(f).writerow(["timestamp", "pin", "start_ms", "duration_ms"])
    except FileExistsError:
        pass

    print("[PulseSender] Sending random GPIO pulses. Ctrl+C to stop.")
    try:
        while True:
            pin = random.choice(PINS)
            dur = round(random.uniform(0.1, 2.0), 4)
            t_start = int(time.monotonic() * 1000)  # milliseconds
            t_dur = int(dur * 1000)

            devices[pin].on()
            time.sleep(dur)
            devices[pin].off()

            with open(LOG_FILE, "a", newline="") as f:
                csv.writer(f).writerow([
                    datetime.now().isoformat(timespec="seconds"),
                    pin,
                    t_start,
                    t_dur
                ])

            time.sleep(random.uniform(0.05, 0.5))
    except KeyboardInterrupt:
        print("\n[PulseSender] Stopped by user.")
    finally:
        for dev in devices.values():
            dev.close()
        print("[PulseSender] GPIOs cleaned up.")

if __name__ == "__main__":
    run_pulse_sender()
