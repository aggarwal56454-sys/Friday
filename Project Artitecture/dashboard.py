import sys
import cv2
import numpy as np
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QHBoxLayout, QWidget, QSlider, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor

# Import our custom AI modules
from src.camera import ThreadedCamera
from src.tracker import HandTracker
from src.gestures import GestureEngine
from src.controller import MouseController

class AIVisionThread(QThread):
    """
    Background thread that runs the AI tracking so the UI doesn't freeze.
    """
    update_frame = pyqtSignal(np.ndarray)
    update_stats = pyqtSignal(int, str, bool, float, float) # Added X/Y coordinate tracking

    def __init__(self, screen_w, screen_h):
        super().__init__()
        self.running = True
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.smooth_factor = 0.5 

    def run(self):
        CAM_W, CAM_H = 640, 480
        camera = ThreadedCamera(src=0, width=CAM_W, height=CAM_H)
        tracker = HandTracker(max_hands=1, detection_con=0.8, tracking_con=0.8)
        gesture_engine = GestureEngine(pinch_threshold=50) # 50 makes pinching super easy
        mouse_ctrl = MouseController(self.screen_w, self.screen_h, CAM_W, CAM_H, reduction=100)

        p_time = 0
        active_mode = True

        while self.running:
            ret, frame = camera.read()
            if not ret: 
                self.msleep(10) # Qt native sleep, better for UI threads
                continue

            frame = cv2.flip(frame, 1) # Selfie view
            frame, landmarks = tracker.find_hands(frame, draw=True)
            gesture = "NONE"
            index_x, index_y = 0.0, 0.0

            # Dynamically update smoothing from the UI slider
            mouse_ctrl.smooth_factor = self.smooth_factor

            if landmarks:
                gesture = gesture_engine.detect_gesture(landmarks)
                
                if gesture == "FIST":
                    active_mode = False
                elif gesture == "OPEN_PALM":
                    active_mode = True

                index_x, index_y = landmarks[8][1], landmarks[8][2]
                
                if active_mode:
                    if gesture in ["MOVE", "LEFT_CLICK", "RIGHT_CLICK", "SCROLL_MODE"]:
                        mouse_ctrl.update_position(index_x, index_y)
                    mouse_ctrl.execute_gesture(gesture)

            # FPS Calc
            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time

            # Send data to the UI thread
            self.update_frame.emit(frame)
            self.update_stats.emit(int(fps), gesture, active_mode, index_x, index_y)
            
            # CRITICAL LAG FIX: Native Qt sleep prevents 100% CPU lockup
            self.msleep(10) 

        camera.stop()

    def stop(self):
        self.running = False
        self.wait()


class DashboardUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Vision - Virtual OS Control")
        self.setGeometry(100, 100, 1000, 650)
        
        # Professional Cyberpunk / Dark Mode Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0f19;
            }
            QLabel {
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame#Panel {
                background-color: #111827;
                border: 1px solid #1e293b;
                border-radius: 12px;
            }
            QSlider::groove:horizontal {
                border-radius: 4px;
                height: 8px;
                margin: 0px;
                background-color: #334155;
            }
            QSlider::handle:horizontal {
                background-color: #00f3ff;
                border: 2px solid #ffffff;
                height: 20px;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background-color: #00f3ff;
                border-radius: 4px;
            }
        """)

        screen = QApplication.primaryScreen().size()
        self.init_ui()
        
        # Start AI Thread
        self.ai_thread = AIVisionThread(screen.width(), screen.height())
        self.ai_thread.update_frame.connect(self.set_image)
        self.ai_thread.update_stats.connect(self.update_labels)
        self.ai_thread.start()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Left Panel (Settings & Stats) ---
        left_panel = QFrame()
        left_panel.setObjectName("Panel")
        left_panel.setFixedWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(25, 25, 25, 25)
        left_layout.setSpacing(15)
        
        # Title
        title = QLabel("CORE SYSTEM")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #00f3ff; letter-spacing: 2px;")
        
        # Status Light
        self.status_label = QLabel("● SYSTEM ONLINE")
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.status_label.setStyleSheet("color: #00ffcc; margin-bottom: 20px;")
        
        # Stats Grid
        stats_layout = QGridLayout()
        
        lbl_fps_title = QLabel("ENGINE FPS:")
        lbl_fps_title.setStyleSheet("color: #94a3b8; font-weight: bold;")
        self.fps_label = QLabel("--")
        self.fps_label.setFont(QFont("Consolas", 14, QFont.Bold))
        self.fps_label.setStyleSheet("color: #ffffff;")
        
        lbl_gest_title = QLabel("LAST GESTURE:")
        lbl_gest_title.setStyleSheet("color: #94a3b8; font-weight: bold;")
        self.gesture_label = QLabel("NONE")
        self.gesture_label.setFont(QFont("Consolas", 14, QFont.Bold))
        self.gesture_label.setStyleSheet("color: #ff003c;")
        
        lbl_mode_title = QLabel("TRACKING MODE:")
        lbl_mode_title.setStyleSheet("color: #94a3b8; font-weight: bold;")
        self.mode_label = QLabel("ACTIVE")
        self.mode_label.setFont(QFont("Consolas", 14, QFont.Bold))
        self.mode_label.setStyleSheet("color: #00ffcc;")

        lbl_coords_title = QLabel("TARGET (X,Y):")
        lbl_coords_title.setStyleSheet("color: #94a3b8; font-weight: bold;")
        self.coords_label = QLabel("0.00, 0.00")
        self.coords_label.setFont(QFont("Consolas", 12))
        self.coords_label.setStyleSheet("color: #cbd5e1;")
        
        stats_layout.addWidget(lbl_fps_title, 0, 0)
        stats_layout.addWidget(self.fps_label, 0, 1)
        stats_layout.addWidget(lbl_gest_title, 1, 0)
        stats_layout.addWidget(self.gesture_label, 1, 1)
        stats_layout.addWidget(lbl_mode_title, 2, 0)
        stats_layout.addWidget(self.mode_label, 2, 1)
        stats_layout.addWidget(lbl_coords_title, 3, 0)
        stats_layout.addWidget(self.coords_label, 3, 1)

        # Smoothing Slider
        slider_title = QLabel("CURSOR SMOOTHING (EMA)")
        slider_title.setFont(QFont("Arial", 10, QFont.Bold))
        slider_title.setStyleSheet("color: #00f3ff; margin-top: 30px;")
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(50) # Default 0.5
        self.slider.valueChanged.connect(self.change_smoothing)
        
        slider_desc = QLabel("Lower = Smoother | Higher = Snappier")
        slider_desc.setStyleSheet("color: #64748b; font-size: 11px;")

        left_layout.addWidget(title)
        left_layout.addWidget(self.status_label)
        left_layout.addLayout(stats_layout)
        left_layout.addWidget(slider_title)
        left_layout.addWidget(self.slider)
        left_layout.addWidget(slider_desc)
        left_layout.addStretch()

        # --- Right Panel (Camera Feed) ---
        right_panel = QFrame()
        right_panel.setObjectName("Panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        cam_title = QLabel("LIVE VISION FEED")
        cam_title.setFont(QFont("Arial", 12, QFont.Bold))
        cam_title.setStyleSheet("color: #94a3b8; margin-bottom: 5px;")
        
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: #000000; border-radius: 8px;")
        self.video_label.setAlignment(Qt.AlignCenter)
        
        right_layout.addWidget(cam_title)
        right_layout.addWidget(self.video_label)
        right_layout.addStretch()
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

    def change_smoothing(self):
        val = self.slider.value() / 100.0
        self.ai_thread.smooth_factor = val

    def update_labels(self, fps, gesture, active, x, y):
        self.fps_label.setText(f"{fps}")
        self.gesture_label.setText(f"{gesture}")
        self.coords_label.setText(f"{x:.2f}, {y:.2f}")
        
        if active:
            self.mode_label.setText("ACTIVE")
            self.mode_label.setStyleSheet("color: #00ffcc;") # Neon Green
        else:
            self.mode_label.setText("LOCKED")
            self.mode_label.setStyleSheet("color: #ff003c;") # Neon Red

    def set_image(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        self.ai_thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DashboardUI()
    window.show()
    sys.exit(app.exec_())