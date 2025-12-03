# menu.py
import customtkinter as ctk
from PIL import Image
import subprocess
import sys
import os

class MenuWindow(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.title("Batalla Naval Algebraica")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")

        # fondo
        try:
            bg_path = os.path.join("assets", "otrofondo.png")
            bg_image = Image.open(bg_path).resize((900, 600))
            self.bg_image = ctk.CTkImage(bg_image, size=(900, 600))
            bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            bg_label.place(x=0, y=0)
        except Exception:
            print("⚠ No se encontró assets/otrofondo.png (sin fondo).")

        # marco central (centrado)
        self.frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1a1a1a", width=520, height=360)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.frame, text="Bienvenido:", font=("Arial", 18)).pack(pady=(22, 2))
        ctk.CTkLabel(self.frame, text=email, font=("Arial", 18, "bold"), text_color="#00aaff").pack()
        ctk.CTkLabel(self.frame, text="Menú Principal", font=("Arial", 28, "bold")).pack(pady=(10, 16))

        # botones (centrados)
        ctk.CTkButton(self.frame, text="Entrar al juego", font=("Arial", 20, "bold"),
                      fg_color="#007bff", hover_color="#0066cc",
                      corner_radius=15, height=50, width=380,
                      command=self.abrir_juego).pack(pady=10)

        ctk.CTkButton(self.frame, text="Cerrar programa", font=("Arial", 20, "bold"),
                      fg_color="#ff4d4d", hover_color="#e60000",
                      corner_radius=15, height=50, width=380,
                      command=self.quit).pack(pady=(6, 16))

        # botones secundarios
        ctk.CTkButton(self.frame, text="Mostrar Mis Puntajes (próx)", width=200,
                      corner_radius=12).pack(pady=6)

    def abrir_juego(self):
        # Lanzar game.py en un nuevo proceso para evitar conflictos con Tkinter
        ruta = os.path.join(os.path.dirname(__file__), "main.py")
        subprocess.Popen([sys.executable, ruta])
        # opcional: cerrar menú si quieres que el juego quede solo
        # self.destroy()

if __name__ == "__main__":
    MenuWindow("demo@correo.com").mainloop()
