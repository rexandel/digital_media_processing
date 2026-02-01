# Digital Media Processing

Коллекция учебных и исследовательских проектов по цифровой обработке изображений, видео, аудио и цветов. Репозиторий содержит независимые подпроекты с наглядными визуализациями и скриптами для экспериментов.

## Содержание
- [Что внутри](#что-внутри)
- [Быстрый старт](#быстрый-старт)
- [Подпроекты](#подпроекты)
  - [Canny Edge Detector](#canny-edge-detector)
  - [Color Models (3D)](#color-models-3d)
  - [Filtering and Blurring Methods](#filtering-and-blurring-methods)
  - [Fourier Denoiser](#fourier-denoiser)
  - [Image & Video Processing](#image--video-processing)
  - [MNIST Neural Network](#mnist-neural-network)
  - [Object Tracking](#object-tracking)
- [Заметки по путям и данным](#заметки-по-путям-и-данным)

## Что внутри
- Реализация Canny детектора в Python и C# с поэтапной визуализацией.
- 3D‑визуализация цветовых моделей (RGB/HSV/HSL/YUV/XYZ/Lab/OKLab/CMY) на Three.js.
- Ручная реализация гауссова размытия и сравнение параметров ядра.
- GUI‑приложение для шумоподавления аудио с STFT/ISTFT и спектрограммами.
- Набор скриптов по работе с изображениями и видео.
- CNN для MNIST с обучением и анализом ошибок.
- Объектный трекинг на основе HSV‑порогов и морфологии.

## Быстрый старт
> Проекты независимы. Запускайте нужный подпроект, установив зависимости для Python.

### Python (общие зависимости)
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install numpy opencv-python matplotlib tensorflow keras sounddevice soundfile scipy python-dotenv
```

> Примечание: некоторые скрипты используют GUI (Tkinter) и доступ к камере/аудио.

## Подпроекты

### Canny Edge Detector
Пошаговая реализация детектора границ Canny. Есть версии на Python и C#.

**Пути:** [canny_edge_detector/](canny_edge_detector/)

**Запуск (Python):**
```bash
python canny_edge_detector/scripts/canny.py
```

### Color Models (3D)
Интерактивная 3D‑визуализация цветовых пространств на Three.js с переключением моделей.

**Пути:** [color_models/](color_models/)

**Запуск:**
```bash
python color_models/quick_start.py
```
Откройте браузер по адресу http://localhost:8000.

### Filtering and Blurring Methods
Ручная реализация гауссова размытия и сравнение параметров ядра.

**Пути:** [filtering_and_blurring_methods/](filtering_and_blurring_methods/)

**Запуск:**
```bash
python filtering_and_blurring_methods/scripts/gaussian_blur.py
```

### Fourier Denoiser
GUI‑приложение для шумоподавления шумов с помощью быстрого преобразования Фурье.

**Пути:** [fourier_denoiser/](fourier_denoiser/)

**Запуск:**
```bash
python fourier_denoiser/main.py
```

### Image & Video Processing
Скрипты для отображения, преобразования цветовых пространств, обработки видео и экспериментов с камерой.

**Пути:** [image_video_processing/](image_video_processing/)

**Пример запуска:**
```bash
python image_video_processing/scripts/video_display_processing.py
```

### MNIST Neural Network
CNN для классификации рукописных цифр MNIST: обучение, сохранение чекпоинтов, оценка качества и анализ ошибок.

**Пути:** [mnist_neural_network/](mnist_neural_network/)

**Запуск:**
```bash
python mnist_neural_network/cnn.py
```

### Object Tracking
HSV‑порогование, морфологические операции и отрисовка ограничивающего прямоугольника по контурам. Используется поток с IP‑камеры.

**Пути:** [object_tracking/](object_tracking/)

**Запуск:**
```bash
python object_tracking/detect_and_draw_bounding_box.py
```

## Заметки по путям и данным
- Часть скриптов содержит абсолютные пути к изображениям/видео. Обновите их под вашу систему.
- Для модулей, использующих IP‑камеру, создайте файл .env с переменной `IP_WEB_CAM`.
- Для корректной работы GUI‑скриптов убедитесь, что доступны дисплей и аудиоустройства.