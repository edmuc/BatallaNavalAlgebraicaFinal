# logic.py
# Lógica principal del juego: disparos (funciones), pistas, puntaje
import re
import numpy as np
import math
import time

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)
from sympy import lambdify


from config import (
    DIFFICULTY_CONFIG,
    NEAR_THRESHOLD,
    HIT_TOLERANCE,
    HINTS_ORDER,
    TEXTO,
    GRID_SIZE,
)
from helpers import (
    distance,
    parse_input_coord,
    quadrant_of,
    signs_of,
    abs_compare,
    approx_distance_hint,
    coordinate_range_hint,
)
from ships import generate_ships, asignar_imagenes_barcos
from state import state, reset_state

from typing import Callable, Tuple, List

# Intentar integrar el módulo multiplayer (si existe)
try:
    import multiplayer
    MULTI_AVAILABLE = True
except Exception:
    multiplayer = None
    MULTI_AVAILABLE = False

# ------------------------------
# PARSER DE FUNCIONES (MEJORADO, VECTORIAL Y ROBUSTO)
# ------------------------------

x = sp.symbols('x')


def _parse_input_function(expr: str):
    """
    Parser completo, robusto y seguro.
    """
    if not expr:
        return None

    s = expr.lower().strip()

    # Reemplazos
    s = s.replace("^", "**")
    s = s.replace("ln", "log")
    s = s.replace("raiz", "sqrt")
    s = s.replace("abs", "Abs")
    s = re.sub(r"\be\b", "E", s)

    # Trigónmetricas (spanish)
    s = re.sub(r"\bsen\b", "sin", s)
    s = re.sub(r"\bsen(?=[(0-9a-z])", "sin", s)
    s = re.sub(r"\bcosec\b", "csc", s)

    # Inversas
    inv_map = {
        "arcsen": "asin", "arcsin": "asin",
        "arccos": "acos", "arctan": "atan",
        "arcsec": "asec", "arccosec": "acsc",
        "arccsc": "acsc", "arccot": "acot"
    }
    for a, b in inv_map.items():
        s = re.sub(rf"\b{a}\b", b, s)

    # Multiplicación implícita básica
    s = re.sub(r"(\d)(x)", r"\1*\2", s)
    s = re.sub(r"(x)([a-z])", r"\1*\2", s)

    funcs = ["sin","cos","tan","csc","sec","cot","asin","acos","atan","asec","acsc","acot","sqrt","log","exp"]
    for fn in funcs:
        s = re.sub(rf"\b{fn}\s+([0-9x(])", rf"{fn}(\1", s)

    # Cerrar paréntesis si faltan
    for fn in funcs:
        opens = s.count(fn + "(")
        closes = s.count(")")
        if closes < opens:
            s += ")" * (opens - closes)

    try:
        transformations = standard_transformations + (implicit_multiplication_application,)
        sym = parse_expr(s, transformations=transformations)
        f = lambdify(x, sym, modules=["numpy"])
        # prueba básica
        test = f(0)
        if isinstance(test, np.ndarray):
            test = float(test.astype(float)[0])
        else:
            test = float(test)
        return f
    except Exception as e:
        print("❌ ERROR PARSEANDO:", e)
        return None

parse_function = _parse_input_function

# ------------------------------
# HERRAMIENTAS DE APOYO
# ------------------------------

def nearest_ship_and_distance_point(shot: Tuple[float, float]):
    if not state.get("ships"):
        return None, float("inf")

    distances = []
    for i, ship in enumerate(state["ships"]):
        ds = [distance(shot, cell) for cell in ship["cells"]]
        distances.append((i, min(ds)))

    idx, d = min(distances, key=lambda x: x[1])
    return idx, round(d, 2)

def nearest_ship_and_distance_curve(f: Callable[[float], float], xs: List[float]):
    if not state.get("ships"):
        return None, float("inf")

    min_d = float("inf")
    min_idx = None

    for i, ship in enumerate(state["ships"]):
        for (cx, cy) in ship["cells"]:
            for x_val in xs:
                try:
                    y = f(x_val)
                except Exception:
                    continue
                d = math.hypot(x_val - cx, y - cy)
                if d < min_d:
                    min_d = d
                    min_idx = i
    return min_idx, round(min_d, 2)

