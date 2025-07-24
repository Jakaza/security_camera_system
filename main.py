import cv2
import time
import signal
import sys
from datetime import datetime, timedelta
from src.camera import Camera
from src.motion_detector import MotionDetector
from src.recorder import VideoRecorder
from src.storage_manager import StorageManager
from config.settings import Config

class SecurityCameraSystem:
    def __init__(self):
        self.camera = Camera(Config.CAMERA_INDEX)
        self.motion_detector = MotionDetector()
        self.recorder = VideoRecorder()
        self.running = False
        self.stats = {
            'start_time': None,
            'motion_events': 0,
            'recordings': 0,
            'last_motion': None
        }
        
    def start(self):
        """Start the security camera system"""
        print("🚀 Starting Security Camera System...")
        print(f"📊 Max Storage: {Config.MAX_STORAGE_GB}GB")
        print(f"📹 Recording Duration: {Config.RECORDING_DURATION}s per clip")
        print("=" * 50)
        
        # Start camera
        if not self.camera.start():
            print("❌ Failed to start camera. Exiting...")
            return False
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print("✅ System started. Press Ctrl+C to stop")
        print("👁️ Monitoring for motion...")
        
        return True
    
    def run(self):
        """Main system loop"""
        last_status_time = time.time()
        motion_cooldown = False
        cooldown_end_time = None
        
        while self.running:
            try:
                # Get current frame
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Detect motion
                motion_detected, processed_frame = self.motion_detector.detect_motion(frame)
                
                # Handle motion detection
                if motion_detected and not motion_cooldown:
                    self.stats['motion_events'] += 1
                    self.stats['last_motion'] = datetime.now()
                    
                    print(f"🚨 MOTION DETECTED! Event #{self.stats['motion_events']}")
                    
                    # Start recording
                    if self.recorder.start_recording():
                        self.stats['recordings'] += 1
                        
                    # Set cooldown to prevent multiple triggers
                    motion_cooldown = True
                    cooldown_end_time = time.time() + 5  # 5 second cooldown
                
                # Reset cooldown
                if motion_cooldown and time.time() > cooldown_end_time:
                    motion_cooldown = False
                
                # Write frame to recording if active
                if self.recorder.is_recording:
                    self.recorder.write_frame(processed_frame)
                
                # Display live feed (optional)
                if processed_frame is not None:
                    # Add status text to frame
                    status_text = "RECORDING" if self.recorder.is_recording else "MONITORING"
                    color = (0, 0, 255) if self.recorder.is_recording else (0, 255, 0)
                    
                    cv2.putText(processed_frame, status_text, (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    
                    # Show timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(processed_frame, timestamp, (10, processed_frame.shape[0] - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Security Camera', processed_frame)
                
                # Print status every 30 seconds
                if time.time() - last_status_time > 30:
                    self._print_status()
                    last_status_time = time.time()
                
                # Check for 'q' key to quit (if window is focused)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n👋 Quit command received")
                    break
                    
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(1)
        
        self.stop()
    
    def _print_status(self):
        """Print system status"""
        uptime = datetime.now() - self.stats['start_time']
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        print(f"\n📊 STATUS UPDATE")
        print(f"⏱️ Uptime: {uptime_str}")
        print(f"🚨 Motion Events: {self.stats['motion_events']}")
        print(f"🎥 Recordings: {self.stats['recordings']}")
        
        if self.stats['last_motion']:
            last_motion = datetime.now() - self.stats['last_motion']
            print(f"👁️ Last Motion: {str(last_motion).split('.')[0]} ago")
        
        StorageManager.print_storage_info()
        print("-" * 30)
    
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n🛑 Signal {sig} received. Shutting down...")
        self.running = False
    
    def stop(self):
        """Stop the security camera system"""
        print("\n🛑 Stopping Security Camera System...")
        
        self.running = False
        
        # Stop recording
        self.recorder.stop_recording()
        
        # Stop camera
        self.camera.stop()
        
        # Close OpenCV windows
        cv2.destroyAllWindows()
        
        # Print final statistics
        self._print_final_stats()
        
        print("✅ System stopped successfully")
    
    def _print_final_stats(self):
        """Print final system statistics"""
        if self.stats['start_time']:
            total_uptime = datetime.now() - self.stats['start_time']
            
            print("\n" + "=" * 50)
            print("📊 FINAL STATISTICS")
            print("=" * 50)
            print(f"⏱️ Total Uptime: {str(total_uptime).split('.')[0]}")
            print(f"🚨 Total Motion Events: {self.stats['motion_events']}")
            print(f"🎥 Total Recordings: {self.stats['recordings']}")
            
            StorageManager.print_storage_info()
            
            print("=" * 50)

def main():
    """Main entry point"""
    system = SecurityCameraSystem()
    
    try:
        if system.start():
            system.run()
    except KeyboardInterrupt:
        print("\n👋 Keyboard interrupt received")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        system.stop()

if __name__ == "__main__":
    main()