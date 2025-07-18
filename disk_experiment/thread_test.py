import subprocess
import atexit
import signal
import os
import sys

# Launch subprocesses with their own process groups
p1 = subprocess.Popen(["python3", "voltmeter.py"], preexec_fn=os.setsid)
p2 = subprocess.Popen(["python3", "gui_and_camera.py"], preexec_fn=os.setsid)

def cleanup():
    print("\n[Cleanup] Terminating subprocesses...")
    for p in [p1, p2]:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except Exception as e:
            print(f"Failed to kill process {p.pid}: {e}")

atexit.register(cleanup)

# Optional: catch Ctrl+C as well
def sigint_handler(sig, frame):
    print("\n[Ctrl+C] Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# Keep the main script alive
p1.wait()
p2.wait()
