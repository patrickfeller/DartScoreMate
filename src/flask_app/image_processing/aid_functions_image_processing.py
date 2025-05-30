"""
This module provides auxiliary functions for image processing tasks such as resizing images and calculating frame differences.

Functions:
-----------
cropp_image_frame(frame, resize_width, resize_height)
    Resizes the given image frame to the specified width and height using OpenCV.
create_frame_difference(basis_frame, detect_dart_frame, median_filter_kernel_size=5)
    Calculates the absolute difference between two image frames, converts the result to grayscale, and applies a median filter for smoothing.
"""

import cv2

def cropp_image_frame(frame, resize_width:int, resize_height:int):
    """
    Resizes the given image frame to the specified width and height.
    
    :param frame: The input image frame to be resized.
    :type frame: numpy.ndarray
    :param resize_width: The desired width of the resized image.
    :type resize_width: int
    :param resize_height: The desired height of the resized image.
    :type resize_height: int
    :return: The resized image frame.
    :rtype: numpy.ndarray
    """
    resizedFrame = cv2.resize(frame, (resize_width, resize_height))

    return resizedFrame


def create_frame_difference(basis_frame, detect_dart_frame, median_filter_kernel_size:int = 5):
    """
    Calculates the difference between two image frames, applies grayscale conversion, and smooths the result using a median filter.
    
    :param basis_frame: The reference image frame (in RGB format).
    :type basis_frame: numpy.ndarray
    :param detect_dart_frame: The image frame to compare against the reference (in RGB format).
    :type detect_dart_frame: numpy.ndarray
    :param median_filter_kernel_size: The size of the kernel to use for the median filter. Defaults to 5.
    :type median_filter_kernel_size: int, optional
    :return: The processed image representing the smoothed grayscale absolute difference between the two frames.
    :rtype: numpy.ndarray
    """
    # calculating the absolute difference between the two images
    diff = cv2.absdiff(basis_frame, detect_dart_frame)

    # convert the color format from RGB to grayscale
    grayscale = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

    # smoothing the image using a median filter with the specified kernel size
    blurred = cv2.medianBlur(grayscale, median_filter_kernel_size)

    return blurred