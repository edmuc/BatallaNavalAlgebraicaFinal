# ui/panel.py — PANEL FUTURISTA COMPLETO, FINAL

import pygame
from state import state
import time

# ============================
# ESTILO FUTURISTA
# ============================

PANEL_BG = (10, 14, 28)
PANEL_BORDER = (40, 140, 255)
ACCENT = (64, 224, 255)
ACCENT_LIGHT = (150, 255, 255)
TEXT = (230, 240, 255)
DANGER = (255, 90, 90)
OK = (80, 230, 150)
BUTTON_BG = (25, 40, 70)
BUTTON_HOVER = (40, 80, 120)
INPUT_ACTIVE = (120, 200, 255)

pygame.font.init()
FONT_TITLE = pygame.font.SysFont("consolas", 26, bold=True)
FONT_SUB = pygame.font.SysFont("consolas", 20, bold=True)
FONT_LABEL = pygame.font.SysFont("consolas", 18)
FONT_SMALL = pygame.font.SysFont("consolas", 14)


# ============================
# BOTÓN FUTURISTA
# ============================

def draw_button(surface, rect, text, hover=False):
    color = BUTTON_HOVER if hover else BUTTON_BG
    pygame.draw.rect(surface, color, rect, border_radius=10)

    if hover:
        glow = rect.inflate(8, 8)
        pygame.draw.rect(surface, ACCENT, glow, width=3, border_radius=14)

    txt = FONT_LABEL.render(text, True, TEXT)
    surface.blit(
        txt,
        (rect.centerx - txt.get_width() // 2,
         rect.centery - txt.get_height() // 2)
    )
    return rect


# ============================
# TOGGLE (Mostrar barcos)
# ============================

def draw_toggle(surface, rect, label, active):
    bg = (18, 28, 40)
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, (60, 100, 150), rect, width=2, border_radius=8)

    circle_x = rect.x + 14
    circle_y = rect.centery
    circle_color = ACCENT if active else (120, 130, 150)
    pygame.draw.circle(surface, circle_color, (circle_x, circle_y), 8)

    lbl = FONT_SMALL.render(label, True, TEXT)
    surface.blit(lbl, (rect.x + 32,
                       rect.y + rect.height // 2 - lbl.get_height() // 2))


# ============================
# INPUT BOX
# ============================

def draw_input_box(surface, rect, label, value, active, cursor_show):
    border_color = INPUT_ACTIVE if active else (90, 120, 150)
    pygame.draw.rect(surface, border_color, rect.inflate(4, 4), border_radius=8)
    pygame.draw.rect(surface, (80, 80, 180), rect, border_radius=8)

    txt = f"{label}: {value}"
    if active and cursor_show:
        txt += "|"

    render = FONT_LABEL.render(txt, True, TEXT)
    surface.blit(render, (rect.x + 10, rect.y + 7))


# ============================
# BARRA DE VIDA
# ============================

def draw_energy_bar(surface, x, y, w, h, value, max_value):
    pygame.draw.rect(surface, (20, 25, 40), (x, y, w, h), border_radius=6)

    pct = max(0, min(1, (value / max_value) if max_value > 0 else 0))
    fill_w = int(w * pct)

    if pct > 0.6:
        color = OK
    elif pct > 0.3:
        color = (255, 200, 80)
    else:
        color = DANGER

    pygame.draw.rect(surface, color, (x, y, fill_w, h), border_radius=6)

    txt = FONT_SMALL.render(f"{int(pct * 100)}%", True, TEXT)
    surface.blit(txt, (x + w - txt.get_width() - 6, y + 2))


# ============================
# PANEL PRINCIPAL
# ============================

def draw_panel(screen, grid_rect, w, h):
    """
    Devuelve hitboxes:
    {
      "panel": Rect,
      "diff_boxes": [(dif_str, Rect), ...],
      "input_func": Rect,
      "fire_btn": Rect,
      "btn_show_ships": Rect
    }
    """

    panel = pygame.Rect(grid_rect.right + 20, grid_rect.top, w, h)

    pygame.draw.rect(screen, PANEL_BG, panel, border_radius=14)
    pygame.draw.rect(screen, PANEL_BORDER, panel, width=3, border_radius=14)

    title = FONT_TITLE.render("PANEL DE CONTROL", True, ACCENT)
    screen.blit(title, (panel.x + 20, panel.y + 10))

    y = panel.y + 60
    x = panel.x + 20

    # ============================
    # DIFICULTAD
    # ============================

    dif_label = FONT_SUB.render("Dificultad:", True, TEXT)
    screen.blit(dif_label, (x, y))

    y += 35
    bw = (w - 60) // 3
    diff_boxes = []

    difficulties = ["easy", "medium", "hard"]
    labels = ["Fácil", "Media", "Difícil"]

    for i, dif in enumerate(difficulties):
        r = pygame.Rect(x + i * (bw + 10), y, bw, 32)
        active = (state["difficulty"] == dif)

        pygame.draw.rect(screen, ACCENT if active else BUTTON_BG,
                         r, border_radius=8)

        text = FONT_SMALL.render(labels[i], True,
                                 (20, 20, 20) if active else TEXT)
        screen.blit(text, (r.centerx - text.get_width() // 2,
                           r.centery - text.get_height() // 2))

        diff_boxes.append((dif, r))

    y += 60

    # ============================
    # VIDA
    # ============================

    hp_label = FONT_SUB.render("Energía:", True, ACCENT)
    screen.blit(hp_label, (x, y))

    y += 26
    draw_energy_bar(
        screen, x, y, w - 40, 20,
        state.get("lives", 0), state.get("max_lives", 1)
    )

    y += 50

    # ============================
    # INPUT FUNCIÓN f(x)
    # ============================

    func_label = FONT_SUB.render("Función f(x)", True, ACCENT_LIGHT)
    screen.blit(func_label, (x, y))

    y += 35
    input_func_rect = pygame.Rect(x, y, w - 40, 36)

    draw_input_box(
        screen, input_func_rect,
        "f(x)", state.get("input_function", ""),
        state.get("active_field") == "func",
        state.get("cursor_show", True)
    )

    y += 100

    # ============================
    # BOTÓN DISPARAR (hover real)
    # ============================

    fire_btn = pygame.Rect(x, y, w - 40, 44)
    mouse = pygame.mouse.get_pos()
    hover_fire = fire_btn.collidepoint(mouse)

    draw_button(screen, fire_btn, "DISPARAR", hover_fire)

    y += 55

    # ============================
    # MENSAJE
    # ============================

    msg_label = FONT_SUB.render("Mensaje:", True, ACCENT)
    screen.blit(msg_label, (x, y))

    y += 30
    msg = FONT_SMALL.render(state.get("msg", ""), True, TEXT)
    screen.blit(msg, (x, y))

    y += 60

    # ============================
    # TOGGLE: Mostrar barcos
    # ============================

    toggle_rect = pygame.Rect(x, y, 180, 32)
    draw_toggle(
        screen, toggle_rect,
        "Mostrar barcos (pruebas)",
        state.get("show_ships", False)
    )

    # ============================
    # RETORNO
    # ============================

    return {
        "panel": panel,
        "diff_boxes": diff_boxes,
        "input_func": input_func_rect,
        "fire_btn": fire_btn,
        "btn_show_ships": toggle_rect,
    }
