import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Disable PyAutoGUI fail-safe pause for smoother motion
pyautogui.FAILSAFE = False

# Screen dimensions
screen_w, screen_h = pyautogui.size()

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Frame smoothing parameters
prev_x, prev_y = 0, 0
smooth_factor = 4  # Lower value = faster response, higher = smoother cursor

# Active region boundary (margin in pixels)
frame_margin = 100

# Cooldown timers to prevent rapid multi-triggering
last_action_time = 0
cooldown_delay = 0.4  # Seconds between non-scroll clicks

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            
            # Key landmark positions
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]

            # Convert to camera pixel coordinates
            thm_x, thm_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            idx_x, idx_y = int(index_tip.x * w), int(index_tip.y * h)
            mid_x, mid_y = int(middle_tip.x * w), int(middle_tip.y * h)
            rng_x, rng_y = int(ring_tip.x * w), int(ring_tip.y * h)

            # Measure distances between thumb tip and other finger tips
            dist_idx = np.hypot(idx_x - thm_x, idx_y - thm_y)
            dist_mid = np.hypot(mid_x - thm_x, mid_y - thm_y)
            dist_rng = np.hypot(rng_x - thm_x, rng_y - thm_y)
            dist_idx_mid = np.hypot(idx_x - mid_x, idx_y - mid_y)

            # Current timestamp for cooldown handling
            curr_time = time.time()

            # -----------------------------------------------------------------
            # GESTURE 1: SCROLL MODE (Index & Middle fingers held close together)
            # -----------------------------------------------------------------
            if dist_idx_mid < 30 and dist_idx > 40:
                cv2.putText(frame, "Mode: Scroll", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                # Vertical movement controls scrolling speed & direction
                if idx_y < h // 2 - 30:
                    pyautogui.scroll(120)  # Scroll Up
                elif idx_y > h // 2 + 30:
                    pyautogui.scroll(-120) # Scroll Down

            # -----------------------------------------------------------------
            # GESTURE 2: CURSOR MOVEMENT & CLICKS
            # -----------------------------------------------------------------
            else:
                # Map Index finger to Screen coordinates
                target_x = np.interp(idx_x, (frame_margin, w - frame_margin), (0, screen_w))
                target_y = np.interp(idx_y, (frame_margin, h - frame_margin), (0, screen_h))

                # Smooth cursor trajectory
                curr_x = prev_x + (target_x - prev_x) / smooth_factor
                curr_y = prev_y + (target_y - prev_y) / smooth_factor

                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

                # Left-Click (Thumb + Index pinch)
                if dist_idx < 30 and (curr_time - last_action_time > cooldown_delay):
                    cv2.circle(frame, (idx_x, idx_y), 15, (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, "Action: Left Click", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    pyautogui.click()
                    last_action_time = curr_time

                # Right-Click (Thumb + Middle pinch)
                elif dist_mid < 30 and (curr_time - last_action_time > cooldown_delay):
                    cv2.circle(frame, (mid_x, mid_y), 15, (0, 0, 255), cv2.FILLED)
                    cv2.putText(frame, "Action: Right Click", (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    pyautogui.rightClick()
                    last_action_time = curr_time

                # Double-Click (Thumb + Ring pinch)
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