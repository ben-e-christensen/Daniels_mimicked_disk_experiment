import cv2
import numpy as np
from picamera2 import Picamera2
from PIL import Image
import time
#from gui.gui_module import update_angle, update_video
import os
from states import shared_state, state_lock, motor_state, file_state, blob_state

from datetime import datetime

# Directory to save captured frames
today = time.strftime("%Y-%m-%d_%H_%M", time.localtime())
save_dir = f"{file_state['BASE_DIR']}/{today}"
os.makedirs(save_dir, exist_ok=True)
file_state['CURRENT_DIR'] = save_dir

save_dir = f"{file_state['CURRENT_DIR']}/images"
os.makedirs(save_dir, exist_ok=True)

angle_history = []

# ROI placeholder (will be set after user selects it)
x = y = w = h = 0
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


def start_camera_loop(stop_event):
    while not stop_event.is_set():
        global x, y, w, h

        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
        picam2.start()
        time.sleep(1)

        # ROI selection
        frame = picam2.capture_array()
        
        roi = cv2.selectROI("Select Top of Drum", frame, showCrosshair=True, fromCenter=False)
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
        
        
            # Convert to grayscale
            gray = cv2.cvtColor(roi_frame, cv2.COLOR_RGB2GRAY)

            # Apply circular mask
            masked_gray, _ = apply_circular_mask(gray)

            # Threshold to binary
            _, binary = cv2.threshold(masked_gray, 125, 75, cv2.THRESH_BINARY)

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Convert to BGR for display
            roi_bgr = cv2.cvtColor(roi_frame, cv2.COLOR_RGB2BGR)

            if contours:
                largest = max(contours, key=cv2.contourArea)
                blob_state['area'] = area = cv2.contourArea(largest)
                M = cv2.moments(largest)

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(roi_bgr, (cx, cy), 5, (255, 255, 255), -1)

                cv2.drawContours(roi_bgr, [largest], -1, (0, 0, 255), 2)

                if len(largest) >= 5:
                    ellipse = cv2.fitEllipse(largest)
                    cv2.ellipse(roi_bgr, ellipse, (255, 0, 255), 2)
                    blob_state['center'] = [cx, cy]
                    blob_state['angle'] = ellipse[2]
                    #print(f"Area: {area:.2f}, Center: ({cx}, {cy}), Angle: {ellipse[2]:.2f}°")

            # Display result
            cv2.imshow("Blob Detection", roi_bgr)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            with state_lock:
                
                voltage_snapshot = shared_state["voltage"]

            # print(shared_state["voltage"])
            
            #update_angle(f"Angle: {blob_state['angle']:.1f} deg")

            # if frame_counter % 10 == 0:
            #     # Log data every 10 frames
            #     log_data(voltage=voltage_snapshot, angle=f"{blob_state['angle']:.2f}", img=img_name)
            #     cv2.imwrite(filename, frame)
            # elif frame_counter != -1: 

            #     log_data(voltage=voltage_snapshot, angle=f"{blob_state['angle']:.2f}")

            time.sleep(0.1)
    picam2.stop()
    cv2.destroyAllWindows()