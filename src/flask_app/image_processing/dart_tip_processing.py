"""
This module provides the `dart_tip_processing` function, 
which analyzes contours in a binary (thresholded) image to identify the tip of a dart or detect the presence of a hand.
"""

import cv2
import numpy as np
#import matplotlib.pyplot as plt

def dart_tip_processing(processedImage):
    """
    Processes a pre-processed image to detect the tip of a dart or the presence of a hand.
    This function analyzes contours found in the input binary image to identify potential dart tips based on contour area and shape.
    
    :param processedImage: A binary (thresholded) image where the dart and/or hand are expected to be visible.
    :type processedImage: numpy.ndarray
    :return:
        tuple or str or int: 
        
            - (x, y): Coordinates of the detected dart tip if found.
            - "Hand": If a hand is detected in the image.
            - 0: If no suitable dart tip or hand is detected.
    """

    contours, hierarchy = cv2.findContours(processedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    returnvalue = 0
    contourLength = len(contours)

    if contourLength == 0:
        returnvalue = 0
    else:
        contoursSorted = sorted(contours, key = cv2.contourArea, reverse= True)

        for contour in contoursSorted:
            size = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)

            if size > 10000:
                returnvalue = "Hand"
                print("Hand detected")
                break
            elif size < 50:
                continue
            elif h < w:
                continue
            else:
                potential = tuple(contour[contour[:, :, 1].argmax()][0])
                thresh_for_high_y_coordinate = potential[1] - 2
                all_high_y_coordinates = contour[contour[:,:,1] >= thresh_for_high_y_coordinate]
                potential_all_mean = np.mean(all_high_y_coordinates, axis = 0)
                potential_all_mean = tuple(np.rint(potential_all_mean).astype(int))

                contourimage = processedImage.copy()
                cv2.rectangle(contourimage, (x,y), (x+w, y+h), (255,255,255), 1)                
                cv2.line(contourimage, (0, potential_all_mean[1]), (contourimage.shape[1], potential_all_mean[1]),  color=(255, 255, 255), thickness=1)
                cv2.line(contourimage, (potential_all_mean[0], 0), (potential_all_mean[0], contourimage.shape[0]),  color=(255, 255, 255), thickness=1)

                if returnvalue != 0:
                    if returnvalue[1] < potential[1]:
                        returnvalue = potential
                else:
                    returnvalue = potential

    print(f"Result of Find Dart Tip: {returnvalue}")

    #if returnvalue != 0 and returnvalue != "Hand":
    #    processedLineImage = processedImage.copy()
    #    cv2.line(processedLineImage, (0, returnvalue[1]), (processedLineImage.shape[1], returnvalue[1]),  color=(255, 255, 255), thickness=1)
    #    cv2.line(processedLineImage, (returnvalue[0], 0), (returnvalue[0], processedLineImage.shape[0]),  color=(255, 255, 255), thickness=1)
    #    plt.show(plt.imshow(processedLineImage))

    return returnvalue