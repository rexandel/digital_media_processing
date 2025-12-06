import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tkinter as tk
from tkinter import filedialog

class AudioRecorder:
    def __init__(self, samplerate=44100):
        self.samplerate = samplerate
    
    def record_audio(self, duration=10):
        print(f"Запись началась... ({duration} секунд)")
        
        audio = sd.rec(int(duration * self.samplerate), 
                      samplerate=self.samplerate, 
                      channels=1, 
                      dtype='float32')
        
        sd.wait()
        print("Запись завершена")
        
        audio_int16 = (audio * 32767).astype(np.int16)
        
        return audio_int16
    
    def save_audio_with_dialog(self, audio_data, parent_window=None):
        if parent_window is None:
            root = tk.Tk()
            root.withdraw()
            parent = root
        else:
            parent = parent_window
        
        filename = filedialog.asksaveasfilename(
            parent=parent,
            title="Сохранить аудиозапись",
            defaultextension=".wav",
            filetypes=[
                ("Wave files", "*.wav"),
                ("Все файлы", "*.*")
            ],
            initialfile="record.wav"
        )
        
        if filename:
            wav.write(filename, self.samplerate, audio_data)
            print(f"Аудио сохранено как {filename}")
            return filename
        else:
            print("Сохранение отменено")
            return None