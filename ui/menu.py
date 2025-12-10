# ui/menu.py
# Menú futurista estilo HUD (Pygame)
# Incluye botón adicional "Multijugador Online"

import os
import pygame
from ui.textwrap import render_wrapped_text

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

CYAN = (0, 200, 255)
CYAN_HOVER = (0, 255, 255)
YELLOW = (255, 210, 0)
DARK_BG = (6, 18, 32)


def safe_load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None


def make_menu_bg(WIDTH, HEIGHT):
    bg_path = os.path.join(ASSETS_DIR, "grid_bg.png")
    img = safe_load_image(bg_path, (WIDTH, HEIGHT))
    if img:
        return img

    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((8, 18, 30))
    grid_color = (12, 32, 48)

    spacing = 48
    for x in range(0, WIDTH, spacing):
        pygame.draw.line(surf, grid_color, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, spacing):
        pygame.draw.line(surf, grid_color, (0, y), (WIDTH, y))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 80))
    surf.blit(overlay, (0, 0))
    return surf


class NeonButton:
    def __init__(self, x, y, w, h, text, icon=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.icon = icon
        self.hover = False
        self._glow_alpha = 0

    def update(self, pos):
        self.hover = self.rect.collidepoint(pos)
        if self.hover:
            self._glow_alpha = min(200, self._glow_alpha + 25)
        else:
            self._glow_alpha = max(0, self._glow_alpha - 25)

    def draw(self, screen, font):
        if self._glow_alpha > 0:
            glow = pygame.Surface((self.rect.w + 20, self.rect.h + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*CYAN, self._glow_alpha), glow.get_rect(), border_radius=12)
            screen.blit(glow, (self.rect.x - 10, self.rect.y - 10))

        base_color = (6, 18, 30) if not self.hover else (10, 26, 40)
        pygame.draw.rect(screen, base_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, CYAN, self.rect, 3, border_radius=12)

        txt = font.render(self.text, True, (220, 240, 255))
        screen.blit(txt, (
            self.rect.centerx - txt.get_width() // 2,
            self.rect.centery - txt.get_height() // 2
        ))


def draw_menu(screen, WIDTH, HEIGHT):
    title_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.06), bold=True)
    btn_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.03), bold=True)

    bg = make_menu_bg(WIDTH, HEIGHT)
    screen.blit(bg, (0, 0))

    title = "BATALLA NAVAL\nALGEBRAICA"
    lines = title.split("\n")

    y = int(HEIGHT * 0.1)
    for line in lines:
        t = title_font.render(line, True, YELLOW)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y))
        y += title_font.get_height() + 4

    # load icons
    icon_start = safe_load_image(os.path.join(ASSETS_DIR, "icon_start.png"))
    icon_how = safe_load_image(os.path.join(ASSETS_DIR, "icon_how.png"))
    icon_exit = safe_load_image(os.path.join(ASSETS_DIR, "icon_exit.png"))

    bw = int(WIDTH * 0.3)
    bh = int(HEIGHT * 0.075)
    cx = WIDTH // 2 - bw // 2
    y_base = int(HEIGHT * 0.38)

    # Botones originales
    btn_start = NeonButton(cx, y_base, bw, bh, "Iniciar", icon_start)
    btn_multiplayer = NeonButton(cx, y_base + bh + 25, bw, bh, "Multijugador Online")
    btn_how = NeonButton(cx, y_base + 2 * (bh + 25), bw, bh, "Cómo jugar", icon_how)
    btn_exit = NeonButton(cx, y_base + 3 * (bh + 25), bw, bh, "Salir", icon_exit)

    mouse = pygame.mouse.get_pos()
    for b in (btn_start, btn_multiplayer, btn_how, btn_exit):
        b.update(mouse)
        b.draw(screen, btn_font)

    return {
        "btn_start": btn_start.rect,
        "btn_multi": btn_multiplayer.rect,   # ← NUEVO
        "btn_how": btn_how.rect,
        "btn_quit": btn_exit.rect,
    }


