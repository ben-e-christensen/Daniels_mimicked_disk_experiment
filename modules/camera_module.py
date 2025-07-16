import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image
import time
from gui_module import update_angle, update_video

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

    while True:
        frame = picam2.capture_array()
        roi_frame = frame[y:y + h, x:x + w]

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
            update_angle(f"Angle: {smoothed:.1f} deg")

        # Display image
        pil_img = Image.fromarray(display_frame)
        update_video(pil_img)

        time.sleep(0.1)
