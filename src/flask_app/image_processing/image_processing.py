import cv2
import skimage
import matplotlib.pyplot as plt
# from matplotlib.pyplot import savefig

def image_processing(blurred_diff_frame, camera_id):
    # Canny Algorithm
    can = cv2.Canny(blurred_diff_frame, 30, 90)
    #print("Canny Algorithm")
    #plt.show(plt.imshow(can))

    #print()

    # Return threshold value based on the triangle algorithm
    triangle_threshold = skimage.filters.threshold_triangle(blurred_diff_frame)
    #print(f"triangle_threshold: {triangle_threshold}")
    _, triangle = cv2.threshold(blurred_diff_frame, triangle_threshold, 255, cv2.THRESH_BINARY)
    #plt.show(plt.imshow(triangle))

    #print()

    # Return threshold value based on Yen´s method
    yen_threshold = skimage.filters.threshold_yen(blurred_diff_frame)
    #print(f"yen_threshold: {yen_threshold}")
    _, yen = cv2.threshold(blurred_diff_frame, yen_threshold, 255, cv2.THRESH_BINARY)
    #plt.show(plt.imshow(yen))

    #print()

    # Return threshold value based on Li´s iterative Minimum Cross Entropy method
    li_threshold = skimage.filters.threshold_li(blurred_diff_frame)
    #print(f"li_threshold: {li_threshold}")
    _, li = cv2.threshold(blurred_diff_frame, li_threshold, 255, cv2.THRESH_BINARY)
    #plt.show(plt.imshow(li))

    #print()

    # Skalierung der Werte in einem Bild (auch hin zu Absolutwerten)
    combined_threshs = (triangle/3) + (yen/3) + (li/3)
    #own try: combined_threshs = triangle / 2 + yen / 2
    #print(f"combined_thresh: {combined_threshs}" + "\n")
    combined_threshs = cv2.convertScaleAbs(combined_threshs)
    ret, all = cv2.threshold(combined_threshs, 150, 255, cv2.THRESH_BINARY)
    #plt.show(plt.imshow(all))

    #print()

    # Morphological operations to remove noise
    # kernels as ellipse with 3x5
    kernelOpen = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,5))
    kernelClose = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,5))

    # Anwendung der erzeugten Kernel auf das combined_thresh img
    morphological_kernelOpen = cv2.morphologyEx(all, cv2.MORPH_OPEN, kernelOpen)
    #print("Morphological kernel as ellipse 3x5 operations\nKernelOpen:")
    #plt.show(plt.imshow(morphological_kernelOpen))

    morphological_kernelClose = cv2.morphologyEx(morphological_kernelOpen, cv2.MORPH_CLOSE, kernelClose)
    #print("KernelClose:")
    #plt.show(plt.imshow(morphological_kernelClose))
    img_preprocessed = morphological_kernelClose

    # Berechnung threshold & Anwendung Open/Close - Kernel auf geglättetes Bild vom Anfang
    # mithilfe des übergebenen Parameters "thresh_val"
    thresh_val = 15
    #print(f"eingegangenes geglättetes Bild")
    #plt.show(plt.imshow(blurred_diff_frame))

    _, thresh = cv2.threshold(blurred_diff_frame, thresh_val, 255, cv2.THRESH_BINARY)
    #print("Anwendung threshold..")
    #plt.show(plt.imshow(thresh))

    #print()

    # Anwendung Open Kernel
    thresh_morph_kernelOpen = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernelOpen)
    #print("Anwendung Kernel Open")
    #plt.show(plt.imshow(thresh_morph_kernelOpen))

    #print()

    # Anwendung Close Kernel
    thresh_morph_kernelClose = cv2.morphologyEx(thresh_morph_kernelOpen, cv2.MORPH_CLOSE, kernelClose)
    #print("Anwendung Kernel Close")
    #plt.show(plt.imshow(thresh_morph_kernelClose))

    #print()

    # Combine thresholded image with Canny edge detector
    final = img_preprocessed | can
    
    # Save the final image
    # plt.imshow(final, cmap='gray')  # Ensure the image is displayed in grayscale
    # plt.axis('off')  # Turn off axes for better visualization
    # plt.savefig(f"logging/final_image_{camera_id}.jpg", bbox_inches='tight')  # Save the figure without extra whitespace
    # plt.close()  # Close the figure to free memory

    #print("Returns")
    # Returns:
    #print("final")
    #plt.show(plt.imshow(final))
    #print("thresh")
    #plt.show(plt.imshow(thresh_morph_kernelClose))

    return final, thresh_morph_kernelClose