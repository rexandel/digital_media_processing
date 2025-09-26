import cv2
import os
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
        cv2.imshow('Thresholded', imgThresholded)
    except:
        pass

def main():
    camera_url = os.getenv('IP_WEB_CAM')
    video = cv2.VideoCapture(camera_url)

    cv2.namedWindow('Control', cv2.WINDOW_NORMAL)

    LowH = 0
    HighH = 100
    LowS = 50
    HighS = 255
    LowV = 200
    HighV = 255

    cv2.createTrackbar('H_MIN', 'Control', LowH, 255, update_image)
    cv2.createTrackbar('H_MAX', 'Control', HighH, 255, update_image)
    cv2.createTrackbar('S_MIN', 'Control', LowS, 255, update_image)
    cv2.createTrackbar('S_MAX', 'Control', HighS, 255, update_image)
    cv2.createTrackbar('V_MIN', 'Control', LowV, 255, update_image)
    cv2.createTrackbar('V_MAX', 'Control', HighV, 255, update_image)

    while True:
        ret, frame = video.read()
        if not (ret):
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)

        update_image(hsv)

        cv2.namedWindow('Original', cv2.WINDOW_NORMAL)
        cv2.imshow('Original', frame)

        cv2.namedWindow('HSV', cv2.WINDOW_NORMAL)
        cv2.imshow('HSV', hsv)

        if cv2.waitKey(3) & 0xFF == 27:
            break
    
    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
