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
        """Get a list of available camera indices."""
        if not self.available_cameras:
            for i in range(6):  # Check first 6 indices
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  
                if cap.isOpened():
                    self.available_cameras.append(i)
                    cap.release()
        return self.available_cameras

    def release_camera(self, camera_name):
        """Safely release a camera instance."""
        if camera_name in self.camera_instances:
            cap = self.camera_instances[camera_name]
            if cap is not None:
                cap.release()
            del self.camera_instances[camera_name]
            if camera_name in self.current_frames:
                del self.current_frames[camera_name]
            if camera_name in self.last_update:
                del self.last_update[camera_name]
            if camera_name in self.error_counts:
                del self
    
    def update_camera_frame(self, camera_name):
        """Update the frame for the specified camera."""
        cap = self.camera_instances[camera_name]
        ret, frame = cap.read()
        if ret:
            self.current_frames[camera_name] = frame
            self.last_update[camera_name] = time.time()
        else:
            if camera_name in self.error_counts:
                self.error_counts[camera_name] += 1
            else:
                self.error_counts[camera_name] = 1
            self.release_camera(camera_name)