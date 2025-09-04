import cv2
import numpy as np
from picamera2 import Picamera2
import time
import os
import threading
import queue
from datetime import datetime
from states import file_state, blob_state, location_state
from gpiozero import InputDevice

# --- Configuration ---
# This script is designed for maximum performance with no GUI.
# It uses a producer-consumer model with two main threads:
# 1. Acquisition Thread: Captures frames, calculates data, and puts frames on a queue.
# 2. Save Worker Thread: Pulls frames from the queue and saves them to disk.

running_signal = InputDevice(16)

# --- Global Shared State & Threading Primitives ---
save_queue = queue.Queue(maxsize=120) # Buffer for ~2 seconds of frames at 60fps
stop_event = threading.Event()

# --- Directory Setup ---
today = time.strftime("%Y-%m-%d_%H_%M", time.localtime())
save_dir_base = f"{file_state['BASE_DIR']}/{today}"
os.makedirs(save_dir_base, exist_ok=True)
file_state['CURRENT_DIR'] = save_dir_base

image_save_dir = f"{file_state['CURRENT_DIR']}/images"
os.makedirs(image_save_dir, exist_ok=True)

# --- Image Processing Utilities ---
def create_circular_mask(h, w):
    """Creates a circular mask for a given height and width."""
    center = (w // 2, h // 2)
    radius = min(center[0], center[1], w - center[0], h - center[1])
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    return mask

def smooth_angle(new_angle, history, N=10):
    """Smooths an angle value over the last N readings."""
    history.append(new_angle)
    if len(history) > N:
        history.pop(0)
    return sum(history) / len(history)

# --- Thread 1: Lean Data Acquisition (Producer) ---
def data_acquisition_loop(picam2, roi, circular_mask, stop_event_flag):
    """
    Captures frames, calculates blob data, and queues frames for saving.
    This is the lean, high-speed producer thread.
    """
    x, y, w, h = roi
    angle_history = []
    frame_counter = -1
    
    print("LIVE MODE: Data acquisition thread started.")
    while not stop_event_flag.is_set():
        loop_start_time = time.time()

        full_frame = picam2.capture_array()
        roi_frame = full_frame[y:y + h, x:x + w]

        # Perform image analysis to get blob data
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        masked = cv2.bitwise_and(blurred, blurred, mask=circular_mask)
        _, binary = cv2.threshold(masked, 125, 75, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            blob_state['area'] = cv2.contourArea(largest_contour)
            
            if len(largest_contour) >= 5:
                ellipse = cv2.fitEllipse(largest_contour)
                if ellipse[1][0] > 0 and ellipse[1][1] > 0:
                    smoothed_angle = smooth_angle(ellipse[2], angle_history)
                    blob_state['angle'] = smoothed_angle
        
        # If recording is active, put the frame on the queue to be saved
        if running_signal.is_active and location_state['flag']:
            frame_counter += 1
            now = datetime.now()
            # Convert frame to BGR once, just before queueing
            frame_bgr = cv2.cvtColor(full_frame, cv2.COLOR_RGB2BGR)
            try:
                save_queue.put_nowait((frame_counter, now, frame_bgr))
            except queue.Full:
                # This should rarely happen with a large queue, but it prevents a crash.
                print("Warning: Save queue is full. A frame was dropped.")


        # Rate-limit the loop to the target FPS
        elapsed_time = time.time() - loop_start_time
        sleep_duration = max(0, (1/60) - elapsed_time)
        time.sleep(sleep_duration)
    
    print("Data acquisition thread finished.")

# --- Thread 2: Asynchronous Save Worker (Consumer) ---
def save_worker(save_path, stop_event_flag):
    """A dedicated thread that pulls frames from a queue and saves them to disk."""
    print("LIVE MODE: Save worker thread started.")
    while not stop_event_flag.is_set() or not save_queue.empty():
        try:
            frame_count, timestamp, frame_bgr = save_queue.get(timeout=1)
            formatted_time = timestamp.strftime("%Y-%m-%d_%H-%M-%S") + f"_{timestamp.microsecond // 1000:03d}"
            img_name = f"frame_{frame_count:04d}_{formatted_time}.jpg"
            filename = os.path.join(save_path, img_name)
            cv2.imwrite(filename, frame_bgr)
            save_queue.task_done()
        except queue.Empty:
            continue
    print("Save worker thread finished.")

# --- Main Application Logic ---
def start_camera_loop():
    """Initializes and runs the high-speed, no-GUI camera loop."""
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": (1280, 720), "format": "RGB888"},
        controls={"FrameRate": 60, "AnalogueGain": 8.0, "ExposureTime": 10000}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(1)

    print("--- Live Mode Initializing ---")
    print("Please select the ROI on the pop-up window.")
    frame = picam2.capture_array()
    roi = cv2.selectROI("Select Top of Drum for LIVE MODE", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select Top of Drum for LIVE MODE")
    if not any(roi):
        print("No ROI selected. Exiting.")
        picam2.stop()
        return
        
    x, y, w, h = roi
    circular_mask = create_circular_mask(h, w)

    # --- Create and Start All Threads ---
    acquisition_thread = threading.Thread(
        target=data_acquisition_loop, 
        args=(picam2, roi, circular_mask, stop_event)
    )
    save_thread = threading.Thread(
        target=save_worker,
        args=(image_save_dir, stop_event)
    )
    
    acquisition_thread.start()
    save_thread.start()

    try:
        # The main thread just waits for the acquisition thread to finish or for an interrupt.
        acquisition_thread.join()
    except KeyboardInterrupt:
        print("\nShutdown signal received. Stopping threads...")
    finally:
        # --- Graceful Shutdown ---
        stop_event.set()
        # Acquisition thread is already joined, now wait for the save worker.
        save_thread.join()
        picam2.stop()
        print("Live application has been shut down cleanly.")

if __name__ == '__main__':
    # This allows the script to be run directly from the command line
    start_camera_loop()