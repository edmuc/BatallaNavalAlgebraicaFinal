# login.py
import customtkinter as ctk
from firebase_config import auth
from tkinter import messagebox
from PIL import Image
import os

# IMPORTANTE: para guardar uid para el multijugador
from state import state

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Firebase")
        self.geometry("500x400")
        self.resizable(False, False)

        ruta_fondo = os.path.join(BASE_DIR, "assets", "fondo.png")

        try:
            bg_image = Image.open(ruta_fondo)
            self.bg = ctk.CTkImage(light_image=bg_image, size=(500, 400))
            bg_label = ctk.CTkLabel(self, image=self.bg, text="")
            bg_label.place(x=0, y=0)
        except Exception:
            print(f"⚠ No se encontró {ruta_fondo}")

        frame = ctk.CTkFrame(self, width=300, height=260, corner_radius=10)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Iniciar Sesión", font=("Arial", 22)).pack(pady=12)

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", width=260)
        self.email_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=260)
        self.password_entry.pack(pady=8)

        ctk.CTkButton(frame, text="Entrar", command=self.login_user, width=200).pack(pady=12)
        ctk.CTkButton(frame, text="Registrarse", command=self.open_register, fg_color="gray").pack(pady=5)

    def login_user(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        try:
            user = auth.sign_in_with_email_and_password(email, password)

            # 💾 Guardamos el UID y email en state para el multijugador
            state["user_uid"] = user["localId"]
            state["user_email"] = email

            messagebox.showinfo("Éxito", f"¡Bienvenido {email}!")

            self.after(200, self.open_menu, {"email": email, "uid": user["localId"]})

        except Exception as e:
            print(e)
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")

    def open_menu(self, user_data):
        self.destroy()
        from menu import MenuWindow
        # Mandamos el diccionario completo
        MenuWindow(user_data).mainloop()

    def open_register(self):
        RegisterWindow(self)


# ------------------------------ #
#       VENTANA DE REGISTRO
# ------------------------------ #

class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Registro")
        self.geometry("420x350")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Crear Cuenta", font=("Arial", 22)).pack(pady=15)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Correo electrónico", width=260)
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=260)
        self.password_entry.pack(pady=10)

        self.password_repeat_entry = ctk.CTkEntry(self, placeholder_text="Repite la contraseña", show="*", width=260)
        self.password_repeat_entry.pack(pady=10)

        ctk.CTkButton(self, text="Registrarse", command=self.register_user, width=200).pack(pady=18)

    def register_user(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        password2 = self.password_repeat_entry.get().strip()

        if password != password2:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres.")
            return

        try:
            auth.create_user_with_email_and_password(email, password)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            self.destroy()
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "No se pudo registrar. Verifica el correo o intenta más tarde.")


if __name__ == "__main__":
    LoginApp().mainloop()
