import cv2
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

folder = r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\videos"
camera = cv2.VideoCapture(os.getenv('IP_WEB_CAM'))

if not camera.isOpened():
    print("Ошибка: Не удалось подключиться к камере")
    exit()

fps = camera.get(cv2.CAP_PROP_FPS)
w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(os.path.join(folder, "video_from_phone_camera.mp4"), fourcc, fps, (w, h))

while True:
    ret, frame = camera.read()
    if not ret:
        print("Ошибка: Не удалось получить кадр")
        break

    height = frame.shape[0]
    width = frame.shape[1]

    center_x = width // 2
    center_y = height // 2

    center_pixel = frame[center_y, center_x]
    max_color_index = np.argmax(center_pixel)
    print(f'BGR({center_pixel[0]}, {center_pixel[1]}, {center_pixel[2]})')
    color = [0, 0, 0]
    color[max_color_index] = 255

    mask = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.rectangle(mask, (center_x - 50, center_y - 25 // 2), (center_x + 50, center_y + 25 // 2), (255, 255, 255), -1)
    blur = cv2.GaussianBlur(frame, (63, 63), 0)
    frame[mask == 255] = blur[mask == 255]

    cv2.rectangle(frame, (center_x - 25 // 2, center_y - 50), (center_x + 25 // 2, center_y + 50), color, -1)
    cv2.rectangle(frame, (center_x - 50, center_y - 25 // 2), (center_x + 50, center_y + 25 // 2), color, -1)

    cv2.imshow('Video From Phone Camera', frame)
    video_writer.write(frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
video_writer.release()
cv2.destroyAllWindows()