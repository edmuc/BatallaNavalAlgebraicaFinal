# helpers.py
# Funciones matemáticas y utilitarias del juego

import math

# ------------------------------
# Utilidades matemáticas
# ------------------------------

def distance(a, b):
    """
    Distancia Euclidiana entre dos puntos (x1, y1) y (x2, y2).
    """
    return math.hypot(a[0] - b[0], a[1] - b[1])


def quadrant_of(point):
    """
    Determina el cuadrante del punto.
    """
    x, y = point
    if x == 0 and y == 0:
        return "origen"
    if x == 0:
        return "sobre eje Y"
    if y == 0:
        return "sobre eje X"
    if x > 0 and y > 0:
        return "I"
    if x < 0 and y > 0:
        return "II"
    if x < 0 and y < 0:
        return "III"
    return "IV"


def signs_of(point):
    x, y = point
    sx = "positivo" if x > 0 else ("negativo" if x < 0 else "cero")
    sy = "positivo" if y > 0 else ("negativo" if y < 0 else "cero")
    return sx, sy


def abs_compare(point):
    """
    Compara |x| y |y|.
    """
    x, y = point
    ax, ay = abs(x), abs(y)
    if ax > ay:
        return "|x| > |y|"
    if ax < ay:
        return "|x| < |y|"
    return "|x| = |y|"


def approx_distance_hint(point):
    """
    Distancia aproximada del punto al origen.
    """
    d = round(math.hypot(point[0], point[1]), 1)
    if d < 5:
        return f"El barco está relativamente cerca (≈ {d})."
    if d < 15:
        return f"Distancia moderada al origen (≈ {d})."
    return f"Está bastante lejos (≈ {d})."


def coordinate_range_hint(point, r):
    """
    Genera un rango aproximado de coordenadas como pista.
    """
    x, y = point
    span = max(1, r // 6)
    ax = int(x) - span, int(x) + span
    ay = int(y) - span, int(y) + span
    return f"x ∈ [{ax[0]}, {ax[1]}], y ∈ [{ay[0]}, {ay[1]}]"


# ------------------------------
# Parsing
# ------------------------------

def parse_input_coord(value):
    """
    Convierte una cadena a float aceptando coma o punto.
    """
    s = value.strip().replace(",", ".")
    if s == "":
        raise ValueError("Vacío")
    return float(s)

# ------------------------------
# Parser de funciones algebraicas
# ------------------------------

import sympy as sp
x = sp.symbols("x")

def parse_function(expr):
    """
    Convierte la expresión escrita por el jugador en una función f(x).
    Ejemplos válidos:
    2x+1
    x^2 - 3x + 5
    sin(x)
    sqrt(x)+4
    exp(x)
    abs(x)
    """
    try:
        expr = expr.replace("^", "**").replace(" ", "")
        f = sp.sympify(expr, {
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "sqrt": sp.sqrt, "abs": sp.Abs,
            "exp": sp.exp, "ln": sp.log
        })
        return sp.lambdify(x, f, "math")
    except:
        return None
