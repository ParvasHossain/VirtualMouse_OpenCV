import cv2
import pyautogui
import numpy as np
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Disable PyAutoGUI fail-safe pause for smoother motion
pyautogui.FAILSAFE = False

# Screen dimensions
screen_w, screen_h = pyautogui.size()

# -----------------------------------------------------------------
# MEDIAPIPE TASKS API SETUP
# -----------------------------------------------------------------
model_path = 'hand_landmarker.task'

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

# -----------------------------------------------------------------
# PARAMETERS & STATE
# -----------------------------------------------------------------
prev_x, prev_y = 0, 0
smooth_factor = 4  # Lower = faster, higher = smoother

# Margins inside camera frame to reach screen edges easily
frame_margin = 100

last_action_time = 0
cooldown_delay = 0.4  # Seconds between non-scroll clicks

cap = cv2.VideoCapture(0)

# Hand landmark indices reference:
# 4: Thumb Tip | 8: Index Tip | 12: Middle Tip | 16: Ring Tip
HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),
    (0,5), (5,6), (6,7), (7,8),
    (5,9), (9,10), (10,11), (11,12),
    (9,13), (13,14), (14,15), (15,16),
    (13,17), (17,18), (18,19), (19,20), (0,17)
]

def draw_landmarks(image, landmarks_list, width, height):
    """Draw hand skeletons manually without relying on deprecated drawing utils."""
    coords = [(int(lm.x * width), int(lm.y * height)) for lm in landmarks_list]
    for p1, p2 in HAND_CONNECTIONS:
        cv2.line(image, coords[p1], coords[p2], (0, 255, 0), 2)
    for pt in coords:
        cv2.circle(image, pt, 4, (0, 0, 255), cv2.FILLED)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Prepare image for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Perform hand detection
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        landmarks = detection_result.hand_landmarks[0]
        draw_landmarks(frame, landmarks, w, h)

        # Key landmark positions
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]

        # Convert normalized coordinates to pixel coordinates
        thm_x, thm_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
        idx_x, idx_y = int(index_tip.x * w), int(index_tip.y * h)
        mid_x, mid_y = int(middle_tip.x * w), int(middle_tip.y * h)
        rng_x, rng_y = int(ring_tip.x * w), int(ring_tip.y * h)

        # Distances between finger tips
        dist_idx = np.hypot(idx_x - thm_x, idx_y - thm_y)
        dist_mid = np.hypot(mid_x - thm_x, mid_y - thm_y)
        dist_rng = np.hypot(rng_x - thm_x, rng_y - thm_y)
        dist_idx_mid = np.hypot(idx_x - mid_x, idx_y - mid_y)

        curr_time = time.time()

        # -----------------------------------------------------------------
        # GESTURE 1: SCROLL MODE (Index & Middle fingers together)
        # -----------------------------------------------------------------
        if dist_idx_mid < 30 and dist_idx > 40:
            cv2.putText(frame, "Mode: Scroll", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            if idx_y < h // 2 - 30:
                pyautogui.scroll(120)   # Scroll Up
            elif idx_y > h // 2 + 30:
                pyautogui.scroll(-120)  # Scroll Down

        # -----------------------------------------------------------------
        # GESTURE 2: CURSOR MOVEMENT & CLICKS
        # -----------------------------------------------------------------
        else:
            # Map Index finger to screen resolution
            target_x = np.interp(idx_x, (frame_margin, w - frame_margin), (0, screen_w))
            target_y = np.interp(idx_y, (frame_margin, h - frame_margin), (0, screen_h))

            # Exponential smoothing
            curr_x = prev_x + (target_x - prev_x) / smooth_factor
            curr_y = prev_y + (target_y - prev_y) / smooth_factor

            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Left Click (Thumb + Index pinch)
            if dist_idx < 30 and (curr_time - last_action_time > cooldown_delay):
                cv2.circle(frame, (idx_x, idx_y), 15, (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, "Action: Left Click", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.click()
                last_action_time = curr_time

            # Right Click (Thumb + Middle pinch)
            elif dist_mid < 30 and (curr_time - last_action_time > cooldown_delay):
                cv2.circle(frame, (mid_x, mid_y), 15, (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, "Action: Right Click", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                pyautogui.rightClick()
                last_action_time = curr_time

            # Double Click (Thumb + Ring pinch)
            elif dist_rng < 30 and (curr_time - last_action_time > cooldown_delay):
                cv2.circle(frame, (rng_x, rng_y), 15, (255, 0, 255), cv2.FILLED)
                cv2.putText(frame, "Action: Double Click", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                pyautogui.doubleClick()
                last_action_time = curr_time

    cv2.imshow("AI Virtual Mouse Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()