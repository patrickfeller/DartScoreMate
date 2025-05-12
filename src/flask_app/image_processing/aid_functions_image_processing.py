import cv2

def cropp_image_frame(frame, resize_width, resize_height, cropped_height):
    #print("Readed Frame")
    #readed_frame = plt.imshow(frame)
    #plt.show(readed_frame)

    # resized image
    resizedFrame = cv2.resize(frame, (resize_width, resize_height))
    #print("ResizedTestFrame")
    #resizedTestFrame = plt.imshow(resizedFrame)
    #plt.show(resizedTestFrame)

    # cropped image
    #croppedFrame = resizedFrame[croppedHeight:480, 300:950]
    croppedFrame = resizedFrame
    #print("CroppedTestFrame")
    #CroppedTestFrame = plt.imshow(croppedFrame)
    #plt.show(CroppedTestFrame)

    return croppedFrame


def create_frame_difference(basis_frame, detect_dart_frame, median_filter_kernel_size = 5):
    # Berechnung absolute Differenz zwischen den übergebenen Bildern
    diff = cv2.absdiff(basis_frame, detect_dart_frame)
    #print("calculating difference")
    #plt.show(plt.imshow(diff))
    #print()

    # Umwandlung Farbformat von RGB nach Graustufen
    grayscale = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    #print("converted img from rgb to gray")
    #plt.show(plt.imshow(grayscale))
    #print()

    # Bildglättung mit Medianfilter mit ksize-Filterfenstergröße
    blurred = cv2.medianBlur(grayscale, median_filter_kernel_size)
    #print(f"geglättetes Bild mit Kernelgröße: {medianfilterkernelsize}")
    #plt.show(plt.imshow(blurred))
    #print()

    return blurred