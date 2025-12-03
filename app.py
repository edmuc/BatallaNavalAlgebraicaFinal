# app.py
import os
import sys
from splash import SplashScreen
from login import LoginApp

def main():
    # Mostrar Splash (es su propia Tkinter root)
    SplashScreen().mainloop()
    # Al cerrar Splash, se espera que éste lance el login por subprocess
    # Alternativa: abrir el login aquí (si prefieres no usar subprocess en splash)
    # Lanzamos directamente el login para flujo simple:
    LoginApp().mainloop()

if __name__ == "__main__":
    main()
