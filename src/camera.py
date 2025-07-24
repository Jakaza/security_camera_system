import cv2
import threading
import time
from config.settings import Config

class Camera():
    def __init__(self , source = 0):
        self.source = source
        self.cap = None
        self.frame = None
        self.running = False
        self.thread = threading.lock()


    def start(self):
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.source)

            if not self.cap.isOpened():
                raise Exception(f"Could not open camera source: {self.source}")

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, Config.FPS)

            self.running = True
            self.thread = threading.Thread(target=self._capture_frames)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"✅ Camera started successfully on source: {self.source}")
            return True
    
        except Exception as e:
            print(f"❌ Failed to start camera: {e}")
            return False

    def _capture_frames(self):
        """Continuously capture frames in separate thread"""
        while self.running :
            ret , frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                print("⚠️ Failed to read frame from camera")
                time.sleep(0.1)

    def get_frame(self):
        """Get the latest frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        """Stop camera capture"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        if self.cap:
            self.cap.release()
        print("📹 Camera stopped")