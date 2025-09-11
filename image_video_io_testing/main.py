import cv2
import os
import time

folder = r"C:\Users\rexandel\Desktop\GitHub\digital_media_processing\image_video_io_testing\videos"

video = cv2.VideoCapture(os.path.join(folder, 'rick_roll.mp4'), cv2.CAP_ANY)

fps = video.get(cv2.CAP_PROP_FPS)

w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_writer = cv2.VideoWriter(os.path.join(folder, "rick_roll_grayscale.mov"), fourcc, fps, (w, h), isColor=False)


while (True):
    now = time.time()
    ret, frame = video.read()

    if not(ret):
        break
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break
    
    timeDiff = time.time() - now
    if (timeDiff < 1.0/(fps)):
        time.sleep(1.0/(fps) - timeDiff)
    
    video_writer.write(frame)

video.release()
cv2.destroyAllWindows()