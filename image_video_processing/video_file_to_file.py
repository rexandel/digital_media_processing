import cv2, os

folder = r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\videos"
video = cv2.VideoCapture(r"C:\Users\rexandel\Documents\GitHub\digital_media_processing\image_video_processing\videos\ronaldo.mp4", cv2.CAP_ANY)

fps = video.get(cv2.CAP_PROP_FPS)
w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(os.path.join(folder, "ronaldo_grayscale.mp4"), fourcc, fps, (w, h), isColor=False)

while(True):
    ret, frame = video.read()
    if not (ret):
        break

    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Grayscale Ronaldo', grayscale)

    video_writer.write(grayscale)

    if cv2.waitKey(4) & 0xFF == 27:
        break

video.release()
cv2.destroyAllWindows()
