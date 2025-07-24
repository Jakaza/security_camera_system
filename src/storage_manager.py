import os
import time
from datetime import datetime
from config.settings import Config

class StorageManager:
    @staticmethod
    def get_storage_info():
        """Get current storage usage information"""
        total_size = 0
        file_count = 0
        
        if not os.path.exists(Config.RECORDINGS_DIR):
            return {"size_gb": 0, "file_count": 0, "percentage": 0}
        
        for filename in os.listdir(Config.RECORDINGS_DIR):
            if filename.endswith('.mp4'):
                filepath = os.path.join(Config.RECORDINGS_DIR, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
                    file_count += 1
        
        size_gb = total_size / (1024 * 1024 * 1024)
        percentage = (size_gb / Config.MAX_STORAGE_GB) * 100
        
        return {
            "size_gb": round(size_gb, 3),
            "file_count": file_count,
            "percentage": round(percentage, 1),
            "max_gb": Config.MAX_STORAGE_GB
        }
    
    @staticmethod
    def print_storage_info():
        """Print storage information to console"""
        info = StorageManager.get_storage_info()
        print(f"💾 Storage: {info['size_gb']}GB/{info['max_gb']}GB ({info['percentage']}%) - {info['file_count']} files")