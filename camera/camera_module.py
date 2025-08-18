# camera_feed.py
import os, time
from datetime import datetime
import threading

import cv2
import numpy as np
from picamera2 import Picamera2

from states import motor_state, file_state, blob_state  # keep using your states

def apply_circular_mask(gray_img):
    h, w = gray_img.shape
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (w // 2, h // 2)
    radius = min(center[0], center[1], w - center[0], h - center[1])
    cv2.circle(mask, center, radius, 255, -1)
    masked = cv2.bitwise_and(gray_img, gray_img, mask=mask)
    return masked, mask

def smooth_angle(new_angle, history, N=10):
    history.append(new_angle)
    if len(history) > N:
        history.pop(0)
    return sum(history) / len(history)

def start_camera_loop(on_frame, on_angle, stop_event: threading.Event, *, save_frames=False):
    """
    Runs in its own thread. Captures frames, finds blob/angle, and calls:
      - on_frame(frame_rgb) with an RGB numpy array (H,W,3)
      - on_angle(angle_float_degrees)
    No GUI calls inside this function.
    """
    # prepare save dir
    save_dir = os.path.join(file_state["CURRENT_DIR"], "images")
    os.makedirs(save_dir, exist_ok=True)

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
    picam2.start()
    time.sleep(1)

    # --- ROI selection (one-time) using OpenCV's selector ---
    frame = picam2.capture_array()
    roi = cv2.selectROI("Select Top of Drum", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select Top of Drum")
    x, y, w, h = roi if roi is not None else (0, 0, frame.shape[1], frame.shape[0])

    angle_history = []
    frame_counter = -1

    try:
        while not stop_event.is_set():
            frame = picam2.capture_array()  # RGB888
            roi_frame = frame[y:y + h, x:x + w]
            now = datetime.now()
            ts = now.strftime("%Y-%m-%d_%H-%M-%S.") + f"{now.microsecond // 10000:03d}"

            # Update counter only while motor runs
            if motor_state.get("running"):
                frame_counter += 1

            raw_roi_path = os.path.join(save_dir, f"raw_roi_{frame_counter}_{ts}.jpg")
            cv2.imwrite(raw_roi_path, cv2.cvtColor(roi_frame, cv2.COLOR_RGB2BGR))
            # --- processing ---
            gray = cv2.cvtColor(roi_frame, cv2.COLOR_RGB2GRAY)
            masked_gray, _ = apply_circular_mask(gray)
            _, binary = cv2.threshold(masked_gray, 125, 75, cv2.THRESH_BINARY)

            roi_bgr = cv2.cvtColor(roi_frame, cv2.COLOR_RGB2BGR)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest = max(contours, key=cv2.contourArea)
                area = float(cv2.contourArea(largest))
                blob_state["area"] = area
                M = cv2.moments(largest)

                cx = cy = None
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(roi_bgr, (cx, cy), 5, (255, 255, 255), -1)

                cv2.drawContours(roi_bgr, [largest], -1, (0, 0, 255), 2)

                if len(largest) >= 5:
                    ellipse = cv2.fitEllipse(largest)
                    cv2.ellipse(roi_bgr, ellipse, (255, 0, 255), 2)
                    angle_raw = float(ellipse[2])
                    angle_s = smooth_angle(angle_raw, angle_history, N=10)

                    blob_state["center"] = [cx, cy] if cx is not None else None
                    blob_state["angle"] = angle_s

                    # notify GUI about angle
                    try:
                        on_angle(angle_s)
                    except Exception:
                        pass

            # send frame to GUI (convert to RGB for Tk/PIL)
            frame_rgb_ov = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
            try:
                on_frame(frame_rgb_ov)
            except Exception:
                pass

            # Optional save
            if save_frames and motor_state.get("running") and frame_counter >= 0:
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d_%H-%M-%S.") + f"{now.microsecond // 10000:03d}"
                img_name = f"frame_{frame_counter:04d}_{formatted_time}.jpg"
                cv2.imwrite(os.path.join(save_dir, img_name), cv2.cvtColor(roi_frame, cv2.COLOR_RGB2BGR))

    finally:
        try:
            picam2.stop()
        except Exception:
            pass
