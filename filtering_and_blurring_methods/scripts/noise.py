import numpy as np
import cv2


def add_salt_pepper_fast(image, noise_ratio=0.05):
    noisy_image = image.copy()
    height, width = image.shape[:2]
    
    num_noise_pixels = int(noise_ratio * height * width)
    salt_coords = [np.random.randint(0, height, num_noise_pixels), np.random.randint(0, width, num_noise_pixels)]
    pepper_coords = [np.random.randint(0, height, num_noise_pixels), np.random.randint(0, width, num_noise_pixels)]
    
    noisy_image[salt_coords[0], salt_coords[1]] = [255, 255, 255]
    noisy_image[pepper_coords[0], pepper_coords[1]] = [0, 0, 0]
    
    return noisy_image


img = cv2.imread(r'C:\Users\rexandel\Documents\GitHub\digital_media_processing\filtering_and_blurring_methods\images\cat_mini.png')
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

noisy_image = add_salt_pepper_fast(img, 0.05)
noisy_image_blur = cv2.GaussianBlur(noisy_image, (31, 31), 5)

cv2.imshow('Original Image', img)
cv2.imshow('Noisy Image', noisy_image)
cv2.imshow('Noisy Image (Blurred)', noisy_image_blur)

cv2.waitKey(0)
cv2.destroyAllWindows()
