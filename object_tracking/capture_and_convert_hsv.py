import cv2

video = cv2.VideoCapture(0)

while(True):
    ret, frame = video.read()
    if not (ret):
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)

    cv2.namedWindow('Camera (HSV)', cv2.WINDOW_NORMAL)
    cv2.imshow('Camera (HSV)', hsv)

    if cv2.waitKey(3) & 0xFF == 27:
        break

video.release()
cv2.destroyAllWindows()
