# pulse_sender_digital.py
# Drives GPIO23 (A0) and GPIO24 (A1) independently at ~500 Hz.
# Logs: time_only, pin_bcm, channel_label, state(HIGH/LOW)

import time
import csv
import random
from datetime import datetime
from gpiozero import OutputDevice

# --- Config ---
PIN_MAP = {23: "A0", 24: "A1"}     # Pi BCM -> label expected by Xiao wiring
TICK_SEC = 0.002                   # 500 Hz (adjust as needed)
LOG_FILE = "sent_digital.csv"

# --- Setup ---
devices = {pin: OutputDevice(pin, active_high=True, initial_value=False) for pin in PIN_MAP}

# Create CSV w/ header if new
try:
    with open(LOG_FILE, "x", newline="") as f:
        csv.writer(f).writerow(["time", "pin_bcm", "channel", "state"])
except FileExistsError:
    pass

def now_time_only():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

def run():
    print("[PulseSenderDigital] 500 Hz digital toggles on GPIO23 (A0) & GPIO24 (A1). Ctrl+C to stop.")
    next_t = time.perf_counter()
    try:
        while True:
            # Decide states independently (both may be HIGH, both LOW, or mixed)
            states = {pin: bool(random.getrandbits(1)) for pin in PIN_MAP}

            # Apply to pins
            for pin, state in states.items():
                devices[pin].value = state

            # Log one row per pin (time, pin, A0/A1, HIGH/LOW)
            ts = now_time_only()
            with open(LOG_FILE, "a", newline="") as f:
                w = csv.writer(f)
                for pin, state in states.items():
                    w.writerow([ts, pin, PIN_MAP[pin], "HIGH" if state else "LOW"])

            # pace loop to ~500 Hz
            next_t += TICK_SEC
            sleep_for = next_t - time.perf_counter()
            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                # if we fell behind, catch up next tick
                next_t = time.perf_counter()
    except KeyboardInterrupt:
        print("\n[PulseSenderDigital] Stopping.")
    finally:
        for dev in devices.values():
            dev.close()
        print("[PulseSenderDigital] GPIOs cleaned up.")

if __name__ == "__main__":
    run()
