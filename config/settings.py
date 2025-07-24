import os
from datetime import datetime

class Config() :
    # Camera settings
    CAMERA_INDEX = 0
    FRAME_WIDTH = 640
    FRAME_HIGHT = 480
    FPS = 20
    # Motion detection settings
    MOTION_THRESHOLD = 500
    BLUR_SIZE = 21
    DILATE_SIZE = 2
    # Recording settings
    MAX_STORAGE_GB = 1.0
    RECORDING_DURATION = 30
    VIDEO_FORMAT = 'mp4v'
    # Directory settings
    BASE_DIR = os.path.dirname(os.path.dirname(so.path.abspath(__file__)))
    RECORDING_DIR = os.path.join(BASE_DIR, 'recordings')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')

    # Ensure directories exist
    os.makedirs(RECORDING_DIR, exist_ok = True)
    os.makedirs(LOGS_DIR, exist_ok = True)

    @staticmethod
    def get_video_filename():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"motion_{timestamp}.mp4"







