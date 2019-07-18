from __future__ import division
import cv2
import numpy as np

# video initiaization
cap = cv2.VideoCapture(1)
i=0
while True:
	# capture frame-by-frame
	_, main_frame = cap.read()

	# frame dimension before cropping
	height, width = main_frame.shape[:2]
	mid = width/2

	# crop frame of interest
	frame = main_frame[0:400, int(mid-300):int(mid+300)]

	# convert to HSV color space
	img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	
	# Gen lower mask (0-5) and upper mask (175-180) of RED
	mask1 = cv2.inRange(img_hsv, (0,50,20), (5,255,255))
	mask2 = cv2.inRange(img_hsv, (175,50,20), (180,255,255))

	# Merge the mask and crop the red regions
	mask = cv2.bitwise_or(mask1, mask2)
	
	## with noise
	#res_noise = cv2.bitwise_and(frame, frame, mask = mask)
	
	# Remove noise
	kernel_erode = np.ones((4,4), np.uint8)
	eroded_mask = cv2.erode(mask, kernel_erode, iterations=1)
	kernel_dilate = np.ones((6,6),np.uint8)
	dilated_mask = cv2.dilate(eroded_mask, kernel_dilate, iterations=1)

	res_red = cv2.bitwise_and(frame, frame, mask = dilated_mask)
	

	# coverting image with red colored region of interest from HSV to RGB
	frame_bgr_red = cv2.cvtColor(res_red, cv2.COLOR_HSV2BGR)

	# coverting image with black colored region of interest from RGB to GRAYSCALE
	frame_gray_red = cv2.cvtColor(frame_bgr_red, cv2.COLOR_BGR2GRAY)

	# Applying thresholding to the grayscale image for black & white color
	_, thresh_gray = cv2.threshold(frame_gray_red, 10,255, cv2.THRESH_OTSU+cv2.THRESH_BINARY_INV);

	# Find the different contours
	contours = cv2.findContours(thresh_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
	
	# Sort by area (keep only the biggest one)
	contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]

	if len(contours) > 0:
		M = cv2.moments(contours[0])

		if M['m00']!=0:
			# Centroid
			cx = int(M['m10']/M['m00'])
			cy = int(M['m01']/M['m00'])

		#print("Centroid of the biggest area: ({}, {})".format(cx, cy))
		# this divides the screen into 4 quadrants by intersecting 2 lines
		cv2.line(frame,(cx,0),(cx,height),(50,205,50),2)
		cv2.line(frame,(0,cy),(width,cy),(50,205,50),2)

		# draw the contour which is of interest only, i.e. path
		cv2.drawContours(thresh_gray, contours, -1, (0,255,0), 1)

		if cx >= 120:
			print ("Turn Right!")
		
		# if the centroid x coordinate cx is greater than 50 and less than 120 then this means that the path is on track 
		if cx < 120 and cx > 50:
			print ("On Track!")

		# if the centroid x coordinate cx is less than or equal to 50 then this means that the path is towards left 
		if cx <= 50:
			print ("Turn Left")

	else:
		print("No Centroid Found")

	cv2.imshow('original_frame',frame)
	#cv2.imshow('with noise', res_noise)
	cv2.imshow('res_red', res_red)
	cv2.imshow('frame_bgr_red', frame_bgr_red)
	cv2.imshow('frame_gray_red', frame_gray_red)
	cv2.imshow('thresh_frame', thresh_gray)
	#cv2.imwrite('image'+str(i)+'.png', thresh_black)
	i=i+1
	#print("image saved successfully!")
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()