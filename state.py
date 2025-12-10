# state.py — Estado global del juego (incluye multijugador)
import time
from config import DIFFICULTY_CONFIG

state = {

    # -------------------------
    # 🔵 PANTALLAS DEL JUEGO
    # -------------------------
    "screen_state": "menu",          # menu, howto, multiplayer_menu, playing

    # -------------------------
    # ⚙ DIFICULTAD
    # -------------------------
    "difficulty": "medium",

    # -------------------------
    # 🚢 BARCOS Y DISPAROS
    # -------------------------
    "ships": [],
    "hits": [],
    "misses": [],

    # -------------------------
    # ⚙ MODO AVANZADO (colocar barcos)
    # -------------------------
    "placing_ships": False,
    "ships_to_place": 0,

    # -------------------------
    # ❤️ VIDAS Y PROGRESO
    # -------------------------
    "lives": 0,
    "max_lives": 0,
    "attempts": 0,

    # -------------------------
    # 💡 PISTAS
    # -------------------------
    "hints_used": 0,
    "active_hint_index": 0,
    "selected_ship_index": 0,

    # -------------------------
    # ✨ ANIMACIONES
    # -------------------------
    "animating": [],
    "flash_effects": [],
    "cursor_show": True,
    "last_cursor_toggle": time.time(),

    # -------------------------
    # ⌨ ENTRADA DEL JUGADOR
    # -------------------------
    "input_x": "",
    "input_y": "",
    "input_function": "",
    "active_func": "",    
    "active_field": None,

    # -------------------------
    # 📝 MENSAJES
    # -------------------------
    "msg": "",

    # -------------------------
    # 🏁 ESTADO FINAL
    # -------------------------
    "victoria": False,
    "derrota": False,

    # -------------------------
    # 🔍 DEPURACIÓN
    # -------------------------
    "reveal_ships": False,
    "show_ships": False,

    # ==========================================================
    # 🔥 MULTIJUGADOR — NUEVO BLOQUE COMPLETO
    # ==========================================================

    # ¿Estamos en modo multijugador?
    "multiplayer_mode": None,       # "create", "join", None
    "mp_initialized": False,

    # Info de Firebase
    "firebase_uid": None,

    # Información de la sala
    "game_id": None,
    "player_id": None,              # player1 o player2

    # Turnos
    "current_turn": "player1",      # por defecto

    # Disparos recibidos de Firebase
    "remote_shots": [],

    # Chat en tiempo real
    "chat_messages": [],
    "chat_input": "",
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

    # Entradas
    state["input_x"] = ""
    state["input_y"] = ""
    state["input_function"] = ""
    state["active_func"] = ""
    state["active_field"] = None

    # Mensajes
    state["msg"] = "Juego reiniciado."
    state["victoria"] = False
    state["derrota"] = False

    # Efectos
    state["flash_effects"] = []
    state["animating"] = []
    state["cursor_show"] = True

    # Depuración
    state["reveal_ships"] = False

    # Avanzado
    state["placing_ships"] = False
    state["ships_to_place"] = 0

    # -------------------------
    # 🔥 MULTIJUGADOR
    # -------------------------
    state["remote_shots"] = []
    state["chat_messages"] = []
    state["chat_input"] = ""
    # turnos NO se reinician si es modo online
    if state.get("multiplayer_mode"):
        state["msg"] = "Esperando al otro jugador..."

    return state
