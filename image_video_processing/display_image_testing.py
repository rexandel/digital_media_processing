import cv2

cat_image = cv2.imread(r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\images\cat.png", cv2.IMREAD_COLOR)
dafoe_image = cv2.imread(r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\images\willem_dafoe.webp", cv2.IMREAD_GRAYSCALE)
man_image = cv2.imread(r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\images\outraged_man.jpg", cv2.IMREAD_UNCHANGED)

cv2.namedWindow('Crazy Cat', cv2.WINDOW_NORMAL)
cv2.namedWindow('Willem Dafoe', cv2.WINDOW_FULLSCREEN)
cv2.namedWindow('Outraged man', cv2.WINDOW_KEEPRATIO)

cv2.imshow('Crazy Cat', cat_image)
cv2.imshow('Willem Dafoe', dafoe_image)
cv2.imshow('Outraged man', man_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
