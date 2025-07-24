import cv2
import os
import threading
import time
from datetime import datetime
from config.settings import Config

class VideoRecorder:
    def __init__(self):
        self.is_recording = False
        self.writer = None
        self.recording_thread = None
        self.frames_buffer = []
        self.buffer_lock = threading.Lock()
        
    def start_recording(self, filename=None):
        """Start recording video"""
        if self.is_recording:
            return False
            
        if filename is None:
            filename = Config.get_video_filename()
            
        filepath = os.path.join(Config.RECORDINGS_DIR, filename)
        
        # Check storage space before recording
        if not self._check_storage_space():
            print("⚠️ Storage limit reached (1GB). Cleaning old files...")
            self._cleanup_old_recordings()
            
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*Config.VIDEO_FORMAT)
        self.writer = cv2.VideoWriter(
            filepath, 
            fourcc, 
            Config.FPS, 
            (Config.FRAME_WIDTH, Config.FRAME_HEIGHT)
        )
        
        if not self.writer.isOpened():
            print(f"❌ Failed to start recording: {filepath}")
            return False
            
        self.is_recording = True
        self.start_time = datetime.now()
        
        print(f"🔴 Recording started: {filename}")
        
        # Start recording timer
        self.recording_thread = threading.Timer(
            Config.RECORDING_DURATION, 
            self.stop_recording
        )
        self.recording_thread.start()
        
        return True
    
    def write_frame(self, frame):
        """Write frame to video file"""
        if self.is_recording and self.writer and frame is not None:
            # Resize frame to match recording dimensions
            frame_resized = cv2.resize(frame, (Config.FRAME_WIDTH, Config.FRAME_HEIGHT))
            self.writer.write(frame_resized)
    
    def stop_recording(self):
        """Stop recording video"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.recording_thread:
            self.recording_thread.cancel()
        
        if self.writer:
            self.writer.release()
            self.writer = None
            
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"⏹️ Recording stopped. Duration: {duration:.1f}s")
    
    def _check_storage_space(self):
        """Check if storage limit is reached"""
        total_size = 0
        for filename in os.listdir(Config.RECORDINGS_DIR):
            if filename.endswith('.mp4'):
                filepath = os.path.join(Config.RECORDINGS_DIR, filename)
                total_size += os.path.getsize(filepath)
        
        # Convert bytes to GB
        total_gb = total_size / (1024 * 1024 * 1024)
        
        print(f"💾 Storage used: {total_gb:.2f}GB / {Config.MAX_STORAGE_GB}GB")
        
        return total_gb < Config.MAX_STORAGE_GB
    
    def _cleanup_old_recordings(self):
        """Remove oldest recordings to free space"""
        recordings = []
        
        for filename in os.listdir(Config.RECORDINGS_DIR):
            if filename.endswith('.mp4'):
                filepath = os.path.join(Config.RECORDINGS_DIR, filename)
                mtime = os.path.getmtime(filepath)
                recordings.append((filepath, mtime))
        
        # Sort by modification time (oldest first)
        recordings.sort(key=lambda x: x[1])
        
        # Remove oldest 20% of files
        files_to_remove = max(1, len(recordings) // 5)
        
        for filepath, _ in recordings[:files_to_remove]:
            try:
                os.remove(filepath)
                filename = os.path.basename(filepath)
                print(f"🗑️ Removed old recording: {filename}")
            except Exception as e:
                print(f"❌ Failed to remove {filepath}: {e}")