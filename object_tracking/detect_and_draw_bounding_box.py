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
        
        kernel = np.ones((3, 3), np.uint8)
        imgThresholded = cv2.inRange(frame, (LowH, LowS, LowV), (HighH, HighS, HighV))
        imgClosing = cv2.morphologyEx(imgThresholded, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(imgClosing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            for element in contours:
                if cv2.contourArea(element) > 500:
                    moments = cv2.moments(element)
                    dX = moments['m10']
                    dY = moments['m01']
                    dArea = moments['m00']

                    print(f"Moment m10: {dX}\nMoment m01: {dY}\nArea: {dArea}\n")

                    posX = int(dX / dArea)
                    posY = int(dY / dArea)
                    
                    x, y, w, h = cv2.boundingRect(element)

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 5)
                    cv2.circle(frame, (posX, posY), 10, (0, 0, 0), -1)
            return imgThresholded, imgClosing, frame.copy()
        else:
            return imgThresholded, imgClosing, None
        
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

    cv2.createTrackbar('H_MIN', 'Control', LowH, 255, update_image)
    cv2.createTrackbar('H_MAX', 'Control', HighH, 255, update_image)
    cv2.createTrackbar('S_MIN', 'Control', LowS, 255, update_image)
    cv2.createTrackbar('S_MAX', 'Control', HighS, 255, update_image)
    cv2.createTrackbar('V_MIN', 'Control', LowV, 255, update_image)
    cv2.createTrackbar('V_MAX', 'Control', HighV, 255, update_image)

    cv2.namedWindow('Thresholded', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Thresholded + MORPH_CLOSE', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Original with Tracking', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Original', cv2.WINDOW_NORMAL)

    while True:
        ret, frame = video.read()
        if not (ret):
            break
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)

        imgThresholded, imgClosing, tracked_frame = update_image(hsv)

        if tracked_frame is None:
            cv2.imshow('Thresholded', imgThresholded)
            cv2.imshow('Thresholded + MORPH_CLOSE', imgClosing)
            cv2.imshow('Original with Tracking', np.zeros_like(frame[:,:,0]))
            cv2.imshow('Original', frame)
        else:
            tracked = cv2.cvtColor(tracked_frame, cv2.COLOR_HSV2BGR_FULL)
            cv2.imshow('Thresholded', imgThresholded)
            cv2.imshow('Thresholded + MORPH_CLOSE', imgClosing)
            cv2.imshow('Original with Tracking', tracked)
            cv2.imshow('Original', frame)

        if cv2.waitKey(3) & 0xFF == 27:
            break
    
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()