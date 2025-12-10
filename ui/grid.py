# ui/grid.py
# Dibujo del grid y conversión de coordenadas

import pygame
from config import (
    GRID_LEFT, GRID_TOP, GRID_SIZE,
    GRID_COLOR, AXIS_COLOR, TEXTO,
    DIFFICULTY_CONFIG,
)
from state import state
from logic import parse_function

CELL_SIZE = None


# ------------------------------
# AJUSTE DEL GRID
# ------------------------------
def setup_grid_params():
    global CELL_SIZE
    cfg = DIFFICULTY_CONFIG[state["difficulty"]]
    r = cfg["range"]
    ticks = r * 2
    CELL_SIZE = GRID_SIZE / ticks if ticks > 0 else 1


# ------------------------------
# COORDENADAS
# ------------------------------
def world_to_screen(point):
    x, y = point
    cx = GRID_LEFT + GRID_SIZE // 2
    cy = GRID_TOP + GRID_SIZE // 2
    sx = cx + (x * CELL_SIZE)
    sy = cy - (y * CELL_SIZE)
    return sx, sy 


def screen_to_world(px, py):
    cx = GRID_LEFT + GRID_SIZE // 2
    cy = GRID_TOP + GRID_SIZE // 2
    x = (px - cx) / CELL_SIZE
    y = (cy - py) / CELL_SIZE
    return x, y


# ------------------------------
# COLOCAR BARCOS MANUALMENTE
# ------------------------------
def place_ship_at_click(mouse_pos):
    if not state.get("placing_ships", False):
        return

    px, py = mouse_pos

    if not (GRID_LEFT <= px <= GRID_LEFT + GRID_SIZE and
            GRID_TOP  <= py <= GRID_TOP  + GRID_SIZE):
        return

    wx, wy = screen_to_world(px, py)

    wx = round(wx)
    wy = round(wy)

    state["ships"].append({
        "pos": (wx, wy),
        "image": None
    })

    state["ships_to_place"] -= 1

    if state["ships_to_place"] <= 0:
        state["placing_ships"] = False
        state["msg"] = "Todos los barcos han sido colocados."
    else:
        state["msg"] = f"Barco colocado en ({wx}, {wy}). Faltan {state['ships_to_place']}."


# ------------------------------
# DIBUJO DE FUNCIÓN f(x)
# ------------------------------
# ------------------------------
# DIBUJO DE FUNCIÓN f(x) (robusto: usa func_plot_points o input_function)
# ------------------------------
def draw_function(screen):
    """
    Dibuja la función:
    - Si existe state['func_plot_points'] (generada por fire_shot), la dibuja directamente.
    - Si no, intenta parsear state['input_function'] y dibujarla en tiempo real.
    """

    # ---------------------------------------------------------------------
    # 1) SI EXISTEN PUNTOS PRECOMPUTADOS (después de DISPARAR)
    # ---------------------------------------------------------------------
    pts = state.get("func_plot_points")
    if pts:
        screen_pts = []
        for xw, yw in pts:
            try:
                sx, sy = world_to_screen((xw, yw))

                # SOLO se dibuja si está dentro del GRID
                if (GRID_LEFT <= sx <= GRID_LEFT + GRID_SIZE and
                    GRID_TOP  <= sy <= GRID_TOP  + GRID_SIZE):

                    screen_pts.append((int(sx), int(sy)))
                else:
                    if len(screen_pts) > 1:
                        pygame.draw.lines(screen, (255, 200, 40), False, screen_pts, 2)
                    screen_pts = []
            except:
                if len(screen_pts) > 1:
                    pygame.draw.lines(screen, (255, 200, 40), False, screen_pts, 2)
                screen_pts = []

        if len(screen_pts) > 1:
            pygame.draw.lines(screen, (255, 200, 40), False, screen_pts, 2)
        return


    # ---------------------------------------------------------------------
    # 2) SI NO HAY PUNTOS (dibujar función en tiempo real mientras escriben)
    # ---------------------------------------------------------------------
    func_str = state.get("input_function", "").strip()
    if not func_str:
        return

    try:
        f = parse_function(func_str)
    except:
        f = None

    if f is None:
        return

    cfg = DIFFICULTY_CONFIG[state["difficulty"]]
    r = cfg["range"]

    step_world = max(0.02, (r * 2) / 1000.0)
    screen_pts = []

    x = -r
    while x <= r + 1e-9:
        try:
            y = f(x)
            if hasattr(y, "__len__"):
                y = float(y[0]) if len(y) > 0 else float("nan")
            y = float(y)

            sx, sy = world_to_screen((x, y))

            # SOLO dentro del grid, no invade panel, no sigue al infinito
            if (GRID_LEFT <= sx <= GRID_LEFT + GRID_SIZE and
                GRID_TOP  <= sy <= GRID_TOP + GRID_SIZE):

                screen_pts.append((int(sx), int(sy)))
            else:
                if len(screen_pts) > 1:
                    pygame.draw.lines(screen, (150, 230, 255), False, screen_pts, 2)
                screen_pts = []

        except:
            if len(screen_pts) > 1:
                pygame.draw.lines(screen, (150, 230, 255), False, screen_pts, 2)
            screen_pts = []

        x += step_world

    if len(screen_pts) > 1:
        pygame.draw.lines(screen, (150, 230, 255), False, screen_pts, 2)

