from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk, filedialog, messagebox
import tkinter as tk

class SpectrogramViewer:
    
    def __init__(self, parent, title="Спектрограмма"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Сохранить как PNG...", 
                  command=self.save_as_png).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", 
                  command=self.close).pack(side=tk.RIGHT, padx=5)
        
        self.is_closed = False
        
    def show_spectrogram(self, audio_data, sample_rate, title="Спектрограмма", cmap='viridis'):
        if self.is_closed:
            return
            
        self.ax.clear()
        
        NFFT = 1024
        Fs = sample_rate
        noverlap = NFFT // 2
        
        self.ax.specgram(audio_data, NFFT=NFFT, Fs=Fs, 
                         noverlap=noverlap, cmap=cmap)
        
        self.ax.set_xlabel('Время (с)')
        self.ax.set_ylabel('Частота (Гц)')
        self.ax.set_title(title)
        
        self.fig.colorbar(self.ax.images[0], ax=self.ax, label='Мощность (дБ)')
        
        self.canvas.draw()
        
    def save_as_png(self):
        if self.is_closed:
            return
            
        filename = filedialog.asksaveasfilename(
            title="Сохранить спектрограмму",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Сохранено", f"Спектрограмма сохранена: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def close(self):
        self.is_closed = True
        plt.close(self.fig)
        self.window.destroy()