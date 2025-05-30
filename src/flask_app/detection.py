"""
This module provides functions for detecting and calculating the scoring points of darts thrown at a dartboard using images from multiple cameras. 
It includes utilities for processing images, determining dart tip positions, calculating gradients (slopes) from camera perspectives, 
and computing the intersection point of lines to estimate the dart's landing position on the board.

Functions:
-----------
calculating_dart_scoring_points(gradient_camera_a, gradient_camera_b, gradient_camera_c) 
    Calculates the dart scoring points based on the gradients.
score_dart(x, y)
    Calculates the score of a dart throw based on its (x, y) coordinates.
cartesian_to_polar(x, y)
    Converts Cartesian coordinates (x, y) to polar coordinates (r, theta).
intersect(xPos1, yPos1, gradient1, xPos2, yPos2, gradient2)
    Calculate the intersection point of two lines defined by their gradients and a point on each line.
calculating_dart_deviation_of_camera_perspectives(basis_dart_frame, detect_dart_frame, camera_id, medianfilterkernelsize=5, tip_finalprocessedimage=True)
    Calculates the deviation angle as gradient of a dart as seen from a specified camera perspective.
get_angle_in_gradient_camera_a(processed_dart_tip, resize_width, fov)
    Calculates the gradient corresponding to the deviation angle of a dart tip as seen by camera A.
get_angle_in_gradient_camera_b(processed_dart_tip, resize_width, fov)
    Calculates the gradient corresponding to the deviation angle of a dart tip as seen by camera B.
get_angle_in_gradient_camera_c(processed_dart_tip, resize_width, fov)
    Calculates the gradient corresponding to the deviation angle of a dart tip as seen by camera C.
find_angle(x_position, width, fov)
    Calculates the horizontal angle between a detected point based on its x-coordinate and the center of an image.
take_frame_of_dartboard_with_camera(camera_id)
    Captures a single frame from the specified camera device.

Constants:
-----------
FOV: The field of view (in degrees) used for camera calculations.
"""

from image_processing import aid_functions_image_processing, image_processing, dart_tip_processing
import math
import cmath
import cv2
import platform
from gamedata import Dart

FOV = 100 # constant for camera field of view 

def calculating_dart_scoring_points(gradient_camera_a:object, gradient_camera_b:object, gradient_camera_c:object):
    """
    Calculates the dart scoring points based on the gradients detected 
    by three cameras by computing the intersection of the lines defined by each camera's position and its detected gradient.
    
    :param gradient_camera_a: The gradient as float detected by camera A, or "Hand" as str if not detected.
    :type gradient_camera_a: object
    :param gradient_camera_b: The gradient as float detected by camera B, or "Hand" as str if not detected.
    :type gradient_camera_b: object
    :param gradient_camera_c: The gradient as float detected by camera C, or "Hand" as str if not detected.
    :type gradient_camera_c: object

    :return: A tuple (score as int, multiplier as int) representing the dart score and its multiplier (e.g., single, double, triple). 
    Returns (0, 0) if the dart is not detected by all cameras or if an error occurs during calculation.
    :rtype: tuple
    """
    # Camera locations
    aCameraX = -345*math.cos(math.radians(30))
    aCameraY = -345*math.sin(math.radians(30))
    bCameraX = 345*math.cos(math.radians(30))
    bCameraY = -345*math.sin(math.radians(30))
    cCameraX = 0
    cCameraY = 345

    if gradient_camera_a != "Hand" and gradient_camera_b != "Hand" and gradient_camera_c != "Hand":
        try:
           points = []

           points.append(intersect(aCameraX, aCameraY, gradient_camera_a, bCameraX, bCameraY, gradient_camera_b))
           points.append(intersect(aCameraX, aCameraY, gradient_camera_a, cCameraX, cCameraY, gradient_camera_c))
           points.append(intersect(bCameraX, bCameraY, gradient_camera_b, cCameraX, cCameraY, gradient_camera_c))

           xAvg = (sum([i[0] for i in points]))/len(points)
           yAvg = (sum([i[1] for i in points]))/len(points)

           dart_score = score_dart(xAvg, yAvg)

           print(f"detected calculated Dart Score: {dart_score.to_string()}")

           return dart_score.score, dart_score.multiplier
        
        except:
           print("Error in calculating dart scoring points. Returning 0, 0 as overthrown.")
           return 0, 0
    
    else:
        print("Dart not detected by all cameras. Returning 0, 0 as overthrown.")
        return 0,0


def score_dart(x:float, y:float):
    """
    Calculates the score of a dart throw based on its (x, y) coordinates by determining its position as sector and ring on a standard dartboard.
    Returns a Dart object with the score, multiplier, and position.
    
    :param x: The x-coordinate of the dart hit.
    :type x: float
    :param y: The y-coordinate of the dart hit.
    :type y: float
    :return: An instance of the Dart class representing the score, multiplier, and position.
    :rtype: Dart
    """
    r, theta = cartesian_to_polar(x, y)

    sectors = [20,5,12,9,14,11,8,16,7,19,3,17,2,15,10,6,13,4,18,1]
    sector = math.floor(((theta)/(2*math.pi))*20 + 1/2)
    value = sectors[sector]

    if 170 < r:
        return Dart(0, 0, [x, y])
    elif 162 < r:
        return Dart(value, 2, [x, y])
    elif 107 < r:
        return Dart(value, 1, [x, y])
    elif 99 < r:
        return Dart(value, 3, [x, y])
    elif 16 < r:
        return Dart(value, 1, [x, y])
    elif 6.35 < r:
        return Dart(25, 1, [x, y])
    else:
        return Dart(25, 2, [x, y])


