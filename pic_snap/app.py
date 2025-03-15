import streamlit as st
import cv2
import os
from pathlib import Path
import time

def get_available_cameras():
    """Get a list of available camera indices."""
    if 'available_cameras' not in st.session_state:
        available_cameras = []
        for i in range(6):  # Check first 6 indices
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow backend
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        st.session_state.available_cameras = available_cameras
    return st.session_state.available_cameras

def get_next_image_number(folder_path, camera_prefix):
    """Get the next available image number for the specified camera in the folder."""
    existing_files = [f for f in os.listdir(folder_path) if f.startswith(camera_prefix)]
    if not existing_files:
        return 1
    numbers = [int(f.split('_')[1].split('.')[0]) for f in existing_files]
    return max(numbers) + 1

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'save_path' not in st.session_state:
        st.session_state.save_path = os.path.join(os.getcwd(), 'captured_images')
    if 'camera_instances' not in st.session_state:
        st.session_state.camera_instances = {}
    if 'current_frames' not in st.session_state:
        st.session_state.current_frames = {}
    if 'last_update' not in st.session_state:
        st.session_state.last_update = {}
    if 'frame_interval' not in st.session_state:
        st.session_state.frame_interval = 0.1  # 100ms default interval
    if 'error_counts' not in st.session_state:
        st.session_state.error_counts = {}

def release_camera(camera_name):
    """Safely release a camera instance."""
    if camera_name in st.session_state.camera_instances:
        cap = st.session_state.camera_instances[camera_name]
        if cap is not None:
            cap.release()
        del st.session_state.camera_instances[camera_name]
        if camera_name in st.session_state.current_frames:
            del st.session_state.current_frames[camera_name]
        if camera_name in st.session_state.last_update:
            del st.session_state.last_update[camera_name]
        if camera_name in st.session_state.error_counts:
            del st.session_state.error_counts[camera_name]

def get_camera_instance(camera_id, camera_name, resolution):
    """Get or create a camera instance with specified resolution."""
    # Release camera if it exists but has too many errors
    if camera_name in st.session_state.error_counts and st.session_state.error_counts[camera_name] > 5:
        release_camera(camera_name)
        st.warning(f"Camera {camera_name} was reset due to errors. Please refresh the page if issues persist.")
    
    if camera_name not in st.session_state.camera_instances:
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)  # Use DirectShow backend
        if cap.isOpened():
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            # Set buffer size
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            st.session_state.camera_instances[camera_name] = cap
            st.session_state.error_counts[camera_name] = 0
    return st.session_state.camera_instances.get(camera_name)

def update_camera_frame(camera_name, cap):
    """Update frame for a specific camera with frame rate control and error handling."""
    current_time = time.time()
    last_update = st.session_state.last_update.get(camera_name, 0)
    
    # Check if enough time has passed since last update
    if current_time - last_update >= st.session_state.frame_interval:
        if cap is not None and cap.isOpened():
            try:
                # Clear buffer by reading twice
                cap.read()
                ret, frame = cap.read()
                if ret:
                    st.session_state.current_frames[camera_name] = frame
                    st.session_state.last_update[camera_name] = current_time
                    st.session_state.error_counts[camera_name] = 0
                    return frame
                else:
                    st.session_state.error_counts[camera_name] = st.session_state.error_counts.get(camera_name, 0) + 1
            except Exception as e:
                st.session_state.error_counts[camera_name] = st.session_state.error_counts.get(camera_name, 0) + 1
                if st.session_state.error_counts[camera_name] > 5:
                    release_camera(camera_name)
                    return None
    return st.session_state.current_frames.get(camera_name)

def main():
    st.title("Multi-Camera Capture System")
    
    # Initialize session state
    initialize_session_state()
    
    # Get available cameras (cached)
    available_cameras = get_available_cameras()
    
    # Settings sidebar
    st.sidebar.header("Settings")
    
    # Save path selection
    new_save_path = st.sidebar.text_input("Save Path", value=st.session_state.save_path)
    if new_save_path != st.session_state.save_path:
        st.session_state.save_path = new_save_path

    # Resolution selection
    resolution_options = {
        "320x240": (320, 240),
        "640x480": (640, 480),
        "800x600": (800, 600),
        "1280x720": (1280, 720)
    }
    selected_resolution = st.sidebar.selectbox(
        "Camera Resolution",
        options=list(resolution_options.keys()),
        index=0  # Default to 320x240 for better performance
    )
    resolution = resolution_options[selected_resolution]

    # Frame rate control
    fps_options = {
        "30 FPS": 0.033,
        "20 FPS": 0.05,
        "10 FPS": 0.1,
        "5 FPS": 0.2
    }
    selected_fps = st.sidebar.selectbox(
        "Frame Rate",
        options=list(fps_options.keys()),
        index=3  # Default to 5 FPS for better stability
    )
    st.session_state.frame_interval = fps_options[selected_fps]

    # Camera selection for each feed
    col1, col2, col3 = st.columns(3)
    
    # Camera A
    with col1:
        st.header("Camera A")
        camera_a = st.selectbox("Select Camera A", 
                              options=available_cameras,
                              key="camera_a",
                              index=1 if len(available_cameras) > 1 else 0)
        cap_a = get_camera_instance(camera_a, 'A', resolution)
        frame_a = update_camera_frame('A', cap_a)
        if frame_a is not None:
            st.image(frame_a, channels="BGR", use_container_width=True)

    # Camera B
    with col2:
        st.header("Camera B")
        camera_b = st.selectbox("Select Camera B", 
                              options=available_cameras,
                              key="camera_b",
                              index=2 if len(available_cameras) > 2 else 0)
        cap_b = get_camera_instance(camera_b, 'B', resolution)
        frame_b = update_camera_frame('B', cap_b)
        if frame_b is not None:
            st.image(frame_b, channels="BGR", use_container_width=True)

    # Camera C
    with col3:
        st.header("Camera C")
        camera_c = st.selectbox("Select Camera C", 
                              options=available_cameras,
                              key="camera_c",
                              index=3 if len(available_cameras) > 3 else 0)
        cap_c = get_camera_instance(camera_c, 'C', resolution)
        frame_c = update_camera_frame('C', cap_c)
        if frame_c is not None:
            st.image(frame_c, channels="BGR", use_container_width=True)
    
    # Input field for folder name
    folder_name = st.text_input("Enter folder name for image capture", key="folder_name")
    
    if st.button("Capture Images") and folder_name:
        # Create folder if it doesn't exist
        folder_path = os.path.join(st.session_state.save_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Save current frames from all cameras
        for camera_name, frame in st.session_state.current_frames.items():
            if frame is not None:
                # Get next image number for this camera
                next_num = get_next_image_number(folder_path, camera_name)
                # Save image
                filename = f"{camera_name}_{next_num}.jpeg"
                filepath = os.path.join(folder_path, filename)
                cv2.imwrite(filepath, frame)
                st.success(f"Saved {filename}")

    # Add a refresh button to manually update frames
    if st.button("Refresh Frames"):
        # Release all cameras before refresh
        for camera_name in list(st.session_state.camera_instances.keys()):
            release_camera(camera_name)
        st.rerun()

if __name__ == "__main__":
    main()

