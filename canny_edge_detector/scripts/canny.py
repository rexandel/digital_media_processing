import cv2
import numpy as np


def image_preprocessing(path):
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grayscale_blur = cv2.GaussianBlur(grayscale, (5, 5), 1)
    return grayscale_blur


def sobel_kernels():
    Gx = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ], dtype=np.float32)

    Gy = np.array([
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ], dtype=np.float32)

    return Gx, Gy


def sobel(img):
    Gx, Gy = sobel_kernels()
    kernel_size = 3
    padding_size = kernel_size // 2

    img_padded = cv2.copyMakeBorder(img, padding_size, padding_size, padding_size, padding_size, cv2.BORDER_REFLECT)

    height, width = img.shape
    grad_x = np.zeros_like(img, dtype=np.float32)
    grad_y = np.zeros_like(img, dtype=np.float32)

    for y in range(height):
        for x in range(width):
            val_x = 0
            val_y = 0

            y_padded = y + padding_size
            x_padded = x + padding_size

            for k in range(kernel_size):
                for l in range(kernel_size):
                    pixel = img_padded[y_padded + k - padding_size, x_padded + l - padding_size]
                    val_x += pixel * Gx[k, l]
                    val_y += pixel * Gy[k, l]

            grad_x[y, x] = val_x
            grad_y[y, x] = val_y

    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)

    return magnitude, grad_x, grad_y


def angle_num(x, y, tg):
    if x >= 0 and y <= 0:
        if tg < -2.414:
            return 0
        elif tg < -0.414:
            return 1
        else:
            return 2
            
    elif x >= 0 and y >= 0:
        if tg < 0.414:
            return 2
        elif tg < 2.414:
            return 3
        else:
            return 4
            
    elif x <= 0 and y >= 0:
        if tg < -2.414:
            return 4
        elif tg < -0.414:
            return 5
        else:
            return 6
            
    elif x <= 0 and y <= 0:
        if tg < 0.414:
            return 6
        elif tg < 2.414:
            return 7
        else:
            return 0
    else:
        return 0


def non_maximum_suppression(magnitude, grad_x, grad_y):
    tg = np.where(grad_x != 0, grad_y / grad_x, np.sign(grad_y) * np.inf)
    
    edges = np.zeros_like(magnitude, dtype=np.uint8)
    height, width = magnitude.shape
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            angle = angle_num(grad_x[y, x], grad_y[y, x], tg[y, x])
            
            if angle == 0 or angle == 4:
                neighbor1 = [y - 1, x]
                neighbor2 = [y + 1, x]
            elif angle == 1 or angle == 5:
                neighbor1 = [y - 1, x + 1]
                neighbor2 = [y + 1, x - 1]
            elif angle == 2 or angle == 6:
                neighbor1 = [y, x + 1]
                neighbor2 = [y, x - 1]
            elif angle == 3 or angle == 7:
                neighbor1 = [y + 1, x + 1]
                neighbor2 = [y - 1, x - 1]
            else:
                raise Exception('The angle is not defined')
            
            if magnitude[y, x] >= magnitude[neighbor1[0], neighbor1[1]] and magnitude[y, x] > magnitude[neighbor2[0], neighbor2[1]]:
                edges[y, x] = 255
    
    return edges


def double_threshold_filtering(edges, magnitude, low_percent, high_percent):
    max_grad_len = np.max(magnitude)
    low_level = int(max_grad_len * low_percent)
    high_level = int(max_grad_len * high_percent)

    for y in range(edges.shape[0]):
        for x in range(edges.shape[1]):
            if edges[y, x] > 0:
                if magnitude[y, x] < low_level:
                    edges[y, x] = 0
                elif magnitude[y, x] < high_level:
                    keep = False
                    for neighbor_y in (y - 1, y, y + 1):
                        for neighbor_x in (x - 1, x, x + 1):
                            if neighbor_y != y or neighbor_x != x:
                                if edges[neighbor_y, neighbor_x] > 0 and magnitude[neighbor_y, neighbor_x] >= high_level:
                                    keep = True
                    if not keep:
                        edges[y, x] = 0

    edges = (edges > 0).astype(np.uint8) * 255

    return edges


def canny(path, low_percent, high_percent):
    img_preprocessed = image_preprocessing(path)
    magnitude, grad_x, grad_y = sobel(img_preprocessed)

    nms_edges = non_maximum_suppression(magnitude, grad_x, grad_y)
    final_edges = double_threshold_filtering(nms_edges, magnitude, low_percent, high_percent)
    
    return final_edges


def main():
    path = r"D:\GitHub\digital_media_processing\canny_edge_detector\images\plate_number.png"
    
    low_percent = 0.25
    high_percent = 0.45
    
    img_preprocessed = image_preprocessing(path)
    magnitude, _, _ = sobel(img_preprocessed)
    
    homemade_canny = canny(path, low_percent, high_percent)
    opencv_canny = cv2.Canny(img_preprocessed, 25, 80)
    
    cv2.namedWindow('Preprocessed Image', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Sobel Magnitude', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Homemade Canny', cv2.WINDOW_NORMAL)
    cv2.namedWindow('OpenCV Canny', cv2.WINDOW_NORMAL)

    cv2.imshow('Preprocessed Image', img_preprocessed)
    cv2.imshow('Sobel Magnitude', magnitude)
    cv2.imshow('Homemade Canny', homemade_canny)
    cv2.imshow('OpenCV Canny', opencv_canny)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()