import cv2
import os
import numpy as np

folder = r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\videos"
video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    if not ret:
        break

    height = frame.shape[0]
    width = frame.shape[1]

    center_x = width // 2
    center_y = height // 2

    mask = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.rectangle(mask, (center_x - 50, center_y - 25 // 2), (center_x + 50, center_y + 25 // 2), (255, 255, 255), -1)
    blur = cv2.GaussianBlur(frame, (63, 63), 0)
    frame[mask == 255] = blur[mask == 255]

    cv2.rectangle(frame, (center_x - 25 // 2, center_y - 50), (center_x + 25 // 2, center_y + 50), (0, 0, 255), 5)
    cv2.rectangle(frame, (center_x - 50, center_y - 25 // 2), (center_x + 50, center_y + 25 // 2), (0, 0, 255), 5)

    cv2.imshow('Video From Camera', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

video.release()
cv2.destroyAllWindows()