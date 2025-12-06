from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import numpy as np

class SignalOverlayViewer:
    def __init__(self, parent, title="Наложение сигналов"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Сохранить как PNG...", 
                  command=self.save_as_png).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Переключить вид", 
                  command=self.toggle_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Показать разницу", 
                  command=self.show_difference).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть", 
                  command=self.close).pack(side=tk.RIGHT, padx=5)
        
        self.is_closed = False
        self.view_mode = 'overlay'
        self.original_data = None
        self.processed_data = None
        self.sample_rate = None
        
    def show_signals(self, original_data, processed_data, sample_rate, title="Наложение сигналов"):
        if self.is_closed:
            return
            
        self.original_data = original_data
        self.processed_data = processed_data
        self.sample_rate = sample_rate
        
        self._show_overlay_view(title)
        
    def _show_overlay_view(self, title):
        self.ax.clear()
        
        time = np.arange(len(self.original_data)) / self.sample_rate
        
        if len(self.original_data) > 100000:
            step = len(self.original_data) // 100000 + 1
            time = time[::step]
            orig_plot = self.original_data[::step]
            proc_plot = self.processed_data[::step]
        else:
            orig_plot = self.original_data
            proc_plot = self.processed_data
        
        self.ax.plot(time, orig_plot, 'b-', alpha=0.7, linewidth=1.5, label='Оригинальный сигнал')
        self.ax.plot(time, proc_plot, 'r-', alpha=0.7, linewidth=1.5, label='Обработанный сигнал')
        
        self.ax.set_xlabel('Время (с)')
        self.ax.set_ylabel('Амплитуда')
        self.ax.set_title(f"{title}\nСиний - оригинал, Красный - обработанный")
        self.ax.legend(loc='upper right')
        self.ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def _show_separate_view(self, title):
        self.ax.clear()
        
        time = np.arange(len(self.original_data)) / self.sample_rate
        
        if len(self.original_data) > 100000:
            step = len(self.original_data) // 100000 + 1
            time = time[::step]
            orig_plot = self.original_data[::step]
            proc_plot = self.processed_data[::step]
        else:
            orig_plot = self.original_data
            proc_plot = self.processed_data
        
        self.fig.clear()
        
        ax1 = self.fig.add_subplot(211)
        ax1.plot(time, orig_plot, 'b-', alpha=0.8, linewidth=1.5)
        ax1.set_ylabel('Амплитуда')
        ax1.set_title('Оригинальный сигнал')
        ax1.grid(True, alpha=0.3)
        
        ax2 = self.fig.add_subplot(212, sharex=ax1)
        ax2.plot(time, proc_plot, 'r-', alpha=0.8, linewidth=1.5)
        ax2.set_xlabel('Время (с)')
        ax2.set_ylabel('Амплитуда')
        ax2.set_title('Обработанный сигнал')
        ax2.grid(True, alpha=0.3)
        
        self.fig.suptitle(title, fontsize=12)
        self.fig.tight_layout()
        self.canvas.draw()
        
    def _show_difference_view(self, title):
        self.ax.clear()
        
        difference = self.processed_data - self.original_data
        
        time = np.arange(len(difference)) / self.sample_rate
        
        if len(difference) > 100000:
            step = len(difference) // 100000 + 1
            time = time[::step]
            diff_plot = difference[::step]
        else:
            diff_plot = difference
        
        self.ax.plot(time, diff_plot, 'g-', alpha=0.8, linewidth=1.5)
        
        self.ax.set_xlabel('Время (с)')
        self.ax.set_ylabel('Амплитуда')
        self.ax.set_title(f"{title}\nРазница: обработанный - оригинальный (подавленный шум)")
        self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.ax.grid(True, alpha=0.3)
        
        rms_diff = np.sqrt(np.mean(difference**2))
        max_diff = np.max(np.abs(difference))
        self.ax.text(0.02, 0.98, f'RMS разницы: {rms_diff:.6f}\nМакс. разница: {max_diff:.6f}', 
                    transform=self.ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def toggle_view(self):
        if self.is_closed or self.original_data is None:
            return
            
        if self.view_mode == 'overlay':
            self.view_mode = 'separate'
            self._show_separate_view("Сравнение сигналов")
        elif self.view_mode == 'separate':
            self.view_mode = 'difference'
            self.show_difference()
        else:
            self.view_mode = 'overlay'
            self._show_overlay_view("Наложение сигналов")
            
    def show_difference(self):
        if self.is_closed or self.original_data is None:
            return
            
        self.view_mode = 'difference'
        self._show_difference_view("Разница между сигналами")
        
    def save_as_png(self):
        if self.is_closed:
            return
            
        filename = filedialog.asksaveasfilename(
            title="Сохранить график",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Сохранено", f"График сохранен: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def close(self):
        self.is_closed = True
        plt.close(self.fig)
        self.window.destroy()