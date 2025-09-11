import cv2
import os

folder = r"C:\Users\rexandel\Desktop\GitHub\digital_media_processing\image_video_io_testing\images"

print(folder)

img1 = cv2.imread(os.path.join(folder, 'cool_cat.png'), cv2.IMREAD_UNCHANGED)
img2 = cv2.imread(os.path.join(folder, 'crazy_cat.jpg'), cv2.IMREAD_ANYDEPTH)
img3 = cv2.imread(os.path.join(folder, 'flower_cat.webp'), cv2.IMREAD_GRAYSCALE)

cv2.namedWindow('cool_cat', cv2.WINDOW_NORMAL)
cv2.namedWindow('crazy_cat', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('flower_cat', cv2.WINDOW_FULLSCREEN)

cv2.imshow('cool_cat', img1)
cv2.imshow('crazy_cat', img2)
cv2.imshow('flower_cat', img3)

cv2.waitKey(0)
cv2.destroyAllWindows()
