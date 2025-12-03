# state.py
# Manejo del estado global del juego

from config import DIFFICULTY_CONFIG
import time

# Estado inicial del juego
state = {
    "screen_state": "menu",  # "menu", "howto", "playing"
    "difficulty": "medium",

    # Barcos y disparos
    "ships": [],
    "hits": [],
    "misses": [],

    # Modo avanzado (colocar barcos manualmente)
    "placing_ships": False,     # ← NUEVO
    "ships_to_place": 0,        # ← NUEVO

    # Vidas y progreso
    "lives": 0,
    "max_lives": 0,
    "attempts": 0,

    # Pistas
    "hints_used": 0,
    "active_hint_index": 0,
    "selected_ship_index": 0,

    # Animaciones y efectos
    "animating": [],
    "flash_effects": [],
    "cursor_show": True,
    "last_cursor_toggle": time.time(),

    # Entrada del jugador
    "input_x": "",
    "input_y": "",
    "input_function": "",  
    "active_func": "",      
    "active_field": None,   

    # Mensaje de estado
    "msg": "",

    # Flags de fin de juego
    "victoria": False,
    "derrota": False,

    # Depuración / modo simulación
    "reveal_ships": False,
    "show_ships": False,
}

# -------------------------------------------------
# Reinicia completamente el estado
# -------------------------------------------------

def reset_state():
    global state

    cfg = DIFFICULTY_CONFIG[state["difficulty"]]

    # Barcos, disparos
    state["ships"] = []
    state["hits"] = []
    state["misses"] = []
    state["attempts"] = 0

    # Pistas
    state["hints_used"] = 0
    state["active_hint_index"] = 0
    state["selected_ship_index"] = 0

    # Vidas
    state["max_lives"] = cfg["lives"]
    state["lives"] = cfg["lives"]

    # Entradas del usuario
    state["input_x"] = ""
    state["input_y"] = ""
    state["input_function"] = ""
    state["active_func"] = ""
    state["active_field"] = None

    # Mensajes y flags
    state["msg"] = "Juego reiniciado."
    state["victoria"] = False
    state["derrota"] = False

    # Animaciones
    state["flash_effects"] = []
    state["animating"] = []

    # Cursor visual
    state["cursor_show"] = True

    # Modo revelado
    state["reveal_ships"] = False

    # 🔥 Reiniciar modo avanzado
    state["placing_ships"] = False
    state["ships_to_place"] = 0

    return state
