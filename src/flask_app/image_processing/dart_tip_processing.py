import cv2
import numpy as np

def dart_tip_processing(processedImage):
    contours, hierarchy = cv2.findContours(processedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    returnvalue = 0
    contourLength = len(contours)
    #print(f"FindingDartTip:\nAnzahl detektierte Konturen = {contourLength}")
    if contourLength == 0:
        returnvalue = 0
    else:
        contoursSorted = sorted(contours, key = cv2.contourArea, reverse= True)
        contournumber = 0
        for contour in contoursSorted:
            contournumber += 1
            #print(f"\nKontur: {contournumber}") 
            size = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)

            if size > 10000:
                returnvalue = "Hand"
                #print("Hand")
                break
            elif size < 50:
                #print(f"size [{size}] < 50")
                continue
            elif h < w:
                #print(f"h [{h}] < w [{w}]")
                continue
            else:
                potential = tuple(contour[contour[:, :, 1].argmax()][0])
                thresh_for_high_y_coordinate = potential[1] - 2
                all_high_y_coordinates = contour[contour[:,:,1] >= thresh_for_high_y_coordinate]
                potential_all_mean = np.mean(all_high_y_coordinates, axis = 0)
                potential_all_mean = tuple(np.rint(potential_all_mean).astype(int))

                #print(f"mean potential: {potential_all_mean}")

                contourimage = processedImage.copy()
                cv2.rectangle(contourimage, (x,y), (x+w, y+h), (255,255,255), 1)
                #plt.show(plt.imshow(contourimage))
                
                cv2.line(contourimage, (0, potential_all_mean[1]), (contourimage.shape[1], potential_all_mean[1]),  color=(255, 255, 255), thickness=1)
                cv2.line(contourimage, (potential_all_mean[0], 0), (potential_all_mean[0], contourimage.shape[0]),  color=(255, 255, 255), thickness=1)
                #plt.show(plt.imshow(contourimage))

                if returnvalue != 0:
                    if returnvalue[1] < potential[1]:
                        returnvalue = potential
                        #print("set val to new potential")
                else:
                    returnvalue = potential
                    #print("set val to new potential")

    if returnvalue != 0 and returnvalue != "Hand":
        #print("Result of Find Dart Tip:")
        #plt.show(plt.imshow(processedImage))
        processedLineImage = processedImage.copy()
        cv2.line(processedLineImage, (0, returnvalue[1]), (processedLineImage.shape[1], returnvalue[1]),  color=(255, 255, 255), thickness=1)
        cv2.line(processedLineImage, (returnvalue[0], 0), (returnvalue[0], processedLineImage.shape[0]),  color=(255, 255, 255), thickness=1)
        #plt.show(plt.imshow(processedLineImage))

    return returnvalue