def cartesian_to_polar(x:float, y:float):
    """
    Converts Cartesian coordinates (x, y) to polar coordinates (r, theta).

    :param x: The x-coordinate.
    :type x: float
    :param y: The y-coordinate.
    :type y: float
    :return: A tuple (radius as float, theta as float) representing the polar coordinates 
    """

    radius = math.sqrt(x**2 + y**2)

    input_num = complex(x, y)
    radius, theta = cmath.polar(input_num)
    theta += -math.pi/2
    
    return (radius, theta)


def intersect(xPos1:float, yPos1:float, gradient1:float, xPos2:float, yPos2:float, gradient2:float):
    """
    Calculate the intersection point of two lines defined by their gradients and a point on each line.

    :param xPos1: x-coordinate of the point on the first line
    :type xPos1: float
    :param yPos1: y-coordinate of the point on the first line
    :type yPos1: float
    :param gradient1: gradient (slope) of the first line
    :type gradient1: float
    :param xPos2: x-coordinate of the point on the second line
    :type xPos2: float
    :param yPos2: y-coordinate of the point on the second line
    :type yPos2: float
    :param gradient2: gradient (slope) of the second line
    :type gradient2: float
    :return: A tuple (x as float, y as float) representing the intersection point of the two lines.
    :rtype: tuple
    :raises ZeroDivisionError: If the gradients of the two lines are equal or both 0, indicating they are parallel and do not intersect.
    """
    yPos1 = -yPos1
    yPos2 = -yPos2

    c1 = yPos1 - (xPos1*gradient1)
    c2 = yPos2 - (xPos2*gradient2)

    try:
        x = (c2 - c1) / (gradient1 - gradient2)
    except ZeroDivisionError:
        raise ZeroDivisionError("Division by zero: The gradients of the two lines are equal or both 0, indicating they are parallel and do not intersect.")
    
    y = gradient1*x + c1

    return (x, y)


def calculating_dart_deviation_of_camera_perspectives(basis_dart_frame, detect_dart_frame, camera_id:str, medianfilterkernelsize:int = 5, tip_finalprocessedimage:bool = True):
    """
    Calculates the deviation angle as gradient of a dart as seen from a specified camera perspective by comparing a reference frame with a detected dart frame.
    
    :param basis_dart_frame: The reference image frame from the camera.
    :type basis_dart_frame: np.ndarray
    :param detect_dart_frame: The image frame with the new thrown dart present.
    :type detect_dart_frame: np.ndarray
    :param camera_id: Identifier for the camera perspective ('A', 'B', or 'C').
    :type camera_id: str
    :param medianfilterkernelsize: Kernel size for the median filter applied during frame difference calculation. Defaults to 5.
    :type medianfilterkernelsize: int, optional
    :param tip_finalprocessedimage: If True, uses the final processed image for dart tip detection; otherwise, uses the thresholded image. Defaults to True.
    :type tip_finalprocessedimage: bool, optional
    :return: The calculated dart deviation angle in degrees as gradient (float) for the given camera perspective, or a string ("Hand") or 0 (as int) if no dart tip is found.
    :rtype: float or str or int
    :raises Exception: If an unknown camera_id is provided.
    """
    height, width, _ = basis_dart_frame.shape

    # test with no resized size
    resize_height = int(height)
    resize_width = int(width)

    cropped_basis_frame = aid_functions_image_processing.cropp_image_frame(basis_dart_frame, resize_width, resize_height)
    cropped_detect_dart_frame = aid_functions_image_processing.cropp_image_frame(detect_dart_frame, resize_width, resize_height)
    cropped_resize_height, cropped_resize_width, _ = cropped_detect_dart_frame.shape

    difference_frame = aid_functions_image_processing.create_frame_difference(cropped_basis_frame, cropped_detect_dart_frame, medianfilterkernelsize)

    final_ksize, thresh_ksize = image_processing.image_processing(difference_frame, camera_id)

    gradient = 0

    if tip_finalprocessedimage:
        gradient_image = dart_tip_processing.dart_tip_processing(final_ksize)
    else:
        gradient_image = dart_tip_processing.dart_tip_processing(thresh_ksize)


    if gradient_image == "Hand" or gradient_image == 0:
        print("No Dart Tip found")
        return gradient_image
    
    if camera_id == "A":
        gradient = get_angle_in_gradient_camera_a(gradient_image, cropped_resize_width, FOV)
    elif camera_id == "B":
        gradient = get_angle_in_gradient_camera_b(gradient_image, cropped_resize_width, FOV)
    elif camera_id == "C":
        gradient = get_angle_in_gradient_camera_c(gradient_image, cropped_resize_width, FOV)
    else:
        raise Exception("Unknown camera id passed to score detection.")

    return gradient


