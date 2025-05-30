"""
This module provides the `image_processing` function, 
which processes a difference frame using multiple thresholding techniques and morphological operations to enhance features for further image analysis.
"""

import cv2
import skimage
#import matplotlib.pyplot as plt

def image_processing(blurred_diff_frame, camera_id:str):
    """
    Processes a difference frame using multiple thresholding and morphological operations to enhance features for further image analysis.

    :param blurred_diff_frame: The input grayscale image (difference frame) to be processed.
    :type blurred_diff_frame: numpy.ndarray
    :param camera_id: Identifier for the camera, used for logging or saving images.
    :type camera_id: str

    :return: A tuple containing the processed image and the thresholded image after morphological operations.

            - final (numpy.ndarray): The processed image combining morphological operations and Canny edge detection.
            - thresh_morph_kernelClose (numpy.ndarray): The thresholded and morphologically processed image using a fixed threshold value.
    """
    thresh_val = 15

    # apply canny algorithm
    can = cv2.Canny(blurred_diff_frame, 30, 90)

    triangle_threshold = skimage.filters.threshold_triangle(blurred_diff_frame)
    _, triangle = cv2.threshold(blurred_diff_frame, triangle_threshold, 255, cv2.THRESH_BINARY)

    yen_threshold = skimage.filters.threshold_yen(blurred_diff_frame)
    _, yen = cv2.threshold(blurred_diff_frame, yen_threshold, 255, cv2.THRESH_BINARY)

    li_threshold = skimage.filters.threshold_li(blurred_diff_frame)
    _, li = cv2.threshold(blurred_diff_frame, li_threshold, 255, cv2.THRESH_BINARY)

    # Combine the three thresholding methods
    combined_threshs = (triangle/3) + (yen/3) + (li/3)
    combined_threshs = cv2.convertScaleAbs(combined_threshs)
    ret, all = cv2.threshold(combined_threshs, 150, 255, cv2.THRESH_BINARY)

    # Morphological operations to remove noise
    # kernels as ellipse with 3x5
    kernelOpen = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,5))
    kernelClose = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,5))

    morphological_kernelOpen = cv2.morphologyEx(all, cv2.MORPH_OPEN, kernelOpen)
    morphological_kernelClose = cv2.morphologyEx(morphological_kernelOpen, cv2.MORPH_CLOSE, kernelClose)
    img_preprocessed = morphological_kernelClose

    _, thresh = cv2.threshold(blurred_diff_frame, thresh_val, 255, cv2.THRESH_BINARY)

    thresh_morph_kernelOpen = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernelOpen)

    thresh_morph_kernelClose = cv2.morphologyEx(thresh_morph_kernelOpen, cv2.MORPH_CLOSE, kernelClose)

    # Combine thresholded image with Canny edge detector
    final = img_preprocessed | can
    
    ##Save the final image
    #plt.imshow(final, cmap='gray')  # Ensure the image is displayed in grayscale
    #plt.axis('off')  # Turn off axes for better visualization
    #plt.savefig(f"logging/final_image_{camera_id}.jpg", bbox_inches='tight')  # Save the figure without extra whitespace
    #plt.close()  # Close the figure to free memory

    return final, thresh_morph_kernelClose