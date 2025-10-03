import numpy as np
import cv2


def gauss(x, y, sigma, a, b):
    two_sigma_squared = 2 * sigma**2
    return np.exp(-((x - a)**2 + (y - b)**2) / two_sigma_squared) / (np.pi * two_sigma_squared)


def generate_kernel(kernel_size, std_deviation):
    kernel = np.zeros((kernel_size, kernel_size))
    a = b = kernel_size // 2
    
    for y in range(kernel_size):
        for x in range(kernel_size):
            kernel[y, x] = gauss(x, y, std_deviation, a, b)

    kernel /= np.sum(kernel)
    return kernel


def gaussian_blur(img, kernel_size, std_deviation):
    kernel = generate_kernel(kernel_size, std_deviation)

    padding_size = kernel_size // 2
    img_padded = cv2.copyMakeBorder(img, padding_size, padding_size, padding_size, padding_size, cv2.BORDER_REFLECT)

    blurred = img.copy()
    height, width, channels = img.shape
    
    for c in range(channels):
        for y in range(height):
            for x in range(width):
                y_padded = y + padding_size
                x_padded = x + padding_size
                
                val = 0
                for k in range(kernel_size):
                    for l in range(kernel_size):
                        val += img_padded[y_padded + k - padding_size, x_padded + l - padding_size, c] * kernel[k, l]
                
                blurred[y, x, c] = val
    
    return blurred


def main():
    kernel_size = 19
    std_deviation = 3

    img = cv2.imread(r'C:\Users\rexandel\Documents\GitHub\digital_media_processing\filtering_and_blurring_methods\images\cat_mini.png')

    if kernel_size % 2 == 0:
        print('Size of kernel matrix must be odd. Program will terminate with an error')
        exit(1)

    img_blur = gaussian_blur(img, kernel_size, std_deviation)
    img_blur_library = cv2.GaussianBlur(img, (kernel_size, kernel_size), std_deviation)

    cv2.imshow('Original', img)
    cv2.imshow('Gaussian Blur', img_blur)
    cv2.imshow('Gaussian Blur (CV2)', img_blur_library)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
