import cv2
import os

folder = r"C:\Users\rexandel\Desktop\GitHub\digital_media_processing\image_video_io_testing\images"

print(folder)

img = cv2.imread(os.path.join(folder, 'cool_cat.png'))
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.namedWindow('cool_cat_rgb', cv2.WINDOW_NORMAL)
cv2.imshow('cool_cat_rgb', img)

cv2.namedWindow('cool_cat_hsv', cv2.WINDOW_NORMAL)
cv2.imshow('cool_cat_hsv', img_hsv)

cv2.waitKey(0)
cv2.destroyAllWindows()