def draw_howto(screen, WIDTH, HEIGHT):
    bg = make_menu_bg(WIDTH, HEIGHT)
    screen.blit(bg, (0, 0))

    title_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.05), bold=True)
    body_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.025))

    title = title_font.render("Cómo jugar", True, YELLOW)
    screen.blit(title, (60, 40))

    lines = [
        "Objetivo: hundir todos los barcos introduciendo funciones f(x).",
        "Pulsa Enter o haz clic en Disparar para lanzar un tiro.",
        "Las pistas contienen relaciones algebraicas que ayudan a localizar barcos.",
        "Pierdes vidas al fallar. El juego termina cuando se agotan.",
        "La opción 'Mostrar barcos' es para pruebas y depuración."
    ]

    y = 120
    for l in lines:
        render_wrapped_text(screen, l, 60, y, body_font, (220, 240, 255), WIDTH - 120)
        y += 40

    bw = int(WIDTH * 0.2)
    bh = int(HEIGHT * 0.07)

    btn_back = NeonButton(60, HEIGHT - 100, bw, bh, "Volver")
    btn_back.update(pygame.mouse.get_pos())
    btn_back.draw(screen, body_font)

    return {"btn_back": btn_back.rect}

def draw_multiplayer_menu(screen, WIDTH, HEIGHT):
    bg = make_menu_bg(WIDTH, HEIGHT)
    screen.blit(bg, (0, 0))

    title_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.05), bold=True)
    btn_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.03), bold=True)

    title = title_font.render("Multijugador Online", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

    # Botones
    bw = int(WIDTH * 0.3)
    bh = int(HEIGHT * 0.075)
    cx = WIDTH // 2 - bw // 2
    y_base = int(HEIGHT * 0.35)

    btn_create = NeonButton(cx, y_base, bw, bh, "Crear Sala")
    btn_join = NeonButton(cx, y_base + bh + 25, bw, bh, "Unirse a Sala")
    btn_back = NeonButton(cx, y_base + 2 * (bh + 25), bw, bh, "Volver")

    mouse = pygame.mouse.get_pos()
    for b in (btn_create, btn_join, btn_back):
        b.update(mouse)
        b.draw(screen, btn_font)

    return {
        "btn_create": btn_create.rect,
        "btn_join": btn_join.rect,
        "btn_back": btn_back.rect
    }

def draw_room_input(screen, WIDTH, HEIGHT, current_text):
    bg = make_menu_bg(WIDTH, HEIGHT)
    screen.blit(bg, (0, 0))

    title_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.05), bold=True)
    input_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.04), bold=True)
    btn_font = pygame.font.SysFont("consolas", int(HEIGHT * 0.03), bold=True)

    title = title_font.render("Ingresa número de sala (1 o 2)", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    # Caja de texto
    box_w = int(WIDTH * 0.3)
    box_h = int(HEIGHT * 0.08)
    box_rect = pygame.Rect(WIDTH // 2 - box_w // 2, 200, box_w, box_h)

    pygame.draw.rect(screen, (10, 26, 40), box_rect, border_radius=8)
    pygame.draw.rect(screen, CYAN, box_rect, 3, border_radius=8)

    # Mostrar texto escrito
    txt = input_font.render(current_text, True, (220, 240, 255))
    screen.blit(txt, (box_rect.centerx - txt.get_width() // 2,
                      box_rect.centery - txt.get_height() // 2))

    # Botones
    bw = int(WIDTH * 0.25)
    bh = int(HEIGHT * 0.07)
    cx = WIDTH // 2 - bw // 2
    y = 320

    btn_ok = NeonButton(cx, y, bw, bh, "Aceptar")
    btn_back = NeonButton(cx, y + bh + 25, bw, bh, "Volver")

    mouse = pygame.mouse.get_pos()
    for b in (btn_ok, btn_back):
        b.update(mouse)
        b.draw(screen, btn_font)

    return {
        "input_rect": box_rect,
        "btn_ok": btn_ok.rect,
        "btn_back": btn_back.rect
    }
