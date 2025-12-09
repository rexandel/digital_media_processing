import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import keras
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical

# Загрузка данных MNIST
print("Загрузка данных MNIST...")
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Визуализация первых 9 изображений
print("Визуализация первых 9 изображений...")
for i in range(9):
    plt.subplot(3, 3, i+1)
    plt.imshow(x_train[i], cmap='gray')
    plt.title(f"Class {y_train[i]}")
plt.show()

# Вывод информации о форме данных
print("x_train shape", x_train.shape)
print("y_train shape", y_train.shape)
print("x_test shape", x_test.shape)
print("y_test shape", y_test.shape)

n_train_images = x_train.shape[0]
n_test_images = x_test.shape[0]

# Подготовка данных
height = 28
width = 28
depth = 1

x_train = x_train.reshape(n_train_images, height, width, depth).astype(np.float32) / 255
x_test = x_test.reshape(n_test_images, height, width, depth).astype(np.float32) / 255

print(x_train.shape)
print(x_test.shape)

# Преобразование меток в one-hot encoding
n_classes = 10
y_train = to_categorical(y_train, n_classes)
y_test = to_categorical(y_test, n_classes)

# Создание модели CNN
print("Создание модели CNN...")
model = keras.Sequential([
    keras.layers.Input(shape=(width, height, depth)),
    keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu"),
    keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation="relu"),
    keras.layers.MaxPooling2D(pool_size=(2, 2)),
    keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation="relu"),
    keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation="relu"),
    keras.layers.MaxPooling2D(pool_size=(2, 2)),
    keras.layers.Flatten(),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(n_classes, activation="softmax")
])

# Компиляция модели
print("Компиляция модели...")
adam = keras.optimizers.Adam(learning_rate=0.001)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Обучение модели
print("Обучение модели...")
batch_size = 128
n_epochs = 50

save_path = f'checkpoints/CNN/ckpt_{len(model.layers)}' + '_epoch_{epoch:02d}.keras'
save_callback = keras.callbacks.ModelCheckpoint(save_path, verbose=1, monitor='val_accuracy', mode='max', save_best_only=True)

history = model.fit(x_train,
                    y_train,
                    batch_size=batch_size,
                    epochs=n_epochs,
                    verbose=1,
                    validation_split=0.1,
                    callbacks=[save_callback])

# Оценка точности на тестовом датасете
print("Оценка точности на тестовом датасете...")

# Загрузка лучшей сохраненной модели
model = keras.saving.load_model("checkpoints/CNN/ckpt_5_512_epoch_44.keras")
score = model.evaluate(x_test, y_test, verbose=0, return_dict=True)
print(score)

# Предсказание и анализ ошибок
predicted_classes = model.predict(x_test)
correct_count = 0
print("Ошибки:")
for index, image in enumerate(predicted_classes):
    probability = max(image)
    actual_number = np.where(y_test[index] == 1)[0][0]
    prediction = np.where(image == probability)[0][0]
    if actual_number != prediction:
        print(f'Реальное число: {actual_number}, распознанное число: {prediction}, {probability * 100}%')
    else:
        correct_count += 1
print(f'\n{correct_count} из {n_test_images} распознано верно')