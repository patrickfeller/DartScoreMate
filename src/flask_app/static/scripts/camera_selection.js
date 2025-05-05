function selectCamera(position) {
    const selectElement = document.getElementById(`camera_${position}`);
    const feedImage = document.getElementById(`camera_${position}_feed`);
    const cameraId = selectElement.value;
    
    if (cameraId) {
        feedImage.src = `/video_feed?camera_id=${cameraId}`;
    }
}

// Initialize camera feeds when page loads
document.addEventListener('DOMContentLoaded', function() {
    ['a', 'b', 'c'].forEach(position => {
        const selectElement = document.getElementById(`camera_${position}`);
        if (selectElement.value) {
            selectCamera(position);
        }
    });
});
