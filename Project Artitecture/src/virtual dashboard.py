from src.utils import get_distance

class GestureEngine:
    # Increased threshold to 50 for much easier clicking!
    def __init__(self, pinch_threshold=50): 
        self.pinch_threshold = pinch_threshold
        
    def detect_gesture(self, landmarks):
        """Analyzes landmarks and returns the current gesture state."""
        if not landmarks or len(landmarks) < 21:
            return "NONE"

        thumb_tip = landmarks[4][1:]
        index_tip = landmarks[8][1:]
        middle_tip = landmarks[12][1:]
        
        thumb_index_dist = get_distance(thumb_tip, index_tip)
        thumb_middle_dist = get_distance(thumb_tip, middle_tip)
        
        fingers_up = [
            landmarks[8][2] < landmarks[6][2],   # Index
            landmarks[12][2] < landmarks[10][2], # Middle
            landmarks[16][2] < landmarks[14][2], # Ring
            landmarks[20][2] < landmarks[18][2]  # Pinky
        ]

        # Prioritize clicks over everything else for responsiveness
        if thumb_index_dist < self.pinch_threshold:
            return "LEFT_CLICK"
            
        if thumb_middle_dist < self.pinch_threshold:
            return "RIGHT_CLICK"

        if not any(fingers_up):
            return "FIST" 
            
        if fingers_up[0] and not fingers_up[1]:
            return "MOVE"
            
        if all(fingers_up):
            return "OPEN_PALM"
            
        return "NONE"