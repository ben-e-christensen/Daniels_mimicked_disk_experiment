import os
import sys
from app import run_flask_viewer  # We'll set this up below

BASE_DIR = "/home/ben/Documents/disk_experiment/"

def list_sessions(base_dir):
    sessions = []
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path) and \
           os.path.exists(os.path.join(path, "readings.csv")) and \
           os.path.isdir(os.path.join(path, "images")):
            sessions.append(name)
    return sessions

def main():
    sessions = list_sessions(BASE_DIR)

    if not sessions:
        print("No valid sessions found.")
        sys.exit(1)

    print("Available datasets:\n")
    for i, name in enumerate(sessions):
        print(f"{i}: {name}")
    
    index = input("\nSelect a dataset index to view: ")
    try:
        selected = sessions[int(index)]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)

    selected_path = os.path.join(BASE_DIR, selected)
    csv_path = os.path.join(selected_path, "readings.csv")
    image_path = os.path.join(selected_path, "images")

    print(f"\nLaunching viewer for: {selected}")
    run_flask_viewer(csv_path, image_path)

# ✅ This prevents input() from running again on Flask’s debug-mode reload
if __name__ == "__main__":
    main()

