import cv2
import numpy as np
import keras

def main():
    model = keras.saving.load_model(r"D:\GitHub\digital_media_processing\mnist_neural_network\best.keras")

    window_name = 'Draw A Number'
    scale = 15
    
    drawing = False
    pt1_x, pt1_y = 0, 0
    
    def line_drawing(event, x, y, flags, param):
        nonlocal drawing, pt1_x, pt1_y
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            pt1_x, pt1_y = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                cv2.line(img, (pt1_x, pt1_y), (x, y), color=(255, 255, 255), thickness=int(scale))
                pt1_x, pt1_y = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            cv2.line(img, (pt1_x, pt1_y), (x, y), color=(255, 255, 255), thickness=int(scale))
    
    img = np.zeros((28 * scale, 28 * scale), np.uint8)
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, line_drawing)
    
    while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) == 1:
        cv2.imshow(window_name, img)
        key = cv2.waitKey(10) & 0xFF
        
        if key == 27:  # escape
            break
        elif key == 0 or key == 8:  # del or backspace
            img[:,:] = 0
            cv2.setWindowTitle(window_name, window_name)
        elif key == 13 or key == 32:  # enter or space
            if img.max() > 0:
                model_input = img.copy()
                model_input = cv2.resize(model_input, (28, 28))
                model_input = model_input[np.newaxis, ..., np.newaxis]
                model_input = model_input.astype(np.float32) / 255
                
                pred = model.predict(model_input, verbose=0, batch_size=1)[0]
                result = np.where(pred == max(pred))[0][0]
                confidence = int(max(pred) * 100)
                
                cv2.setWindowTitle(window_name, f'I\'m {confidence}% sure the number is {result}')
    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()