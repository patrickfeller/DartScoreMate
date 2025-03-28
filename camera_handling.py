import cv2
import os
from pathlib import Path
import time

class camera:
    def __init__(self):
        self.available_cameras = []
        self.camera_instances = {}
        self.current_frames = {}
        self.last_update = {}
        self.frame_interval = 0.1  # 100ms default interval
        self.error_counts = {}
        self.resulution_options = {
            "320x240": (320, 240),
            "640x480": (640, 480),
            "1280x720": (1280, 720),
            "1920x1080": (1920, 1080)
        }
        self.fps_options = {
            "30 FPS": 0.033,
            "20 FPS": 0.05,
            "10 FPS": 0.1,
            "5 FPS": 0.2
        }
 
    def get_available_cameras(self):
        """Get a list of available camera indices with name."""
        if not self.available_cameras:
            for i in range(6):  # Check first 6 indices
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  
                if cap.isOpened():
                    self.available_cameras.append(i)
                    cap.release()
        return self.available_cameras
