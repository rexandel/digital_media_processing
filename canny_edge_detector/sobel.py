import cv2
import numpy as np
import os


def image_preprocessing(path):
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grayscale_blur = cv2.GaussianBlur(grayscale, (19, 19), 3)

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


def sobel_filter(img):
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

    angle = np.arctan2(grad_y, grad_x)
    angle_degrees = np.degrees(angle)

    return magnitude, grad_x, grad_y, angle_degrees


def save_matrices_to_txt(path, magnitude, grad_x, grad_y, angle):
    np.set_printoptions(precision=4, suppress=True, linewidth=120)
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "magnitude.txt"), "w") as f:
        f.write("Magnitude Matrix:\n")
        np.savetxt(f, magnitude, fmt='%4d')
    
    with open(os.path.join(path, "grad_x.txt"), "w") as f:
        f.write("Gradient X Matrix:\n")
        np.savetxt(f, grad_x, fmt='%8.4f')
    
    with open(os.path.join(path, "grad_y.txt"), "w") as f:
        f.write("Gradient Y Matrix:\n")
        np.savetxt(f, grad_y, fmt='%8.4f')
    
    with open(os.path.join(path, "angle.txt"), "w") as f:
        f.write("Angle Matrix:\n")
        np.savetxt(f, angle, fmt='%8.4f')


def main():
    img_preprocessed = image_preprocessing(r"D:\GitHub\digital_media_processing\canny_edge_detector\images\respectable_cat.jpg")

    magnitude, grad_x, grad_y, angle = sobel_filter(img_preprocessed)

    save_matrices_to_txt(r"D:\GitHub\digital_media_processing\canny_edge_detector\matrices", magnitude, grad_x, grad_y, angle)
    
    grad_x_vis = cv2.convertScaleAbs(grad_x)
    grad_y_vis = cv2.convertScaleAbs(grad_y)

    cv2.imshow('Sobel Magnitude', magnitude)
    cv2.imshow('Gradient X', grad_x_vis)
    cv2.imshow('Gradient Y', grad_y_vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()