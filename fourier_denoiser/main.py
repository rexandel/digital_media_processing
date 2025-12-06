import tkinter as tk
from modules import DenoiserUI

def main():
    root = tk.Tk()
    root.geometry("1500x400")
    app = DenoiserUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()