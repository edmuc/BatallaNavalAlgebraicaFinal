# drawing.py
import pygame

IMAGES = {}   # aquí se guardan las imágenes mandadas desde main.py

def set_images(images_dict):
    global IMAGES
    IMAGES = images_dict


def draw_button(screen, rect, text, hover=False):
    color = (50,150,230) if hover else (30,120,200)
    pygame.draw.rect(screen, color, rect, border_radius=8)

    font = pygame.font.SysFont("Arial", 18)
    txt = font.render(text, True, (245,245,245))
    screen.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2,
                      rect.y + (rect.height - txt.get_height()) // 2))


# --------------------------
#       NUEVO TOGGLE
# --------------------------
def draw_toggle(screen, rect, text, active):
    bg = (40, 70, 110) if not active else (70, 130, 210)
    outline = (120,140,180)
    txt_color = (230, 230, 230)

    pygame.draw.rect(screen, bg, rect, border_radius=6)
    pygame.draw.rect(screen, outline, rect, width=2, border_radius=6)

    # Texto
    font = pygame.font.SysFont("Arial", 18)
    txt = font.render(text, True, txt_color)
    screen.blit(txt, (rect.x + 35, rect.y + rect.height//2 - txt.get_height()//2))

    # Indicador ON/OFF (circulito)
    color = (255,255,255) if active else (170,170,170)
    pygame.draw.circle(screen, color, (rect.x + 15, rect.y + rect.height//2), 6)


def draw_ui(screen, state):
    """
    state: {
        "show_ships": True/False
    }
    """

    screen.fill((10,41,85))

    # Mostrar un barco si existe
    if "BARCO_H" in IMAGES and state["show_ships"]:
        screen.blit(IMAGES["BARCO_H"], (50, 50))

    # dibujar el toggle
    toggle_rect = pygame.Rect(580, 350, 260, 32)
    draw_toggle(screen, toggle_rect, "Mostrar barcos (pruebas)", state["show_ships"])

    # botones dummy
    return {
        "toggle_rect": toggle_rect,
        "btn_fire": pygame.Rect(800, 600, 1, 1)  # evita errores
    }
