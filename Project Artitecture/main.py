import cv2
import time
from tkinter import Tk
from src.camera import ThreadedCamera
from src.tracker import HandTracker
from src.gestures import GestureEngine
from src.controller import MouseController

def get_screen_resolution():
    """Gets primary monitor resolution."""
    root = Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.destroy()
    return w, h

def draw_hud(frame, fps, gesture, active_mode):
    """Draws a futuristic cyberpunk-style HUD on the camera feed."""
    h, w, _ = frame.shape
    
    # Overlay Background
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 80), (15, 15, 15), -1)
    cv2.rectangle(overlay, (0, h-40), (w, h), (15, 15, 15), -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

    # Texts & Stats
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"AI VISION V1.0", (20, 30), font, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"FPS: {int(fps)}", (w - 120, 30), font, 0.7, (0, 255, 0), 2)
    
    # Gesture & Status Indicator
    status_color = (0, 255, 0) if active_mode else (0, 0, 255)
    cv2.putText(frame, f"GESTURE: {gesture}", (20, 60), font, 0.7, (255, 0, 255), 2)
    cv2.putText(frame, f"STATE: {'ACTIVE' if active_mode else 'LOCKED'}", (w - 200, 60), font, 0.7, status_color, 2)
    
    # Draw Interaction Box
    cv2.rectangle(frame, (100, 100), (w-100, h-200), (255, 0, 255), 1)
    
    return frame

def main():
    # Setup Constants
    CAM_W, CAM_H = 640, 480
    SCREEN_W, SCREEN_H = get_screen_resolution()
    
    # Initialize Modules
    print("[INFO] Initializing AI Tracking System...")
    camera = ThreadedCamera(src=0, width=CAM_W, height=CAM_H)
    tracker = HandTracker(max_hands=1, detection_con=0.8, tracking_con=0.8)
    gesture_engine = GestureEngine(pinch_threshold=35)
    mouse_ctrl = MouseController(SCREEN_W, SCREEN_H, CAM_W, CAM_H, reduction=100)

    p_time = 0
    active_mode = True # False means cursor is locked

    try:
        while True:
            ret, frame = camera.read()
            if not ret: continue

            # Flip horizontally for selfie-view natural interaction
            frame = cv2.flip(frame, 1)
            
            # Process Hand Tracking
            frame, landmarks = tracker.find_hands(frame)
            gesture = "NONE"

            if landmarks:
                gesture = gesture_engine.detect_gesture(landmarks)
                
                # Check for Lock/Unlock
                if gesture == "FIST":
                    active_mode = False
                elif gesture == "OPEN_PALM":
                    active_mode = True

                if active_mode:
                    # Index finger tip is landmark 8
                    index_x, index_y = landmarks[8][1], landmarks[8][2]
                    
                    if gesture in ["MOVE", "LEFT_CLICK", "RIGHT_CLICK"]:
                        mouse_ctrl.update_position(index_x, index_y)
                    
                    mouse_ctrl.execute_gesture(gesture)

            # Calculate FPS
            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time

            # Draw UI
            frame = draw_hud(frame, fps, gesture, active_mode)

            # Render Screen
            cv2.imshow("Virtual Touchscreen UI", frame)

            # Exit condition
            if cv2.waitKey(1) & 0xFF == 27: # ESC key
                break
                
    except KeyboardInterrupt:
        print("[INFO] System interrupted by user.")
    finally:
        print("[INFO] Shutting down...")
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()