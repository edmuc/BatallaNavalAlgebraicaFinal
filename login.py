# login.py
import customtkinter as ctk
from firebase_config import auth
from tkinter import messagebox
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Firebase")
        self.geometry("500x400")
        self.resizable(False, False)

        # Ruta absoluta del fondo
        ruta_fondo = os.path.join(BASE_DIR, "assets", "fondo.png")

        # fondo (opcional)
        try:
            bg_image = Image.open(ruta_fondo)
            self.bg = ctk.CTkImage(light_image=bg_image, size=(500, 400))
            bg_label = ctk.CTkLabel(self, image=self.bg, text="")
            bg_label.place(x=0, y=0)
        except Exception:
            print(f"⚠ No se encontró {ruta_fondo} (sin fondo).")

        frame = ctk.CTkFrame(self, width=300, height=250, corner_radius=10)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Iniciar Sesión", font=("Arial", 22)).pack(pady=12)
        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", width=260)
        self.email_entry.pack(pady=8)
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=260)
        self.password_entry.pack(pady=8)

        ctk.CTkButton(frame, text="Entrar", command=self.login_user, width=200).pack(pady=12)

    def login_user(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            auth.sign_in_with_email_and_password(email, password)
            messagebox.showinfo("Éxito", f"¡Bienvenido {email}!")
            self.after(200, self.open_menu, email)
        except Exception:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")

    def open_menu(self, email):
        self.destroy()
        from menu import MenuWindow
        MenuWindow(email).mainloop()


if __name__ == "__main__":
    LoginApp().mainloop()
