import cv2
import os
import numpy as np

folder = r"C:\Users\rexandel\Desktop\GitHub\digital_media_processing\image_video_io_testing\videos"

camera = cv2.VideoCapture(0)
frame_w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

rectangles = np.array([
    [[  0, 140], [260, 180]],
    [[110,   0], [150, 140]],
    [[110, 180], [150, 320]]
])

max_x = max(rect[1][0] for rect in rectangles)
max_y = max(rect[1][1] for rect in rectangles)

offset_x = (frame_w - max_x) // 2
offset_y = (frame_h - max_y) // 2

fps = 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(os.path.join(folder, "camera_output.mp4"), fourcc, fps, (frame_w, frame_h))

while (True):
    ret, frame = camera.read()

    if not(ret):
        break

    x1, y1 = rectangles[0][0]
    x2, y2 = rectangles[0][1]
    
    mask = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
    mask = cv2.rectangle(mask, (x1 + offset_x, y1 + offset_y), (x2 + offset_x, y2 + offset_y), (255, 255, 255), -1)
    
    blur = cv2.GaussianBlur(frame, (63, 63), 0)
    frame[mask == 255] = blur[mask == 255]

    for rect in rectangles:
        x1, y1 = rect[0]
        x2, y2 = rect[1]
        cv2.rectangle(frame, (x1 + offset_x, y1 + offset_y), (x2 + offset_x, y2 + offset_y), (0, 0, 255), 2)

    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break
    
    video_writer.write(frame)

camera.release()
cv2.destroyAllWindows()
