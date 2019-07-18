from __future__ import division
import cv2
import numpy as np
import serial
import time
# calling header file which helps us use GPIO’s of PI
import RPi.GPIO as GPIO 

in1 = 24
in2 = 23
in3 = 22
in4 = 26
en1 = 12
en2 = 13
temp1=1
slowSpeed = 20
fastSpeed = 40



GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)
GPIO.setup(en1,GPIO.OUT)
GPIO.setup(en2,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)
p1=GPIO.PWM(en1,1000)
p2=GPIO.PWM(en2,1000)
p1.start(0)
p2.start(0)
print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("r-run s-stop f-forward b-backward l-low m-medium h-high e-exit")
print("\n")


i=0

# video initiaization
cap = cv2.VideoCapture(-1)
# video Frame Size initialization
cap.set(3, 160)
cap.set(4, 120)

# Sleep of 2 seconds for initialization
time.sleep(2)

# variable that counts the no. of intersections
intersectionCount = 0

def forwardRun():
    p1.ChangeDutyCycle(55)
    p2.ChangeDutyCycle(fastSpeed)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    GPIO.output(in3,GPIO.HIGH)
    GPIO.output(in4,GPIO.LOW)

def backwardRun():
    p1.ChangeDutyCycle(fastSpeed)
    p2.ChangeDutyCycle(fastSpeed)
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.HIGH)
    
    
def stop():
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.LOW)
    
def towardsRight():
    p1.ChangeDutyCycle(fastSpeed)
    p2.ChangeDutyCycle(0)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    GPIO.output(in3,GPIO.LOW)
    GPIO.output(in4,GPIO.LOW)

def towardsLeft():
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(fastSpeed)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)
    GPIO.output(in3,GPIO.HIGH)
    GPIO.output(in4,GPIO.LOW)

def slightLeft():
    p1.ChangeDutyCycle(slowSpeed)
    p2.ChangeDutyCycle(fastSpeed)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    GPIO.output(in3,GPIO.HIGH)
    GPIO.output(in4,GPIO.LOW)
    
def slightRight():
    p1.ChangeDutyCycle(fastSpeed)
    p2.ChangeDutyCycle(slowSpeed)
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    GPIO.output(in3,GPIO.HIGH)
    GPIO.output(in4,GPIO.LOW)
    
while True:
    # capture frame-by-frame
    _, main_frame = cap.read()
    if main_frame is None:
        break

	# frame dimension before cropping
    height, width = main_frame.shape[:2]
    mid = width/2

	# crop frame of interest
    frame = main_frame[0:400, int(mid-300):int(mid+300)]

	# blur the frame
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)

	# convert to HSV color space
    img_hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	
	# Gen lower mask (0-5) and upper mask (175-180) of RED
    mask1 = cv2.inRange(img_hsv, (0,50,20), (5,255,255))
    mask2 = cv2.inRange(img_hsv, (175,50,20), (180,255,255))

	# Merge the mask and crop the red regions
    mask = cv2.bitwise_or(mask1, mask2)
	
	## with noise
	#res_noise = cv2.bitwise_and(frame, frame, mask = mask)
	
	# Remove noise
    kernel_erode = np.ones((4,4), np.uint8)
    eroded_mask = cv2.erode(mask, kernel_erode, iterations=2)
    kernel_dilate = np.ones((6,6),np.uint8)
    dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=2)

    res_red = cv2.bitwise_and(frame, frame, mask = dilated_mask)
	
	# coverting image with red colored region of interest from HSV to RGB
    frame_bgr_red = cv2.cvtColor(res_red, cv2.COLOR_HSV2BGR)

	# coverting image with black colored region of interest from RGB to GRAYSCALE
    frame_gray_red = cv2.cvtColor(frame_bgr_red, cv2.COLOR_BGR2GRAY)

	# Applying thresholding to the grayscale image for black & white color
    _, thresh_gray = cv2.threshold(frame_gray_red, 10,255, cv2.THRESH_OTSU)

	# Find the different contours
    _, contours, _ = cv2.findContours(thresh_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	
	# Sort by area (keep only the biggest one)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

    if len(contours) > 0:
        M = cv2.moments(contours[0])
        if M['m00']!=0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

		#print("Centroid of the biggest area: ({}, {})".format(cx, cy))
		# this divides the screen into 4 quadrants by intersecting 2 lines
        cv2.line(frame,(cx,0),(cx,height),(50,205,50),2)
        cv2.line(frame,(0,cy),(width,cy),(50,205,50),2)

		# draw the contour which is of interest only, i.e. path
        cv2.drawContours(thresh_gray, contours, -1, (0,255,0), 1)
        if cx >= mid+150:
            print ("Turn Left!")
            slightLeft()
        if cx < mid+150 and cx > mid-150:
            print ("On Track!")
            i=0
            #forwardRun()
            backwardRun()
                
        if cx <= mid-150:
            print ("Turn Right!")
            slightRight()
                    

    else:
        stop()
        
    i = i+1

    cv2.imshow('original_frame',frame)
	#cv2.imshow('with noise', res_noise)
	# cv2.imshow('res_red', res_red)
	# cv2.imshow('frame_bgr_red', frame_bgr_red)
	# cv2.imshow('frame_gray_red', frame_gray_red)
    cv2.imshow('thresh_frame', thresh_gray)
	#cv2.imwrite('image'+str(i)+'.png', thresh_black)
	#print("image saved successfully!")
    if cv2.waitKey(1) & 0xFF == ord('q'):
    	break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()