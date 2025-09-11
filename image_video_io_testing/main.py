import cv2
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
folder = r"C:\Users\rexandel\Desktop\GitHub\digital_media_processing\image_video_io_testing\videos"

camera = cv2.VideoCapture(os.getenv('IP_WEB_CAM') + "/video")
frame_w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

center_x = frame_w // 2
center_y = frame_h // 2

rectangles = np.array([
    [[  0, 140], [260, 180]],
    [[110,   0], [150, 140]],
    [[110, 180], [150, 320]]
])

max_x = max(rect[1][0] for rect in rectangles)
max_y = max(rect[1][1] for rect in rectangles)

offset_x = (frame_w - max_x) // 2
offset_y = (frame_h - max_y) // 2

while (True):
    ret, frame = camera.read()

    if not(ret):
        break

    center_pixel = frame[center_y][center_x]
    max_color_index = np.argmax(center_pixel)
    print(f'RGB({center_pixel[2]}, {center_pixel[1]}, {center_pixel[0]})')
    color = [0, 0, 0]
    color[max_color_index] = 255

    for rect in rectangles:
        x1, y1 = rect[0]
        x2, y2 = rect[1]
        cv2.rectangle(frame, (x1 + offset_x, y1 + offset_y), (x2 + offset_x, y2 + offset_y), color, -1)

    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()
