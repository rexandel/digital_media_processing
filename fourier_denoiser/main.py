import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import soundfile as sf
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from audio_enhancer import AudioEnhancer
from audio_recorder import AudioRecorder
from signal_overlay_viewer import SignalOverlayViewer
from spectrogram_viewer import SpectrogramViewer


class DenoiserApp:
    def __init__(self, root):
        self.root = root
        root.title("Noise Suppressor")

        self.in_path = None
        self.orig_data = None
        self.orig_sr = None
        self.result_data = None
        self.result_sr = None
        
        self.spectrogram_windows = {
            'original': None,
            'result': None
        }
        
        self.signal_overlay_window = None
        
        self.enhancer = AudioEnhancer()
        self.recorder = AudioRecorder()

        self.q = queue.Queue()

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        record_load_frame = ttk.LabelFrame(frm, text="Запись и загрузка", padding=8)
        record_load_frame.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        record_load_frame.columnconfigure(1, weight=1)
        
        ttk.Label(record_load_frame, text="Длительность записи (сек):").grid(row=0, column=0, sticky="w")
        self.var_record_duration = tk.StringVar(value="10")
        ttk.Entry(record_load_frame, textvariable=self.var_record_duration, width=8).grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        btn_record = ttk.Button(record_load_frame, text="Записать аудио", command=self.record_audio)
        btn_record.grid(row=0, column=2, padx=5)
        
        btn_browse = ttk.Button(record_load_frame, text="Загрузить файл...", command=self.browse_file)
        btn_browse.grid(row=0, column=3, padx=5)
        
        self.lbl_file = ttk.Label(record_load_frame, text="Файл не выбран")
        self.lbl_file.grid(row=1, column=0, columnspan=4, sticky="w", pady=(10, 0))

        params_frame = ttk.LabelFrame(frm, text="Параметры улучшения", padding=8)
        params_frame.grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        for i in range(4):
            params_frame.columnconfigure(i, weight=1)

        ttk.Label(params_frame, text="Размер окна STFT:").grid(row=0, column=0, sticky="w")
        self.var_window_size = tk.StringVar(value="2048")
        ttk.Entry(params_frame, textvariable=self.var_window_size, width=8).grid(row=0, column=1, sticky="w")

        ttk.Label(params_frame, text="Шаг окна (hop):").grid(row=0, column=2, sticky="w")
        self.var_hop_length = tk.StringVar(value="512")
        ttk.Entry(params_frame, textvariable=self.var_hop_length, width=8).grid(row=0, column=3, sticky="w")

        ttk.Label(params_frame, text="Оконная функция:").grid(row=1, column=0, sticky="w", pady=(6,0))
        self.var_window_type = tk.StringVar(value="Ханн")
        window_combo = ttk.Combobox(
            params_frame, 
            textvariable=self.var_window_type, 
            values=['Ханн', 'Хэмминг', 'Блэкман', 'Бартлетт', 'Кайзер'],
            width=10,
            state="readonly"
        )
        window_combo.grid(row=1, column=1, sticky="w", pady=(6,0))

        ttk.Label(params_frame, text="Количество кадров для оценки шума:").grid(row=2, column=0, sticky="w", pady=(6,0))
        self.var_noise_frames = tk.StringVar(value="256")
        ttk.Entry(params_frame, textvariable=self.var_noise_frames, width=8).grid(row=2, column=1, sticky="w", pady=(6,0))

        ttk.Label(params_frame, text="Сила подавления шума:").grid(row=2, column=2, sticky="w", pady=(6,0))
        self.var_reduction_strength = tk.StringVar(value="16")
        ttk.Entry(params_frame, textvariable=self.var_reduction_strength, width=8).grid(row=2, column=3, sticky="w", pady=(6,0))

        ttk.Label(params_frame, text="Минимальный уровень спектра:").grid(row=3, column=0, sticky="w", pady=(6,0))
        self.var_spectral_floor = tk.StringVar(value="0.15")
        ttk.Entry(params_frame, textvariable=self.var_spectral_floor, width=8).grid(row=3, column=1, sticky="w", pady=(6,0))

        self.var_use_numpy_fft = tk.BooleanVar(value=False)
        chk_numpy_fft = ttk.Checkbutton(
            params_frame,
            text="Использовать встроенный NumPy FFT",
            variable=self.var_use_numpy_fft
        )
        chk_numpy_fft.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 0))

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=4, pady=6)
        btn_frame.columnconfigure((0,1,2,3,4,5,6,7,8), weight=1)

        self.btn_play_orig = ttk.Button(btn_frame, text="Прослушать исходный", command=self.play_original, state="disabled")
        self.btn_play_orig.grid(row=0, column=0, padx=3)

        self.btn_stop_play = ttk.Button(btn_frame, text="Остановить воспроизведение", command=self.stop_playback, state="disabled")
        self.btn_stop_play.grid(row=0, column=1, padx=3)

        self.btn_spectrogram_orig = ttk.Button(btn_frame, text="Спектрограмма до", command=self.show_original_spectrogram, state="disabled")
        self.btn_spectrogram_orig.grid(row=0, column=2, padx=3)

        self.btn_process = ttk.Button(btn_frame, text="Улучшить качество", command=self.start_processing, state="disabled")
        self.btn_process.grid(row=0, column=3, padx=3)

        self.btn_play_result = ttk.Button(btn_frame, text="Прослушать результат", command=self.play_result, state="disabled")
        self.btn_play_result.grid(row=0, column=4, padx=3)

        self.btn_spectrogram_result = ttk.Button(btn_frame, text="Спектрограмма после", command=self.show_result_spectrogram, state="disabled")
        self.btn_spectrogram_result.grid(row=0, column=5, padx=3)

        self.btn_show_overlay = ttk.Button(btn_frame, text="Наложение сигналов", command=self.show_signal_overlay, state="disabled")
        self.btn_show_overlay.grid(row=0, column=6, padx=3)

        self.btn_save = ttk.Button(btn_frame, text="Сохранить результат...", command=self.save_result, state="disabled")
        self.btn_save.grid(row=0, column=7, padx=3)

        status_frame = ttk.Frame(frm)
        status_frame.grid(row=3, column=0, sticky="ew", padx=4, pady=(0,8))
        status_frame.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Готово")
        self.lbl_status = ttk.Label(status_frame, textvariable=self.status_var, anchor="w")
        self.lbl_status.grid(row=0, column=0, sticky="ew")

        self.root.after(200, self._process_queue)

        self._play_thread = None
        self._play_stop = threading.Event()

    def show_original_spectrogram(self):
        if self.orig_data is None:
            return
            
        if self.spectrogram_windows['original'] is not None:
            try:
                self.spectrogram_windows['original'].close()
            except:
                pass
        
        self.spectrogram_windows['original'] = SpectrogramViewer(
            self.root, 
            title="Спектрограмма исходного аудио"
        )
        
        try:
            max_samples = min(len(self.orig_data), self.orig_sr * 5)
            audio_to_show = self.orig_data[:max_samples]
            
            self.spectrogram_windows['original'].show_spectrogram(
                audio_to_show, 
                self.orig_sr,
                title=f"Спектрограмма исходного аудио\n{len(audio_to_show)} samples, {self.orig_sr} Hz",
                cmap='plasma'
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить спектрограмму: {e}")

    def show_result_spectrogram(self):
        if self.result_data is None:
            return
            
        if self.spectrogram_windows['result'] is not None:
            try:
                self.spectrogram_windows['result'].close()
            except:
                pass
        
        self.spectrogram_windows['result'] = SpectrogramViewer(
            self.root, 
            title="Спектрограмма обработанного аудио"
        )
        
        try:
            max_samples = min(len(self.result_data), self.result_sr * 5)
            audio_to_show = self.result_data[:max_samples]
            
            self.spectrogram_windows['result'].show_spectrogram(
                audio_to_show, 
                self.result_sr,
                title=f"Спектрограмма обработанного аудио\n{len(audio_to_show)} samples, {self.result_sr} Hz",
                cmap='viridis'
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить спектрограмму: {e}")

    def show_signal_overlay(self):
        if self.orig_data is None or self.result_data is None:
            return
            
        if self.signal_overlay_window is not None:
            try:
                self.signal_overlay_window.close()
            except:
                pass
        
        self.signal_overlay_window = SignalOverlayViewer(
            self.root, 
            title="Наложение сигналов: оригинал vs обработанный"
        )
        
        try:
            max_samples = min(len(self.orig_data), len(self.result_data), self.orig_sr * 10)
            orig_to_show = self.orig_data[:max_samples]
            result_to_show = self.result_data[:max_samples]
            
            min_len = min(len(orig_to_show), len(result_to_show))
            orig_to_show = orig_to_show[:min_len]
            result_to_show = result_to_show[:min_len]
            
            self.signal_overlay_window.show_signals(
                orig_to_show, 
                result_to_show,
                self.orig_sr,
                title=f"Сравнение сигналов ({min_len} samples, {self.orig_sr} Hz)"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график: {e}")

    def record_audio(self):
        try:
            duration = float(self.var_record_duration.get())
            if duration <= 0:
                raise ValueError("Длительность должна быть больше 0")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверная длительность записи: {e}")
            return
        
        self.status_var.set(f"Запись аудио ({duration} сек)...")
        t = threading.Thread(target=self._recording_worker, args=(duration,), daemon=True)
        t.start()

    def _recording_worker(self, duration):
        try:
            audio_int16 = self.recorder.record_audio(duration)
            
            filename = self.recorder.save_audio_with_dialog(audio_int16, self.root)
            
            if filename:
                data, sr = sf.read(filename, always_2d=False)
                
                self.in_path = filename
                if data.ndim > 1:
                    data = data.mean(axis=1)
                self.orig_data = data.astype(np.float32)
                self.orig_sr = sr
                self.result_data = None
                self.result_sr = None
                
                self.q.put(("info", f"Аудио записано и сохранено: {filename}"))
                self.q.put(("file_loaded", ""))
            else:
                self.q.put(("info", "Запись отменена"))
                
        except Exception as e:
            self.q.put(("error", f"Ошибка записи: {e}"))

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Выберите аудиофайл", 
            filetypes=[
                ("Audio files", "*.wav *.flac *.aiff *.aif *.ogg *.mp3"), 
                ("All files", "*.*")
            ]
        )
        if not path:
            return
        try:
            data, sr = sf.read(path, always_2d=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            return

        self.in_path = path
        if data.ndim > 1:
            data = data.mean(axis=1)
        self.orig_data = data.astype(np.float32)
        self.orig_sr = sr
        self.result_data = None
        self.result_sr = None

        self.lbl_file.config(text=f"{path} — {self.orig_data.shape} samples, {sr} Hz")
        self._update_buttons_state()
        self.status_var.set("Файл загружен")

    def _playback_worker(self, data: np.ndarray, sr: int):
        try:
            sd.stop()
            self._play_stop.clear()
            self.btn_stop_play.config(state="normal")
            to_play = np.array(data, dtype=np.float32)
            sd.play(to_play, sr)
            while sd.get_stream() is not None and sd.get_stream().active:
                if self._play_stop.is_set():
                    sd.stop()
                    break
                sd.sleep(100)
        except Exception as e:
            self.q.put(("error", f"Ошибка воспроизведения: {e}"))
        finally:
            self.q.put(("info", "Воспроизведение завершено"))
            self.btn_stop_play.config(state="disabled")

    def play_original(self):
        if self.orig_data is None:
            return
        self.status_var.set("Воспроизведение исходного...")
        self._start_play_thread(self.orig_data, self.orig_sr)

    def play_result(self):
        if self.result_data is None:
            return
        self.status_var.set("Воспроизведение результата...")
        self._start_play_thread(self.result_data, self.result_sr)

    def _start_play_thread(self, data, sr):
        if self._play_thread and self._play_thread.is_alive():
            self._play_stop.set()
            try:
                sd.stop()
            except Exception:
                pass
            self._play_thread.join(timeout=0.5)

        self._play_stop.clear()
        self._play_thread = threading.Thread(target=self._playback_worker, args=(data, sr), daemon=True)
        self._play_thread.start()

    def stop_playback(self):
        if self._play_thread and self._play_thread.is_alive():
            self._play_stop.set()
            try:
                sd.stop()
            except Exception:
                pass
            self.status_var.set("Остановлено")

    def start_processing(self):
        if self.orig_data is None:
            messagebox.showwarning("Нет файла", "Сначала загрузите или запишите аудио.")
            return
        
        try:
            window_size = int(self.var_window_size.get())
            if window_size <= 0 or (window_size & (window_size - 1)) != 0:
                raise ValueError("Размер окна должен быть степенью двойки > 0")
        except Exception as e:
            messagebox.showerror("Неверный параметр", f"Размер окна неверен: {e}")
            return

        try:
            hop_length = int(self.var_hop_length.get())
            if hop_length <= 0 or hop_length > window_size:
                raise ValueError("Шаг окна должен быть > 0 и меньше размера окна")
        except Exception as e:
            messagebox.showerror("Неверный параметр", f"Шаг окна неверен: {e}")
            return

        try:
            noise_frames = int(self.var_noise_frames.get())
            if noise_frames < 1:
                raise ValueError("Количество кадров должно быть >= 1")
        except Exception as e:
            messagebox.showerror("Неверный параметр", f"Количество кадров неверно: {e}")
            return

        try:
            reduction_strength = float(self.var_reduction_strength.get())
            if reduction_strength < 0:
                raise ValueError("Сила подавления должна быть >= 0")
        except Exception as e:
            messagebox.showerror("Неверный параметр", f"Сила подавления неверна: {e}")
            return

        try:
            spectral_floor = float(self.var_spectral_floor.get())
            if spectral_floor < 0 or spectral_floor > 1:
                raise ValueError("Минимальный уровень спектра должен быть между 0 и 1")
        except Exception as e:
            messagebox.showerror("Неверный параметр", f"Минимальный уровень спектра неверен: {e}")
            return

        window_type = self.var_window_type.get()
        use_numpy_fft = self.var_use_numpy_fft.get()
        
        params = dict(
            window_size=window_size,
            hop_length=hop_length,
            noise_sample_frames=noise_frames,
            noise_reduction_strength=reduction_strength,
            spectral_floor_level=spectral_floor,
            window_type=window_type,
            use_numpy_fft=use_numpy_fft
        )

        t = threading.Thread(target=self._processing_worker, args=(self.orig_data, self.orig_sr, params), daemon=True)
        t.start()
        fft_type = "NumPy FFT" if use_numpy_fft else "кастомный FFT"
        self.status_var.set(f"Запущено улучшение качества ({fft_type})...")
        self.btn_process.config(state="disabled")
        self.btn_play_orig.config(state="disabled")
        self.btn_spectrogram_orig.config(state="disabled")
        self.btn_play_result.config(state="disabled")
        self.btn_spectrogram_result.config(state="disabled")
        self.btn_show_overlay.config(state="disabled")
        self.btn_save.config(state="disabled")

    def _processing_worker(self, audio, sr, params):
        try:
            fft_type = "NumPy FFT" if params['use_numpy_fft'] else "кастомный FFT"
            self.q.put(("info", f"Обработка ({fft_type}): окно={params['window_size']}, шаг={params['hop_length']}, функция={params['window_type']}, кадров шума={params['noise_sample_frames']}, сила={params['noise_reduction_strength']}"))
            
            den = self.enhancer.enhance_audio_new(
                audio_data=audio,
                sample_rate=sr,
                noise_sample_frames=params['noise_sample_frames'],
                noise_reduction_strength=params['noise_reduction_strength'],
                spectral_floor_level=params['spectral_floor_level'],
                window_size=params['window_size'],
                hop_length=params['hop_length'],
                window_type=params['window_type'],
                use_numpy_fft=params['use_numpy_fft'],
                random_frames_seed=42
            )
            
            self.result_data = den
            self.result_sr = sr
            self.q.put(("done", f"Готово ({fft_type})"))
        except Exception as e:
            self.q.put(("error", f"Ошибка обработки: {e}"))

    def save_result(self):
        if self.result_data is None:
            return
        path = filedialog.asksaveasfilename(
            title="Сохранить результат как", 
            defaultextension=".wav", 
            filetypes=[
                ("WAV file", "*.wav"),
                ("FLAC", "*.flac"), 
                ("All files", "*.*")
            ]
        )
        if not path:
            return
        try:
            audio_int16 = (self.result_data * 32767).astype(np.int16)
            wav.write(path, self.result_sr, audio_int16)
            messagebox.showinfo("Сохранено", f"Результат сохранён: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def _process_queue(self):
        try:
            while True:
                typ, msg = self.q.get_nowait()
                if typ == "info":
                    self.status_var.set(msg)
                elif typ == "error":
                    self.status_var.set("Ошибка")
                    messagebox.showerror("Ошибка", msg)
                    self._update_buttons_state()
                elif typ == "done":
                    self.status_var.set(msg)
                    self._update_buttons_state()
                elif typ == "file_loaded":
                    self.lbl_file.config(text=f"recorded_audio.wav — {len(self.orig_data)} samples, {self.orig_sr} Hz")
                    self._update_buttons_state()
                else:
                    self.status_var.set(msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(200, self._process_queue)
    
    def _update_buttons_state(self):
        has_original = self.orig_data is not None
        has_result = self.result_data is not None
        
        self.btn_play_orig.config(state="normal" if has_original else "disabled")
        self.btn_spectrogram_orig.config(state="normal" if has_original else "disabled")
        self.btn_process.config(state="normal" if has_original else "disabled")
        self.btn_play_result.config(state="normal" if has_result else "disabled")
        self.btn_spectrogram_result.config(state="normal" if has_result else "disabled")
        self.btn_show_overlay.config(state="normal" if has_result else "disabled")
        self.btn_save.config(state="normal" if has_result else "disabled")


def main():
    root = tk.Tk()
    root.geometry("1500x400")
    app = DenoiserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()