def get_angle_in_gradient_camera_a(processed_dart_tip:tuple, resize_width:float, fov:int):
    """
    Calculates the gradient (slope) corresponding to the deviation angle of a dart tip as seen by camera A by reference to its Field Of View.
    
    :param processed_dart_tip: The (x, y) coordinates of the detected dart tip in the processed image.
    :type processed_dart_tip: tuple
    :param resize_width: The width of the image used for processing.
    :type resize_width: float
    :param fov: The field of view of the camera in degrees.
    :type fov: int
    :return: The gradient (slope) corresponding to the calculated angle, with sign indicating direction.
    :rtype: float
    """

    x_pos_bull_correction = 577
    camera_angle_offset = 30

    angle = find_angle(processed_dart_tip[0], resize_width, fov) - find_angle(x_pos_bull_correction, resize_width, fov) + camera_angle_offset

    # angle_to_gradient
    if angle == 0:
        slope = 0
    if angle < 0:
        slope = 1
    if angle > 0:
        slope = -1

    angle = abs(angle)

    gradient = math.sin(math.radians(angle)) / math.cos(math.radians(angle))
    gradient *= slope

    return gradient


def get_angle_in_gradient_camera_b(processed_dart_tip:tuple, resize_width:float, fov:int):
    """
    Calculates the gradient (slope) corresponding to the deviation angle of a dart tip as seen by camera B by reference to its Field Of View.
    
    :param processed_dart_tip: The (x, y) coordinates of the detected dart tip in the processed image.
    :type processed_dart_tip: tuple
    :param resize_width: The width of the image used for processing.
    :type resize_width: float
    :param fov: The field of view of the camera in degrees.
    :type fov: int
    :return: The gradient (slope) corresponding to the calculated angle, with sign indicating direction.
    :rtype: float
    """
    x_pos_bull_correction = 673
    camera_angle_offset = -30
    
    angle = find_angle(processed_dart_tip[0], resize_width, fov) - find_angle(x_pos_bull_correction, resize_width, fov) + camera_angle_offset

    # angle_to_gradient
    if angle == 0:
        slope = 0
    if angle < 0:
        slope = 1
    if angle > 0:
        slope = -1

    angle = abs(angle)

    gradient = math.sin(math.radians(angle)) / math.cos(math.radians(angle))
    gradient *= slope

    return gradient


def get_angle_in_gradient_camera_c(processed_dart_tip:tuple, resize_width:float, fov:int):
    """
    Calculates the gradient (slope) corresponding to the deviation angle of a dart tip as seen by camera C by reference to its Field Of View.
    
    :param processed_dart_tip: The (x, y) coordinates of the detected dart tip in the processed image.
    :type processed_dart_tip: tuple
    :param resize_width: The width of the image used for processing.
    :type resize_width: float
    :param fov: The field of view of the camera in degrees.
    :type fov: int
    :return: The gradient (slope) corresponding to the calculated angle, with sign indicating direction.
    :rtype: float
    """
    x_pos_bull_correction = 702
    camera_angle_offset = 0

    angle = find_angle(processed_dart_tip[0], resize_width, fov) - find_angle(x_pos_bull_correction, resize_width, fov) + camera_angle_offset

    # angle_to_gradient
    if angle == 0:
        slope = 0
    if angle < 0:
        slope = 1
    if angle > 0:
        slope = -1

    angle = abs(angle)

    gradient = math.sin(math.radians(angle)) / math.cos(math.radians(angle))
    gradient *= slope

    if gradient == 0:
        gradient = math.tan(math.radians(89.999999999999999))
    else:
        gradient = -(1/gradient)
    
    return gradient


def find_angle(x_position:float, width:float, fov:int):
    """
    Calculates the horizontal angle between a detected point based on its x-coordinate and the center of an image, by referencing to the field of view.
    
    :param x_position: The x-coordinate of the detected point in the image.
    :type x_position: float
    :param width: The total width of the image.
    :type width: float
    :param fov: The horizontal field of view of the camera in degrees.
    :type fov: int
    :return: The angle in degrees between the detected point and the center of the image.
    :rtype: float
    """
    x = x_position - width/2

    angle = math.atan((2*x*math.tan(math.radians(fov/2)))/(width))
    angle = math.degrees(angle)
    
    return angle


def take_frame_of_dartboard_with_camera(camera_id:int):
    """
    Captures a single frame from the specified camera device.
    
    :param camera_id: The ID/index of the camera device to use.
    :type camera_id: int
    :return: A tuple (success, frame) where:

            - success (bool): True if a frame was successfully captured, False otherwise.
            - frame (numpy.ndarray or None): The captured frame if successful, otherwise None.
    :rtype: tuple
    """
    system = platform.system()
    if system == "Linux":
        camera = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
    else:
        camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

    try:
        success, frame = camera.read()
        return True, frame
    except:
        if not success:
            return False, None
    finally:
        camera.release()