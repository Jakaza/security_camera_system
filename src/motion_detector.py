import cv2
import imutils
import numpy as np
from datetime import datetime

class MotionDetector:
    def __init__(self):
        self.background = None
        self.motion_detected = False
        self.last_motion_time = None
        
    def detect_motion(self, frame):
        """Detect motion in the current frame"""
        if frame is None:
            return False, None
            
        from config.settings import Config
        
        # Convert to grayscale and blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (Config.BLUR_SIZE, Config.BLUR_SIZE), 0)
        
        # Initialize background frame
        if self.background is None:
            self.background = gray
            return False, frame
        
        # Compute absolute difference between current and background frame
        frame_delta = cv2.absdiff(self.background, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate the threshold image to fill holes
        thresh = cv2.dilate(thresh, None, iterations=Config.DILATE_ITERATIONS)
        
        # Find contours
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        
        motion_detected = False
        
        # Draw rectangles around detected motion
        for contour in contours:
            if cv2.contourArea(contour) < Config.MOTION_THRESHOLD:
                continue
                
            motion_detected = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Update motion status
        if motion_detected:
            self.motion_detected = True
            self.last_motion_time = datetime.now()
            
        # Update background (slowly adapt to changes)
        self.background = cv2.addWeighted(self.background, 0.95, gray, 0.05, 0)
        
        return motion_detected, frame
    
    def reset_background(self):
        """Reset background model"""
        self.background = None
        print("🔄 Background model reset")