# ------------------------------
# DIBUJO DEL GRID
# ------------------------------
def draw_grid(screen, SMALL_FONT):

    pygame.draw.rect(
        screen,
        (5, 25, 55),
        (GRID_LEFT - 3, GRID_TOP - 3, GRID_SIZE + 6, GRID_SIZE + 6),
        border_radius=10
    )

    cfg = DIFFICULTY_CONFIG[state["difficulty"]]
    r = cfg["range"]

    cx = GRID_LEFT + GRID_SIZE // 2
    cy = GRID_TOP + GRID_SIZE // 2

    # Líneas finas
    for i in range(-r, r + 1):
        x = cx + i * CELL_SIZE
        y = cy + i * CELL_SIZE

        line_color = (40, 70, 110)
        pygame.draw.line(screen, line_color, (x, GRID_TOP), (x, GRID_TOP + GRID_SIZE))
        pygame.draw.line(screen, line_color, (GRID_LEFT, y), (GRID_LEFT + GRID_SIZE, y))

    # Líneas principales
    for i in range(-r, r + 1):
        if i % 1 == 0:
            x = cx + i * CELL_SIZE
            y = cy + i * CELL_SIZE

            pygame.draw.line(screen, (60, 100, 150), (x, GRID_TOP), (x, GRID_TOP + GRID_SIZE), 1)
            pygame.draw.line(screen, (60, 100, 150), (GRID_LEFT, y), (GRID_LEFT + GRID_SIZE, y), 1)

    # Ejes
    pygame.draw.line(screen, (200, 200, 255), (cx, GRID_TOP), (cx, GRID_TOP + GRID_SIZE), 3)
    pygame.draw.line(screen, (200, 200, 255), (GRID_LEFT, cy), (GRID_LEFT + GRID_SIZE, cy), 3)

    # Numeración
    for i in range(-r, r + 1):
        x = cx + i * CELL_SIZE
        y = cy + i * CELL_SIZE
        txt = SMALL_FONT.render(str(i), True, TEXTO)
        screen.blit(txt, (x - txt.get_width() // 2, GRID_TOP - 20))
        screen.blit(txt, (GRID_LEFT - 30, y - txt.get_height() // 2))

    # --- NUEVO: dibujar disparos del enemigo (Firebase) ---
    draw_enemy_hits(screen)

    # Dibuja función, barcos, etc.
    draw_function(screen)
    draw_ships(screen)


# ------------------------------
# MOSTRAR BARCOS (debug)
# ------------------------------
def draw_ships(screen):
    if not state.get("show_ships", False):
        return

    ships = state.get("ships", [])
    if not ships:
        return

    for ship in ships:
        img = ship.get("image")
        if img is None:
            continue

        x0, y0 = ship["pos"]

        px, py = world_to_screen((x0, y0))

        px -= CELL_SIZE / 2
        py -= CELL_SIZE / 2

        screen.blit(img, (int(px), int(py)))

def draw_enemy_hits(screen):
    """Dibuja los disparos del enemigo que vienen de Firebase."""
    if not state.get("multiplayer", False):
        return

    hits = state.get("enemy_hits", [])
    if not hits:
        return

    for item in hits:

        # --- Caso 1: tupla (x, y, hit)
        if isinstance(item, (list, tuple)):
            if len(item) == 3:
                xw, yw, hit = item
            elif len(item) >= 4:
                xw, yw, hit = item[:3]  # ignorar extra
            else:
                continue

        # --- Caso 2: diccionario de Firebase
        elif isinstance(item, dict):
            xw = item.get("x")
            yw = item.get("y")
            hit = item.get("hit")
            if xw is None or yw is None:
                continue

        else:
            continue

        sx, sy = world_to_screen((xw, yw))

        color = (255, 80, 80) if hit else (180, 180, 255)
        pygame.draw.circle(screen, color, (int(sx), int(sy)), 6)
