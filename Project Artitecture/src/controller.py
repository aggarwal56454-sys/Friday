from pynput.mouse import Button, Controller
import time
from src.utils import map_coordinates

class MouseController:
    def __init__(self, screen_w, screen_h, frame_w, frame_h, reduction=100):
        self.mouse = Controller()
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        # Interaction box (deadzone reduction)
        self.box_x1, self.box_x2 = reduction, frame_w - reduction
        self.box_y1, self.box_y2 = reduction, frame_h - reduction * 2
        
        # Smoothing setup
        self.prev_x, self.prev_y = 0, 0
        self.smooth_factor = 0.5 
        
        # Click state tracking (Prevents lag/spam)
        self.left_down = False
        self.right_down = False
        self.right_click_cooldown = 0

    def update_position(self, target_x, target_y):
        """Maps camera coordinate to screen coordinate with smoothing."""
        screen_x = map_coordinates(target_x, self.box_x1, self.box_x2, 0, self.screen_w)
        screen_y = map_coordinates(target_y, self.box_y1, self.box_y2, 0, self.screen_h)
        
        curr_x = self.prev_x + (screen_x - self.prev_x) * self.smooth_factor
        curr_y = self.prev_y + (screen_y - self.prev_y) * self.smooth_factor
        
        self.mouse.position = (curr_x, curr_y)
        self.prev_x, self.prev_y = curr_x, curr_y

    def execute_gesture(self, gesture):
        # Handle Right Click Cooldown
        if self.right_click_cooldown > 0:
            self.right_click_cooldown -= 1

        if gesture == "LEFT_CLICK":
            if not self.left_down:
                self.mouse.press(Button.left)
                self.left_down = True
        elif gesture == "RIGHT_CLICK":
            if not self.right_down and self.right_click_cooldown == 0:
                self.mouse.click(Button.right, 1)
                self.right_down = True
                self.right_click_cooldown = 20 # Wait 20 frames before allowing another right click
        else:
            # If no click gesture is detected, release everything
            if self.left_down:
                self.mouse.release(Button.left)
                self.left_down = False
            self.right_down = False