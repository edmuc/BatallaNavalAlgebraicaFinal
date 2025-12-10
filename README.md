1. Requisitos del Sistema

Para ejecutar el juego se requiere:

Python 3.10 o superior

Sistema operativo compatible con Python:

Windows 10 / 11

Linux

macOS

2. Librerías de Python Necesarias

Antes de iniciar el programa, deben estar instaladas las siguientes librerías externas:

2.1. Pygame

Utilizada para toda la interfaz gráfica del juego (pantallas, botones, tableros, animaciones).

Instalación:

pip install pygame

2.2. SymPy

Se utiliza para interpretar funciones matemáticas ingresadas por el usuario y evaluarlas.

Instalación:

pip install sympy

2.3. NumPy

Sirve para operaciones matemáticas internas, manejo de vectores y cálculos rápidos.

Instalación:

pip install numpy

2.4. Firebase Admin SDK (opcional, solo para modo multijugador)

Utilizado para sincronizar datos entre las dos instancias del juego cuando se juega en modo "Sala 1 / Sala 2".

Instalación:

pip install firebase-admin


Además, se requiere:

Archivo serviceAccountKey.json dentro de la carpeta de tu proyecto

Acceso al proyecto de Firebase configurado

3. Archivos Internos Requeridos

Para que el juego se ejecute correctamente, deben estar presentes los siguientes módulos:

main.py

logic.py

state.py

multiplayer.py

Carpeta ui/ con:

grid.py

panel.py

buttons.py

(otros archivos de interfaz)

Carpeta assets/ con las imágenes:

Barcos horizontales

Barcos verticales

Íconos e imágenes decorativas

4. Inicialización del Juego

Una vez instaladas las librerías, ejecutar:

python main.py


El juego se iniciará en modo local por defecto.
Para multijugador, se debe elegir Sala 1 o Sala 2 desde el menú.</br>Ambos jugadores deben ejecutar el programa simultáneamente.

5. Errores Comunes

"No module named pygame"
→ Falta instalar Pygame.

"No module named sympy"
→ Falta instalar SymPy.

"firebase_admin is not defined"
→ No está instalado el SDK de Firebase o falta el archivo JSON de credenciales.

La ventana se congela
→ Se ejecutó una función inválida o se produjo un ciclo infinito; cerrar y reabrir.
