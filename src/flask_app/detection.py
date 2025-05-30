from image_processing import aid_functions_image_processing, image_processing, dart_tip_processing
import math
import cmath
import cv2
from gamedata import Dart

# constant for camera field of view 
FOV = 100


def calculating_dart_scoring_points(gradient_camera_a, gradient_camera_b, gradient_camera_c):
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

           #print(f"points: {points}")

           xAvg = (sum([i[0] for i in points]))/len(points)
           yAvg = (sum([i[1] for i in points]))/len(points)

           #print(f"calculated Average points: xAvg:{xAvg}; yAvg:{yAvg}")

           dart_score = score_dart(xAvg, yAvg)

           #print(f"Dart Score: {dart_score.to_string()}")

           return dart_score.score, dart_score.multiplier
        
        except:
           #print("Error in calculating dart scoring points. Returning 0, 0 as overthrown.")
           return 0, 0
    
    else:
        return 0,0


def score_dart(x, y):
    r, theta = cartesian_to_polar(x, y)

    print(f"calculated polar: r: {r}, theta: {theta}")

    sectors = [20,5,12,9,14,11,8,16,7,19,3,17,2,15,10,6,13,4,18,1]
    sector = math.floor(((theta)/(2*math.pi))*20 + 1/2)

    print(f"calculated sector: {sector}")

    value = sectors[sector]

    print(f"calculated value: {value}")

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


def cartesian_to_polar(x, y):
    r = math.sqrt(x**2 + y**2)

    input_num = complex(x, y)
    r, theta = cmath.polar(input_num)
    theta += -math.pi/2
    
    return (r, theta)


def intersect(xPos1, yPos1, gradient1, xPos2, yPos2, gradient2):
    yPos1 = -yPos1
    yPos2 = -yPos2

    c1 = yPos1 - (xPos1*gradient1)
    c2 = yPos2 - (xPos2*gradient2)

    x = (c2 - c1) / (gradient1 - gradient2)
    y = gradient1*x + c1

    return (x, y)


def calculating_dart_deviation_of_camera_perspectives(basis_dart_frame, detect_dart_frame, camera_id, medianfilterkernelsize = 5, tip_finalprocessedimage = True):
    height, width, _ = basis_dart_frame.shape
    #print(f"basic height: {height},\nbasic width: {width}")

    # test with no resized size
    resize_height = int(height)
    resize_width = int(width)
    cropped_height = 0

    #print(f"Resized shape:\nresized height: {resizeHeight},\nresized width: {resizeWidth},\ncropped height: {croppedHeight}\n")

    #print("empty frame")
    cropped_basis_frame = aid_functions_image_processing.cropp_image_frame(basis_dart_frame, resize_width, resize_height, cropped_height)
    #print("test frame")
    cropped_detect_dart_frame = aid_functions_image_processing.cropp_image_frame(detect_dart_frame, resize_width, resize_height, cropped_height)
    cropped_resize_height, cropped_resize_width, _ = cropped_detect_dart_frame.shape
    

    #print(f"create difference with medianfilterkernelsize: {medianfilterkernelsize}")
    blurred_ksize = aid_functions_image_processing.create_frame_difference(cropped_basis_frame, cropped_detect_dart_frame, medianfilterkernelsize)

    #print("image processing")
    final_ksize, thresh_ksize = image_processing.image_processing(blurred_ksize, camera_id)

    gradient = 0


    if tip_finalprocessedimage:
        #print("find dart tip Gradient - final image")
        gradient_image = dart_tip_processing.dart_tip_processing(final_ksize)
    else:
        #print("find dart tip Gradient - thresh image")
        gradient_image = dart_tip_processing.dart_tip_processing(thresh_ksize)


    if gradient_image == "Hand" or gradient_image == 0:
        #print("No Dart Tip found")
        return gradient_image
    
    if camera_id == "A":
        gradient = get_angle_in_gradient_a(gradient_image, cropped_resize_width, FOV)

        # D20
        #gradient = get_angle_in_gradient_a([294.7], cropped_resize_width, FOV) # Test with manually measured x Pos = 294.7

        # D25
        #gradient = get_angle_in_gradient_a([577], cropped_resize_width, FOV) # Test with manually measured x Pos = 577

        # T12
        #gradient = get_angle_in_gradient_a([491.2], cropped_resize_width, FOV) # Test with manually measured x Pos = 491.2
        
    elif camera_id == "B":
        gradient = get_angle_in_gradient_b(gradient_image, cropped_resize_width, FOV)

        # D20
        #gradient = get_angle_in_gradient_b([947.9], cropped_resize_width, FOV) # Test with manually measured x Pos = 947.9

        # D25
        #gradient = get_angle_in_gradient_b([673], cropped_resize_width, FOV) # Test with manually measured x Pos = 673

        # T12
        #gradient = get_angle_in_gradient_b([835.9], cropped_resize_width, FOV) # Test with manually measured x Pos = 835.9

    elif camera_id == "C":
        gradient = get_angle_in_gradient_c(gradient_image, cropped_resize_width, FOV)

        # D20
        #gradient = get_angle_in_gradient_c([696.3], cropped_resize_width, FOV) # Test with manually measured x Pos = 696.3

        # D25
        #gradient = get_angle_in_gradient_c([702], cropped_resize_width, FOV) # Test with manually measured x Pos = 702

        # T12
        #gradient = get_angle_in_gradient_c([619.9], cropped_resize_width, FOV) # Test with manually measured x Pos = 619.9

    else:
        raise Exception("Unknown camera id passed to score detection.")

    return gradient


def get_angle_in_gradient_a(processedDartTip, resizeWidth, fov):
    xPosBullCorrection = 577

    angle = find_angle(processedDartTip[0], resizeWidth, fov) - find_angle(xPosBullCorrection, resizeWidth, fov) + 30
    #angle = find_angle(processedDartTip[0], resizeWidth, fov) - find_angle(638.46, 1280, fov) - 30


    #print(f"adjusted Angle {angle}")

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

    #print(f"Gradient: {gradient}")

    return gradient


def get_angle_in_gradient_b(processedDartTip, resizeWidth, fov):
    xPosBullCorrection = 673
    
    angle = find_angle(processedDartTip[0], resizeWidth, fov) - find_angle(xPosBullCorrection, resizeWidth, fov) - 30
    #angle = find_angle(processedDartTip[0], resizeWidth, fov) - find_angle(630.769, 1280, fov) + 30


    #print(f"adjusted Angle {angle}")

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

    #print(f"Gradient: {gradient}")

    return gradient


def get_angle_in_gradient_c(processedDartTip, resizeWidth, fov):
    xPosBullCorrection = 702

    #angle = find_angle(processedDartTip[0], resizeWidth, fov) - find_angle(300, 650, fov)
    angle = find_angle(processedDartTip[0], resizeWidth, fov) - find_angle(xPosBullCorrection, resizeWidth, fov)


    #print(f"adjusted Angle {angle}")

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
    
    #print(f"Gradient: {gradient}")

    return gradient


def find_angle(x_position, width, FOV):
    # Returns the angle between the detected point and the center of the image
    x = x_position - width/2

    angle = math.atan((2*x*math.tan(math.radians(FOV/2)))/(width))
    angle = math.degrees(angle)
    
    #print(f"Angle: {angle}")

    return angle


def take_frame_of_dartboard_with_camera(camera_id:int):
    import platform

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