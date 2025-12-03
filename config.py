from pathlib import Path
import pygame


import pygame

pygame.init()

# ----- FUENTES -----
FONT_BIG = pygame.font.Font(None, 60)      # Títulos
FONT_MEDIUM = pygame.font.Font(None, 40)   # Botones
FONT_SMALL = pygame.font.Font(None, 30)    # Textos extra

# ===========================
# RUTAS Y ASSETS
# ===========================

ASSET_DIR = Path(__file__).parent / "assets"

print("ASSET_DIR =", ASSET_DIR)
print("ARCHIVOS EN ASSET_DIR:", list(ASSET_DIR.iterdir()))
print("HORIZ EXISTE:", (ASSET_DIR / "barco_horizontal.png.png").exists())
print("VERT EXISTE:", (ASSET_DIR / "barco_vertical.png.png").exists())
print("EXPLO EXISTE:", (ASSET_DIR / "explosion.jpg").exists())

# Rutas de imágenes
BARCO_HORIZ_PATH = ASSET_DIR / "barco_horizontal.png.png"
BARCO_VERT_PATH = ASSET_DIR / "barco_vertical.png.png"
EXPLOSION_IMG_PATH = ASSET_DIR / "explosion.jpg"

# ===========================
# PYGAME INIT (ANTES DE CARGAR IMG)
# ===========================

pygame.init()
pygame.display.set_mode((1, 1))  # Ventana mínima para permitir convert_alpha()

# ===========================
# CARGA SEGURA DE IMÁGENES
# ===========================

def cargar_imagen(ruta):
    try:
        img = pygame.image.load(ruta).convert_alpha()
        print(f"[OK] Imagen cargada: {ruta.name}")
        return img
    except Exception as e:
        print(f"[ERROR] No se pudo cargar {ruta.name}: {e}")
        return None

IMG_BARCO_H = cargar_imagen(BARCO_HORIZ_PATH)
IMG_BARCO_V = cargar_imagen(BARCO_VERT_PATH)
EXPLOSION_IMG = cargar_imagen(EXPLOSION_IMG_PATH)

print("IMG_BARCO_H =", IMG_BARCO_H)
print("IMG_BARCO_V =", IMG_BARCO_V)
print("EXPLOSION_IMG =", EXPLOSION_IMG)

# ===========================
# PANTALLA Y FUENTES
# ===========================

WIDTH = 1000
HEIGHT = 700
FPS = 60

FONT_BIG = pygame.font.SysFont("arial", 28)
FONT_VICTORY = pygame.font.SysFont("arial", 48, bold=True)
SMALL = pygame.font.SysFont("arial", 18)

# ===========================
# COLORES
# ===========================

TEXTO = (230, 230, 230)
BUTTON_COLOR = (45, 85, 155)
BUTTON_HOVER = (75, 120, 200)
INPUT_BG = (20, 35, 60)
INPUT_BORDER = (100, 120, 160)
INPUT_ACTIVE_BORDER = (200, 200, 255)
PANEL = (15, 25, 40)
SEPARATOR = (90, 90, 120)
GRID_COLOR = (90, 120, 160)
AXIS_COLOR = (200, 200, 255)

# ===========================
# GRID
# ===========================

GRID_LEFT = 40
GRID_TOP = 40
GRID_SIZE = 500

# ===========================
# JUEGO Y DIFICULTADES
# ===========================

SHIP_SIZE = 3

DIFFICULTY_CONFIG = {
    "easy":   {"range": 10, "ships": 2, "lives": 10},
    "medium": {"range": 12, "ships": 3, "lives": 8},
    "hard":   {"range": 15, "ships": 4, "lives": 6},
}

# ===========================
# LÓGICA DEL JUEGO
# ===========================

NEAR_THRESHOLD = 3.0
HIT_TOLERANCE = 0.1
HINTS_ORDER = ["x", "y"]
