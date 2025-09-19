import cv2

man_image_bgr = cv2.imread(r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\images\outraged_man.jpg", cv2.IMREAD_COLOR)
man_image_hsv = cv2.cvtColor(man_image_bgr, cv2.COLOR_BGR2HSV)

cv2.namedWindow('Outraged Man (BGR)', cv2.WINDOW_NORMAL)
cv2.namedWindow('Outraged Man (HSV)', cv2.WINDOW_NORMAL)

cv2.imshow('Outraged Man (BGR)', man_image_bgr)
cv2.imshow('Outraged Man (HSV)', man_image_hsv)

cv2.waitKey(0)
cv2.destroyAllWindows()
