import cv2
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def update_image(frame):
    try:
        LowH = cv2.getTrackbarPos('H_MIN', 'Control')
        HighH = cv2.getTrackbarPos('H_MAX', 'Control')
        LowS = cv2.getTrackbarPos('S_MIN', 'Control')
        HighS = cv2.getTrackbarPos('S_MAX', 'Control')
        LowV = cv2.getTrackbarPos('V_MIN', 'Control')
        HighV = cv2.getTrackbarPos('V_MAX', 'Control')
        
        kernel = np.ones((17, 17), np.uint8)
        imgThresholded = cv2.inRange(frame, (LowH, LowS, LowV), (HighH, HighS, HighV))
        imgClosing = cv2.morphologyEx(imgThresholded, cv2.MORPH_CLOSE, kernel)

        moments = cv2.moments(imgClosing, True)
        dX = moments['m01']
        dY = moments['m10']
        dArea = moments['m00']

        print(f"Moment m01: {dX}\nMoment m10: {dY}\nArea: {dArea}\n")

        if dArea > 500:
            posX = int(dX / dArea)
            posY = int(dY / dArea)
            
            x, y, w, h = cv2.boundingRect(imgClosing)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 5)
            cv2.circle(frame, (posX, posY), 10, (0, 0, 0), -1)
        
        return imgThresholded, imgClosing, frame.copy()
    except Exception as e:
        print(f"Error in update_image: {e}")
        return None, None, None

def main():
    camera_url = os.getenv('IP_WEB_CAM')
    video = cv2.VideoCapture(camera_url)

    cv2.namedWindow('Control', cv2.WINDOW_NORMAL)

    LowH = 0
    HighH = 100
    LowS = 100
    HighS = 255
    LowV = 130
    HighV = 255

    cv2.createTrackbar('H_MIN', 'Control', LowH, 255, lambda x: None)
    cv2.createTrackbar('H_MAX', 'Control', HighH, 255, lambda x: None)
    cv2.createTrackbar('S_MIN', 'Control', LowS, 255, lambda x: None)
    cv2.createTrackbar('S_MAX', 'Control', HighS, 255, lambda x: None)
    cv2.createTrackbar('V_MIN', 'Control', LowV, 255, lambda x: None)
    cv2.createTrackbar('V_MAX', 'Control', HighV, 255, lambda x: None)

    cv2.namedWindow('Thresholded', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Thresholded + MORPH_CLOSE', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Original with Tracking', cv2.WINDOW_NORMAL)

    while True:
        ret, frame = video.read()
        if not (ret):
            break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)

        imgThresholded, imgClosing, tracked_frame = update_image(hsv)
        tracked = cv2.cvtColor(tracked_frame, cv2.COLOR_HSV2BGR_FULL)
        
        cv2.imshow('Thresholded', imgThresholded)
        cv2.imshow('Thresholded + MORPH_CLOSE', imgClosing)
        cv2.imshow('Original with Tracking', tracked)
        
        if cv2.waitKey(3) & 0xFF == 27:
            break
    
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()