def mark_hit_on_ship_by_point(ship, shot):
    for c in ship["cells"]:
        if distance(shot, c) <= HIT_TOLERANCE:
            return c
    return None

# ------------------------------
# DETECCIÓN DE IMPACTO CURVA–CELDA
# ------------------------------

def _point_in_cell(x_val, y_val, cx, cy):
    return (cx - 0.5) <= x_val <= (cx + 0.5) and (cy - 0.5) <= y_val <= (cy + 0.5)

def _segment_intersects_rect(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
    if rx1 <= x1 <= rx2 and ry1 <= y1 <= ry2:
        return True
    if rx1 <= x2 <= rx2 and ry1 <= y2 <= ry2:
        return True

    def _ccw(Ax, Ay, Bx, By, Cx, Cy):
        return (Cy - Ay) * (Bx - Ax) > (By - Ay) * (Cx - Ax)

    def _intersect(Ax, Ay, Bx, By, Cx, Cy, Dx, Dy):
        return (_ccw(Ax, Ay, Cx, Cy, Dx, Dy) != _ccw(Bx, By, Cx, Cy, Dx, Dy)) and (
            _ccw(Ax, Ay, Bx, By, Cx, Cy) != _ccw(Ax, Ay, Bx, By, Dx, Dy)
        )

    edges = [
        (rx1, ry1, rx2, ry1),
        (rx2, ry1, rx2, ry2),
        (rx2, ry2, rx1, ry2),
        (rx1, ry2, rx1, ry1),
    ]
    for ex1, ey1, ex2, ey2 in edges:
        if _intersect(x1, y1, x2, y2, ex1, ey1, ex2, ey2):
            return True
    return False

def _curve_hits_cell(f, cx, cy, xs, hit_tol):
    try:
        fy = f(cx)
        if abs(fy - cy) <= 1e-9:
            return True
    except:
        pass

    prev = None
    for x_val in xs:
        try:
            y_val = f(x_val)
        except:
            prev = None
            continue

        if math.hypot(x_val - cx, y_val - cy) <= hit_tol:
            return True

        if prev is not None:
            x0, y0 = prev
            if _segment_intersects_rect(
                x0, y0, x_val, y_val,
                cx - 0.5, cy - 0.5,
                cx + 0.5, cy + 0.5
            ):
                return True
        prev = (x_val, y_val)

    return False

# ------------------------------
# PISTAS
# ------------------------------

def get_next_hint():
    if not state.get("ships"):
        return "No hay barcos."

    # defensivo: asegurar keys
    state.setdefault("selected_ship_index", 0)
    state.setdefault("active_hint_index", 0)

    idx = min(state["selected_ship_index"], len(state["ships"]) - 1)
    ship = state["ships"][idx]
    cells = ship["cells"]
    center = cells[len(cells) // 2]
    r = DIFFICULTY_CONFIG[state["difficulty"]]["range"]

    kind = HINTS_ORDER[min(state.get("active_hint_index",0), len(HINTS_ORDER) - 1)]

    if kind == "cuadrante":
        return f"Pista: el barco #{idx+1} está en el cuadrante {quadrant_of(center)}."

    if kind == "signos":
        sx, sy = signs_of(center)
        return f"Pista: x es {sx}, y es {sy}."

    if kind == "abs_compare":
        return f"Pista: {abs_compare(center)}."

    if kind == "approx_distance":
        return f"Pista: {approx_distance_hint(center)}"

    if kind == "range_hint":
        return f"Pista: {coordinate_range_hint(center, r)}"

    return "Sin más pistas."

def use_hint():
    if not state.get("ships"):
        state["msg"] = "No hay barcos."
        return

    state.setdefault("hints_used", 0)
    state.setdefault("selected_ship_index", 0)
    state.setdefault("active_hint_index", 0)

    max_hints = len(HINTS_ORDER) * len(state["ships"])
    if state["hints_used"] >= max_hints:
        state["msg"] = "No quedan más pistas."
        return

    state["active_hint_index"] = (state["active_hint_index"] + 1) % len(HINTS_ORDER)

    if state["active_hint_index"] == 0:
        state["selected_ship_index"] = (state["selected_ship_index"] + 1) % max(1, len(state["ships"]))

    state["hints_used"] += 1
    state["msg"] = get_next_hint()

# ------------------------------
# DISPARO
# ------------------------------

def fire_shot():
    """
    Ejecuta el disparo con la función f(x).
    En modo multijugador:
      - bloquea si no es tu turno
      - calcula impacto respecto a enemy_ships (si están disponibles)
      - envía el disparo a Firebase vía multiplayer.send_shot(...)
      - envía una curva muestreada (lista de puntos) para verificación/depuración
    """
    # bloqueo por turno si estamos en multijugador
    if state.get("multiplayer"):
        # si no hay datos de turno aún, no permitir
        if state.get("turn") is None:
            state["msg"] = "Esperando sincronización del servidor..."
            return
        # comprobar que es mi turno
        my_pid = state.get("player_id")
        if my_pid is None:
            state["msg"] = "No identificado en la partida."
            return
        if state.get("turn") != my_pid:
            state["msg"] = "No es tu turno."
            return

    expr = state.get("input_function", "").strip()
    if expr == "":
        state["msg"] = "Ingrese una función válida (ej: 2x+1, sen(x), sqrt(x)+3)."
        return

    f = _parse_input_function(expr)
    if f is None:
        state["msg"] = "Función inválida o vacía."
        return

    # guardar función activa
    state["active_func_expr"] = expr
    state["active_func_callable"] = f

    cfg = DIFFICULTY_CONFIG[state["difficulty"]]
    rng = cfg["range"]

    # Puntos para graficar (vectorizado)
    xs_np = np.linspace(-rng, rng, 1000)
    plot_points = []
    try:
        ys_np = f(xs_np)
        mask = np.isfinite(ys_np)
        plot_points = list(zip(xs_np[mask].tolist(), ys_np[mask].tolist()))
    except Exception:
        # Fallback escalar
        step = 0.1
        xs = [i * step for i in range(int(-rng / step), int(rng / step) + 1)]
        for xv in xs:
            try:
                yv = float(f(xv))
                if math.isfinite(yv):
                    plot_points.append((xv, yv))
            except:
                continue

    state["func_plot_points"] = plot_points  # renderer lo usa

    # ---------- detección de impacto ----------
    step = 0.1
    xs = [i * step for i in range(int(-rng / step), int(rng / step) + 1)]

    impacto = False
    celda_impactada = None
    barco_impactado = None

    # Si estamos en multijugador, preferimos comparar contra enemy_ships (si están)
    target_ships = state["enemy_ships"] if state.get("multiplayer") and state.get("enemy_ships") else state.get("ships", [])

    for ship in target_ships:
        for (cx, cy) in ship["cells"]:
            try:
                hit = _curve_hits_cell(f, cx, cy, xs, HIT_TOLERANCE)
            except Exception:
                hit = False

            if hit:
                impacto = True
                celda_impactada = (cx, cy)
                barco_impactado = ship
                break
        if impacto:
            break

    # Contadores/registro local (mantener compatibilidad con tu proyecto)
    state.setdefault("attempts", 0)
    state.setdefault("hits", [])
    state.setdefault("misses", [])
    state.setdefault("animating", [])
    state.setdefault("flash_effects", [])

    state["attempts"] += 1

    if impacto:
        # si ya habías golpeado esa celda
        if celda_impactada in state["hits"]:
            state["msg"] = "Ya habías golpeado esa casilla."
        else:
            state["hits"].append(celda_impactada)
            state["msg"] = f"¡Impacto con f(x) = {expr}!"
            state["animating"].append({"pos": celda_impactada, "t": 0, "max": 18, "color": (255,160,80), "image": None})
            state["flash_effects"].append({"pos": celda_impactada, "t": 0, "max": 22, "color": (220,60,60)})

            if barco_impactado and all(c in state["hits"] for c in barco_impactado["cells"]):
                barco_impactado["sunk"] = True
                state["msg"] += " ¡Hundiste el barco!"

    else:
        state["misses"].append(expr)
        state["lives"] = state.get("lives", 0) - 1

        # limpiar efectos previos de miss_func
        state["animating"] = [a for a in state.get("animating", []) if a.get("type") != "miss_func"]
        state["flash_effects"] = [f for f in state.get("flash_effects", []) if f.get("type") != "miss_func"]

        idx, d = nearest_ship_and_distance_curve(f, xs)

        if d <= NEAR_THRESHOLD:
            state["msg"] = f"¡Casi! distancia al barco más cercano: {d:.2f}"
        else:
            state["msg"] = f"Fallaste. distancia al barco más cercano: {d:.2f}"

        state["animating"].append({
            "pos": (0, 0),
            "t": 0,
            "max": 40,
            "color": (64, 224, 208),
            "type": "miss_func",
            "func_expr": expr
        })

        try:
            pos = (0, f(0))
            state["flash_effects"].append({
                "pos": pos,
                "t": 0,
                "max": 22,
                "color": (64, 224, 208),
                "type": "miss_func_flash"
            })
        except:
            pass

    # ----------------------------
    #  Enviar resultado a multiplayer (si aplica)
    # ----------------------------
    if state.get("multiplayer"):
        # decidir coordenada objetivo para enviar: prioridad celda_impactada, sino punto central de la curva
        if celda_impactada:
            tx, ty = celda_impactada
        elif plot_points:
            mid = plot_points[len(plot_points)//2]
            tx, ty = round(mid[0]), round(mid[1])
        else:
            tx, ty = 0, 0

        sent_hit = bool(impacto)

        # registrar en mis tiros locales
        state.setdefault("my_hits", [])
        state["my_hits"].append((tx, ty, sent_hit))

        # preparar curva muestreada para enviar (limitar tamaño)
        curve_to_send = []
        try:
            if plot_points:
                max_points = 80  # limitar para no enviar payload gigante
                step = max(1, len(plot_points) // max_points)
                sampled = plot_points[::step]
                # serializar como listas de ints/float
                curve_to_send = [[float(round(p[0], 3)), float(round(p[1], 3))] for p in sampled]
        except Exception:
            curve_to_send = []

        if MULTI_AVAILABLE:
            try:
                multiplayer.send_shot(tx, ty, sent_hit, curve=curve_to_send)
            except Exception as e:
                print("Error enviando disparo a multiplayer:", e)
                state["msg"] += " (Error enviando al servidor.)"
        else:
            state["msg"] += " (Modo local - multiplayer no disponible)"

    # limpiar input y estado de edición
    state["input_function"] = ""
    state["active_field"] = None

    # comprobar victoria local
    if all(s.get("sunk", False) for s in state.get("ships", [])):
        state["victoria"] = True
        state["msg"] = "¡Has hundido todas las naves! Felicidades."
        return

    if state.get("lives", 0) <= 0:
        ships_str = ", ".join(str(s["cells"]) for s in state.get("ships") or []) 
        state["msg"] = f"Perdiste. Los barcos estaban en: {ships_str}"
        state["derrota"] = True
        return

    # Si estamos en multijugador, chequear si el enemigo hundió todos mis barcos (local check)
    if state.get("multiplayer") and MULTI_AVAILABLE:
        try:
            multiplayer.check_my_defeat()
        except Exception:
            pass

# ------------------------------
# NUEVO JUEGO
# ------------------------------

def new_game():
    from ui.grid import setup_grid_params

    reset_state()
    cfg = DIFFICULTY_CONFIG[state["difficulty"]]
    grid_range = cfg["range"]

    cell_size = GRID_SIZE / (grid_range * 2)

    # generar barcos locales
    state["ships"] = generate_ships()
    asignar_imagenes_barcos(cell_size)

    setup_grid_params()

    # Si estamos en multijugador y tenemos match_id: subir barcos y arrancar listener
    if state.get("multiplayer") and MULTI_AVAILABLE and state.get("match_id"):
        try:
            multiplayer.upload_my_ships()
        except Exception as e:
            print("No se pudo subir barcos:", e)
        try:
            # start listener solo si no estaba conectado
            if not state.get("connected"):
                multiplayer.start_listener()
                state["connected"] = True
        except Exception as e:
            print("No se pudo iniciar listener:", e)

    return state

# ------------------------------
# PUNTAJE
# ------------------------------

def calculate_score():
    base = 100
    state.setdefault("attempts", 0)
    state.setdefault("lives", 0)
    state.setdefault("misses", [])
    score = max(0, base + state["lives"] * 10 - state["attempts"] * 5 - len(state["misses"]) * 2)
    return score

def get_ship_positions(game_state):
    positions = []
    for ship in game_state.get("ships", []):
        positions.extend(ship["cells"])
    return positions
