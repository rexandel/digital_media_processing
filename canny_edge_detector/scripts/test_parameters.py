import cv2
import numpy as np

def canny_with_thresholds(path, low_percent, high_percent, sigma):
    def image_preprocessing(path, sigma):
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel_size = 6 * sigma + 1
        grayscale_blur = cv2.GaussianBlur(grayscale, (kernel_size, kernel_size), sigma)
        return grayscale_blur

    def sobel_kernels():
        Gx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        Gy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
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
            if tg < -2.414: return 0
            elif tg < -0.414: return 1
            else: return 2
        elif x >= 0 and y >= 0:
            if tg < 0.414: return 2
            elif tg < 2.414: return 3
            else: return 4
        elif x <= 0 and y >= 0:
            if tg < -2.414: return 4
            elif tg < -0.414: return 5
            else: return 6
        elif x <= 0 and y <= 0:
            if tg < 0.414: return 6
            elif tg < 2.414: return 7
            else: return 0
        else: return 0

    def non_maximum_suppression(magnitude, grad_x, grad_y):
        tg = np.where(grad_x != 0, grad_y / grad_x, np.sign(grad_y) * np.inf)
        edges = np.zeros_like(magnitude, dtype=np.uint8)
        height, width = magnitude.shape
        
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                angle = angle_num(grad_x[y, x], grad_y[y, x], tg[y, x])
                
                if angle == 0 or angle == 4:
                    neighbor1 = [y, x - 1]
                    neighbor2 = [y, x + 1]
                elif angle == 1 or angle == 5:
                    neighbor1 = [y - 1, x + 1]
                    neighbor2 = [y + 1, x - 1]
                elif angle == 2 or angle == 6:
                    neighbor1 = [y - 1, x]
                    neighbor2 = [y + 1, x]
                elif angle == 3 or angle == 7:
                    neighbor1 = [y - 1, x - 1]
                    neighbor2 = [y + 1, x + 1]
                else:
                    neighbor1 = [y, x]
                    neighbor2 = [y, x]
                
                if (magnitude[y, x] >= magnitude[neighbor1[0], neighbor1[1]] and 
                    magnitude[y, x] >= magnitude[neighbor2[0], neighbor2[1]]):
                    edges[y, x] = magnitude[y, x]
        
        return edges

    def double_threshold_filtering(edges, magnitude, low_percent, high_percent):
        max_grad_len = np.max(magnitude)
        low_level = int(max_grad_len * low_percent)
        high_level = int(max_grad_len * high_percent)
        
        strong_edges = (edges >= high_level)
        weak_edges = (edges >= low_level) & (edges < high_level)
        
        final_edges = np.zeros_like(edges, dtype=np.uint8)
        final_edges[strong_edges] = 255
        
        height, width = edges.shape
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if weak_edges[y, x]:
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dy == 0 and dx == 0:
                                continue
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < height and 0 <= nx < width:
                                if strong_edges[ny, nx]:
                                    final_edges[y, x] = 255
                                    break
        
        return final_edges

    img_preprocessed = image_preprocessing(path, sigma)
    magnitude, grad_x, grad_y = sobel(img_preprocessed)
    nms_edges = non_maximum_suppression(magnitude, grad_x, grad_y)
    final_edges = double_threshold_filtering(nms_edges, magnitude, low_percent, high_percent)
    
    return final_edges


def threshold_selection(path, step=0.05):
    low_thresholds = np.arange(0.05, 0.95, step)
    high_thresholds = np.arange(0.05, 0.95, step)
    sigma_values = [1, 2, 3]
    
    combinations = []
    for sigma in sigma_values:
        for low_percent in low_thresholds:
            for high_percent in high_thresholds:
                if low_percent < high_percent:
                    combinations.append((low_percent, high_percent, sigma))
    
    print(f"Всего комбинаций для просмотра: {len(combinations)}")
    print("\nУправление:")
    print("SPACE - следующий результат")
    print("L - сохранить результат")
    print("ESC - завершить просмотр")

    saved_results = []
    current_index = 0
    
    while current_index < len(combinations):
        low_percent, high_percent, sigma = combinations[current_index]
        
        if sigma == 1:
            kernel_size = 7
        elif sigma == 2:
            kernel_size = 13
        elif sigma == 3:
            kernel_size = 19
        
        print(f"Текущая комбинация [{current_index + 1}/{len(combinations)}]: low={low_percent:.2f}, high={high_percent:.2f}, sigma={sigma}, kernel_size={kernel_size}")

        try:
            edges = canny_with_thresholds(path, low_percent, high_percent, sigma)
            
            window_title = f'Canny - low:{low_percent:.2f}, high:{high_percent:.2f}, sigma:{sigma}, ksize:{kernel_size}'
            cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
            cv2.imshow(window_title, edges)
            
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27:  # ESC - выход
                print("Завершение просмотра...")
                break
            elif key == 32:  # SPACE - следующий
                current_index += 1
            elif key == ord('l') or key == ord('L'):  # L - сохранить результат
                result_data = {
                    'edges': edges.copy(),
                    'low_threshold': low_percent,
                    'high_threshold': high_percent,
                    'sigma': sigma,
                    'kernel_size': kernel_size
                }
                saved_results.append(result_data)
                print(f"Сохранен результат {len(saved_results)}: low={low_percent:.2f}, high={high_percent:.2f}, sigma={sigma}, kernel_size={kernel_size}")
                current_index += 1
            
        except Exception as e:
            print(f"Ошибка для low: {low_percent:.2f}, high: {high_percent:.2f}, sigma: {sigma}: {e}")
            current_index += 1
    
    cv2.destroyAllWindows()
    
    if saved_results:
        print(f"\nСохранено результатов: {len(saved_results)}")
        for i, result in enumerate(saved_results, 1):
            print(f"Результат {i}: low={result['low_threshold']:.2f}, high={result['high_threshold']:.2f}, sigma={result['sigma']}, kernel_size={result['kernel_size']}")
            
    return saved_results


if __name__ == "__main__":
    path = r"D:\GitHub\digital_media_processing\canny_edge_detector\images\flower.jpg"
    
    saved_results = threshold_selection(path, step=0.05)