import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image
import time
from .gui_module import update_angle, update_video
import os
from states import shared_state, state_lock, motor_state
from logger import log_data
from datetime import datetime
from states import file_state
# Directory to save captured frames


today = time.strftime("%Y-%m-%d_%H:%M", time.localtime())
save_dir = f"{file_state['CURRENT_DIR']}/images"
os.makedirs(save_dir, exist_ok=True)


angle_history = []

# ROI placeholder (will be set after user selects it)
x = y = w = h = 0



def smooth_angle(new_angle, history, N=10):
    history.append(new_angle)
    if len(history) > N:
        history.pop(0)
    return sum(history) / len(history)


def start_camera_loop():
    global x, y, w, h

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
    picam2.start()
    time.sleep(1)

    # ROI selection
    frame = picam2.capture_array()
    
    roi = cv2.selectROI("Select Top of Drum", frame, False, False)
    cv2.destroyWindow("Select Top of Drum")
    x, y, w, h = roi

    frame_counter = -1  # Start from -1 to capture first frame as 0  
    while True:
        frame = picam2.capture_array()
        roi_frame = frame[y:y + h, x:x + w]
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 10000:03d}"
        img_name = f"frame_{frame_counter:04d} {formatted_time}.jpg"
        filename = os.path.join(save_dir, img_name)

        if motor_state['running']:
            frame_counter += 1
    
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 80, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        display_frame = roi_frame.copy()
        largest = None

        for cnt in contours:
            if cv2.contourArea(cnt) > 1000 and len(cnt) > 5:
                if largest is None or cv2.contourArea(cnt) > cv2.contourArea(largest):
                    largest = cnt

        if largest is not None:
            ellipse = cv2.fitEllipse(largest)
            cv2.ellipse(display_frame, ellipse, (0, 255, 0), 2)
            angle = ellipse[2]
            smoothed = smooth_angle(angle, angle_history)

            with state_lock:
                shared_state["angle"] = smoothed
                angle_snapshot = shared_state["angle"]
                voltage_snapshot = shared_state["voltage"]

            update_angle(f"Angle: {smoothed:.1f} deg")

            if frame_counter % 10 == 0:
                # Log data every 10 frames
                log_data(voltage=voltage_snapshot, angle=f"{angle_snapshot:.2f}", img=img_name)
                cv2.imwrite(filename, frame)


        # Display image
        pil_img = Image.fromarray(display_frame)
        update_video(pil_img)

        time.sleep(0.1)
