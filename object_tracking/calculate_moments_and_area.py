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
        
        imgThresholded = cv2.inRange(frame, (LowH, LowS, LowV), (HighH, HighS, HighV))

        kernel = np.ones((17, 17), np.uint8)
        
        imgEroded = cv2.erode(imgThresholded, kernel)
        imgDilated = cv2.dilate(imgThresholded, kernel)
        
        imgOpening = cv2.morphologyEx(imgThresholded, cv2.MORPH_OPEN, kernel)
        imgClosing = cv2.morphologyEx(imgThresholded, cv2.MORPH_CLOSE, kernel)

        cv2.imshow('Thresholded', imgThresholded)
        cv2.imshow('Thresholded + Erode', imgEroded)
        cv2.imshow('Thresholded + Dilate', imgDilated)
        cv2.imshow('Thresholded + MORPH_OPEN', imgOpening)
        cv2.imshow('Thresholded + MORPH_CLOSE', imgClosing)

        moments = cv2.moments(imgClosing, True)
        dX = moments['m10']
        dY = moments['m01']
        dArea = moments['m00']

        print(f"Moment m10: {dX}\nMoment m01: {dY}\nArea: {dArea}\n")

    except:
        pass

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

    cv2.createTrackbar('H_MIN', 'Control', LowH, 255, update_image)
    cv2.createTrackbar('H_MAX', 'Control', HighH, 255, update_image)
    cv2.createTrackbar('S_MIN', 'Control', LowS, 255, update_image)
    cv2.createTrackbar('S_MAX', 'Control', HighS, 255, update_image)
    cv2.createTrackbar('V_MIN', 'Control', LowV, 255, update_image)
    cv2.createTrackbar('V_MAX', 'Control', HighV, 255, update_image)

    cv2.namedWindow('Thresholded', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Thresholded + Erode', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Thresholded + Dilate', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Thresholded + MORPH_OPEN', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Thresholded + MORPH_CLOSE', cv2.WINDOW_NORMAL)

    while True:
        ret, frame = video.read()
        if not (ret):
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)

        update_image(hsv)

        if cv2.waitKey(3) & 0xFF == 27:
            break
    
    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
