import cv2
import mediapipe as mp

# Explicitly import the solutions modules to fix the AttributeError
from mediapipe.python.solutions import hands as mp_hands_module
from mediapipe.python.solutions import drawing_utils as mp_draw_module

class HandTracker:
    def __init__(self, max_hands=1, detection_con=0.8, tracking_con=0.8):
        self.mp_hands = mp_hands_module
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=tracking_con
        )
        self.mp_draw = mp_draw_module

    def find_hands(self, frame, draw=True):
        """Processes the frame and returns landmarks and the drawn frame."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        
        landmarks = []
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    # Draw futuristic cyan connections
                    self.mp_draw.draw_landmarks(
                        frame, hand_lms, self.mp_hands.HAND_CONNECTIONS,
                        self.mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=2),
                        self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)
                    )
                
                h, w, c = frame.shape
                # Convert normalized coordinates to pixel coordinates
                for id, lm in enumerate(hand_lms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks.append([id, cx, cy])
        
        return frame, landmarks