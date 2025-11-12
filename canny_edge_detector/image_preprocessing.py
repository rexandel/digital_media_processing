import cv2


def image_preprocessing(path):
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grayscale_blur = cv2.GaussianBlur(grayscale, (19, 19), 3)

    cv2.imshow('Grayscale Image', grayscale)
    cv2.imshow('Blurred Grayscale Image', grayscale_blur)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    image_preprocessing(r"D:\GitHub\digital_media_processing\canny_edge_detector\images\respectable_cat.jpg")


if __name__ == "__main__":
    main()
