import cv2

video = cv2.VideoCapture(r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\videos\ronaldo.mp4", cv2.CAP_ANY)

while(True):
    ret, frame = video.read()
    if not (ret):
        break

    frame = cv2.resize(frame, (800, 500))

    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    cv2.imshow('Grayscale Ronaldo', grayscale)
    cv2.imshow('HSV Ronaldo', hsv)

    if cv2.waitKey(3) & 0xFF == 27:
        break

cv2.destroyAllWindows()
