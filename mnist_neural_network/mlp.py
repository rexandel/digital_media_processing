import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import keras
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical

# Загрузка данных MNIST
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Визуализация первых 9 изображений
plt.figure(figsize=(10, 10))
for i in range(9):
    plt.subplot(3, 3, i + 1)
    plt.imshow(x_train[i], cmap='gray')
    plt.title(f"Class {y_train[i]}")
    plt.axis('off')
plt.tight_layout()
plt.show()

# Информация о данных
print("x_train shape", x_train.shape)
print("y_train shape", y_train.shape)
print("x_test shape", x_test.shape)
print("y_test shape", y_test.shape)

n_train_images = x_train.shape[0]
n_test_images = x_test.shape[0]

# Предобработка данных
height = 28
width = 28
depth = 1

x_train = x_train.reshape(n_train_images, height * width * depth).astype(np.float32) / 255
x_test = x_test.reshape(n_test_images, height * width * depth).astype(np.float32) / 255

print("x_train shape after reshape:", x_train.shape)
print("x_test shape after reshape:", x_test.shape)

# Преобразование меток в one-hot encoding
n_classes = 10
y_train = to_categorical(y_train, n_classes)
y_test = to_categorical(y_test, n_classes)

# Создание модели MLP
hidden_size = 512

model = keras.Sequential()
model.add(keras.layers.Input(shape=(width * height,)))          # Входной слой
model.add(keras.layers.Dense(hidden_size, activation='relu'))   # 1-й скрытый слой (активация Rectified Linear Unit для нелинейных преобразований)
model.add(keras.layers.Dropout(0.2))                            # Дропаут для предотвращения переобучения
model.add(keras.layers.Dense(hidden_size, activation='relu'))   # 2-й скрытый слой
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Dense(n_classes, activation='softmax'))  # Активация softmax преобразует выходы в вероятности (сумма = 1)

# Компиляция модели с оптимизатором Adam
adam = keras.optimizers.Adam(learning_rate=0.001)
model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])

# Обучение модели
batch_size = 128
n_epochs = 50

save_path = f'checkpoints/MLP/ckpt_{len(model.layers)}' + '_epoch_{epoch:02d}.keras'
save_callback = keras.callbacks.ModelCheckpoint(save_path, verbose=1, monitor='val_accuracy', mode='max', save_best_only=True)

model.fit(x_train,
          y_train,
          batch_size=batch_size,
          epochs=n_epochs,
          verbose=1,
          validation_split=0.1,
          callbacks=[save_callback])

# Загрузка лучшей модели и оценка на тестовых данных
model = keras.saving.load_model("checkpoints/MLP/ckpt_5_512_epoch_44.keras")
score = model.evaluate(x_test, y_test, verbose=0, return_dict=True)
print("\nОценка модели на тестовых данных:", score)

# Предсказания и анализ ошибок
predicted_classes = model.predict(x_test)
correct_count = 0
print("\nОшибки:")
for index, image in enumerate(predicted_classes):
    probability = max(image)
    actual_number = np.where(y_test[index] == 1)[0][0]
    prediction = np.where(image == probability)[0][0]
    if actual_number != prediction:
        print(f'Правильное число: {actual_number}, предсказанное число: {prediction}, вероятность: {probability * 100:.2f}%')
    else:
        correct_count += 1

print(f'\n{correct_count} из {n_test_images} предсказаны верно')
print(f'Точность: {correct_count / n_test_images * 100:.2f}%')