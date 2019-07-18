import numpy as np
import cv2
import serial
import time

# video initiaization
cap = cv2.VideoCapture(-1)
# video Frame Size initialization
cap.set(3, 160)
cap.set(4, 120)

# Arduino port initialization
ArduinoSerial = serial.Serial('COM14', 9600)
# Sleep of 2 seconds for initialization
time.sleep(2)

# whether the bot is running or not
isRunning = True
# variable that counts the no. of intersections
intersectionCount = 0


# Function to apply gaussian blur on the input image
def unsharp_mask(img, blur_size = (5,5), imgWeight = 1.5, gaussianWeight = -0.5):
    gaussian = cv2.GaussianBlur(img, blur_size, gaussianWeight)
    return cv2.addWeighted(img, imgWeight, gaussian, gaussianWeight, 0)

while(isRunning):
    global isRunning
    # Capture frame-by-frame
    ret, main_frame = cap.read()
    # Crop frame of interest
    frame = main_frame[60:120, 0:160]
    # Convert rgb image to HSV image
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #upper limit for selecting black color 
    upper_black = np.array([0,0,90], dtype=np.uint8)
    #lower limit for selecting black color
    lower_black = np.array([255,255,255], dtype=np.uint8)
    # 
    mask_black = cv2.inRange(frame_hsv, upper_black, lower_black)
    res_black = cv2.bitwise_and(frame,frame, mask= mask_black)

    # coverting image with black colored region of interest from HSV to RGB
    frame_bgr_black = cv2.cvtColor(res_black, cv2.COLOR_HSV2BGR)
    # coverting image with black colored region of interest from RGB to GRAYSCALE
    frame_gray_black = cv2.cvtColor(frame_bgr_black, cv2.COLOR_BGR2GRAY)
    # Applying thresholding to the grayscale image for black & white color
    aRet_black,thresh_black = cv2.threshold(frame_gray_black, 60,255, cv2.THRESH_BINARY_INV);
    # determing the contours in the image
    _, contours_black, _ = cv2.findContours(thresh_black.copy(), 0, cv2.CHAIN_APPROX_NONE)

    #upper limit for selecting green color 
    upper_green = np.array([80,255,255], dtype=np.uint8)
    #lower limit for selecting green color 
    lower_green = np.array([65,60,60], dtype=np.uint8)

    mask_red = cv2.inRange(frame_hsv, lower_green, upper_green)
    res_red = cv2.bitwise_and(frame,frame, mask= mask_red)

    # coverting image with green colored region of interest from HSV to RGB
    frame_bgr_red = cv2.cvtColor(res_red, cv2.COLOR_HSV2BGR)
    # coverting image with green colored region of interest from RGB to GRAYSCALE
    frame_gray_red = cv2.cvtColor(frame_bgr_red, cv2.COLOR_BGR2GRAY)
    # Applying thresholding to the grayscale image for green & white color
    aRet_red,thresh_red = cv2.threshold(frame_gray_red, 20, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU);
    # determing the contours in the image
    _, contours_red, _ = cv2.findContours(thresh_red.copy(), 0, cv2.CHAIN_APPROX_NONE)
    
    # if the no of contours in an image with green colored region of interest is greater than 1 then its a junction
    if len(contours_red)>1:
        # Arduino command to send signal for left turn at intersection
        ArduinoSerial.write('Y'.encode())
        print('Green Found')
        print('Intersection Found')
        # break

    # if the no of contours in an image with black colored region of interest is greater than 0 then its a track
    if len(contours_black) >= 0:
        # try-except is applied for Null value check for c, where c is the contour with max area
        try:
            c = max(contours_black, key=cv2.contourArea)
        except:
            print('contour error')

        # Properties of contours
        M = cv2.moments(c)

        # check if the denominator is 0 or not so as to avoid division by 0
        if M['m00']!=0:
            # cx & cy are the coordinates of the center of the screen (direction of movement is decided based on these only)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

        # this divides the screen into 4 quadrants by intersecting 2 lines
        cv2.line(thresh_black,(cx,0),(cx,720),(50,205,50),1)
        cv2.line(thresh_black,(0,cy),(1280,cy),(50,205,50),1)

        # draw the contour which is of interest only, i.e. path
        cv2.drawContours(thresh_black, contours_black, -1, (0,255,0), 1)

        # if the centroid x coordinate cx is greater than or equal to 120 then this means that the path is towards right 
        if cx >= 120:
            print ("Turn Right!")
            # Arduino command to send signal for slight right turn
            ArduinoSerial.write('R'.encode())
        
        # if the centroid x coordinate cx is greater than 50 and less than 120 then this means that the path is on track 
        if cx < 120 and cx > 50:

            print ("On Track!")
            i=0
            # Arduino command to send signal for on track movement
            ArduinoSerial.write('T'.encode())

        # if the centroid x coordinate cx is less than or equal to 50 then this means that the path is towards left 
        if cx <= 50:
            print ("Turn Left")
            # Arduino command to send signal for slight left turn
            ArduinoSerial.write('L'.encode())
    i+=1
    cv2.imshow('frame',thresh_black)
    cv2.imshow('frame0',frame)
    print()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()