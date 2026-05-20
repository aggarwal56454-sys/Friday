import cv2
import threading
import time

class ThreadedCamera:
    """Multi-threaded webcam capture for zero-latency frame reading."""
    def __init__(self, src=0, width=640, height=480):
        # Try default backend first
        self.capture = cv2.VideoCapture(src)
        
        # Windows fallback if the camera is stubborn
        if not self.capture.isOpened():
            print("[WARNING] Default camera failed. Trying DirectShow...")
            self.capture = cv2.VideoCapture(src, cv2.CAP_DSHOW)
            
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.capture.set(cv2.CAP_PROP_FPS, 60)
        
        self.ret, self.frame = self.capture.read()
        self.running = True
        
        # Start background thread
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                self.ret = ret
                self.frame = frame
            else:
                time.sleep(0.01) # Prevent CPU overload if camera stutters

    def read(self):
        # Safely return the frame
        if self.ret and self.frame is not None:
            return self.ret, self.frame.copy()
        return False, None

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.capture.release()