# splash.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.geometry("700x500+400+150")

        # Ruta de la imagen
        ruta_fondo = os.path.join(BASE_DIR, "assets", "fondo.png")

        try:
            img = Image.open(ruta_fondo)
        except Exception:
            img = Image.new("RGB", (700, 500), color="black")

        img = img.resize((700, 500))
        self.bg = ImageTk.PhotoImage(img)
        fondo = tk.Label(self, image=self.bg)
        fondo.place(x=0, y=0, relwidth=1, relheight=1)

        titulo = tk.Label(
            self,
            text="⚓ Batalla Naval Algebraica ⚓",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#000000"
        )
        titulo.pack(pady=40)

        self.progress = ttk.Progressbar(
            self, orient="horizontal", mode="determinate", length=400
        )
        self.progress.pack(pady=20)
        self.after(100, lambda: self.load_progress(0))

    def load_progress(self, value):
        if value >= 100:
            self.destroy()
            return
        self.progress["value"] = value
        self.after(40, lambda: self.load_progress(value + 6))


if __name__ == "__main__":
    SplashScreen().mainloop()
