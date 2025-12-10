# multiplayer.py — Sistema de partidas online para Batalla Naval Algebraica
# Adaptado para salas fijas: "1" y "2"
# Mejora: listener y operaciones de red en hilos para evitar bloquear Pygame.

import time
import threading
from state import state

# IMPORTANTE: firebase_config.py debe exponer `db`
try:
    from firebase_config import db
    FB_AVAILABLE = True
except Exception as e:
    print("⚠ multiplayer.py: firebase_config.db no disponible:", e)
    db = None
    FB_AVAILABLE = False

_listener = None           # objeto stream devuelto por pyrebase (si aplica)
_listener_thread = None    # hilo que ejecuta la stream
_listener_lock = threading.Lock()


# ============================================
#   CREAR SALA (resetea sala 1 o 2)
# ============================================
def create_match(player_email: str, sala: str):
    """
    Crea o reinicia una sala fija ("1" o "2").
    Esta función es síncrona (hace set en Firebase). Su latencia depende de la red.
    """
    if not FB_AVAILABLE:
        raise RuntimeError("Firebase no disponible")

    match_id = sala  # usamos sala 1 o sala 2

    payload = {
        "player1": player_email,
        "player2": None,
        "turn": "p1",
        "p1_ready": False,
        "p2_ready": False,
        "p1_ships": [],
        "p2_ships": [],
        "p1_hits": {},
        "p2_hits": {},
        "winner": None,
        "created_at": time.time()
    }

    try:
        # Sobrescribimos la sala SIEMPRE
        db.child("matches").child(match_id).set(payload)
    except Exception as e:
        print("Error creando sala en Firebase:", e)
        return None

    state["match_id"] = match_id
    state["player_id"] = "p1"
    state["multiplayer"] = True
    state["connected"] = False

    print(f"✔ Sala {match_id} creada (reset).")
    return match_id


# ============================================
#  UNIRSE A SALA (1 o 2)
# ============================================
def join_match(sala: str, player_email: str):
    """
    Intenta unirse como jugador 2.
    Devuelve (True, msg) o (False, msg) para compatibilidad con usos anteriores.
    """
    if not FB_AVAILABLE:
        return False, "Firebase no disponible"

    match_id = sala

    try:
        match = db.child("matches").child(match_id).get().val()
    except Exception as e:
        print("Error leyendo sala:", e)
        return False, "Error leyendo sala"

    if not match:
        return False, f"La sala {match_id} no existe."
    if match.get("player2"):
        return False, f"La sala {match_id} ya está llena."

    try:
        db.child("matches").child(match_id).update({
            "player2": player_email,
            "p2_ready": False
        })
    except Exception as e:
        print("Error actualizando sala:", e)
        return False, "Error al actualizar sala"

    state["match_id"] = match_id
    state["player_id"] = "p2"
    state["multiplayer"] = True
    state["connected"] = False

    print(f"✔ Te uniste a la sala {match_id}")
    return True, "Unido correctamente."


# ============================================
#   SUBIR MIS BARCOS (ahora no-bloqueante)
# ============================================
def upload_my_ships():
    """
    Subir barcos en background para no bloquear UI.
    """
    if not FB_AVAILABLE:
        print("⚠ upload_my_ships: Firebase no disponible")
        return

    mid = state.get("match_id")
    pid = state.get("player_id")

    if not mid or not pid:
        print("⚠ upload_my_ships: falta match_id o player_id")
        return

    ships_serialized = []
    for ship in state.get("ships", []):
        cells = ship.get("cells") or []
        ship_cells = [[int(c[0]), int(c[1])] for c in cells]
        ships_serialized.append(ship_cells)

    key = f"{pid}_ships"

    def _worker():
        try:
            db.child("matches").child(mid).update({
                key: ships_serialized,
                f"{pid}_ready": True
            })
            print("✔ Barcos subidos a Firebase (background).")
        except Exception as e:
            print("Error subiendo barcos (background):", e)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


# ============================================
#   ENVIAR DISPARO (no-bloqueante)
# ============================================
def send_shot(x, y, hit: bool, curve=None):
    """
    Envía un disparo a Firebase en un hilo para evitar congelar la UI.
    """
    if not FB_AVAILABLE:
        print("⚠ send_shot: Firebase no disponible")
        return

    mid = state.get("match_id")
    pid = state.get("player_id")

    if not mid or not pid:
        print("⚠ send_shot: falta match_id o player_id")
        return

    enemy = "p2" if pid == "p1" else "p1"

    shot = {
        "x": int(x),
        "y": int(y),
        "hit": bool(hit),
        "curve": curve or [],
        "t": time.time(),
        "from": pid
    }

    def _worker(shot_obj, mid_local, pid_local, enemy_local):
        try:
            db.child("matches").child(mid_local).child(f"{pid_local}_hits").push(shot_obj)
            db.child("matches").child(mid_local).update({"turn": enemy_local})
            print(f"📡 Disparo enviado a Firebase (background): ({shot_obj['x']},{shot_obj['y']}) hit={shot_obj['hit']}")
        except Exception as e:
            print("Error enviando disparo (background):", e)

    t = threading.Thread(target=_worker, args=(shot, mid, pid, enemy), daemon=True)
    t.start()


# ============================================
#   LISTENER DE PARTIDA (corre en thread seguro)
# ============================================
def start_listener():
    """
    Inicia la stream de Firebase en un hilo separado para no bloquear el main loop de Pygame.
    Guarda el objeto stream en _listener y el hilo en _listener_thread.
    """
    global _listener, _listener_thread

    if not FB_AVAILABLE:
        print("⚠ start_listener: Firebase no disponible")
        return

    mid = state.get("match_id")
    if not mid:
        print("⚠ start_listener: falta match_id")
        return

    # si ya hay un listener para el mismo mid, no reiniciamos
    with _listener_lock:
        if _listener_thread and _listener_thread.is_alive():
            print("🔵 Listener ya activo (no se inicia otro).")
            return

    def watcher(evt):
        # Este callback puede ser llamado desde el thread de pyrebase.
        # Intentamos leer snapshot completo, si falla usamos evt.data
        try:
            snapshot = db.child("matches").child(mid).get().val() or {}
        except Exception:
            snapshot = evt.data if isinstance(evt.data, dict) else {}

        pid = state.get("player_id")
        if not pid:
            return

        enemy = "p2" if pid == "p1" else "p1"

        # turnos
        if "turn" in snapshot:
            state["turn"] = snapshot.get("turn")

        # ganador
        if snapshot.get("winner"):
            state["winner"] = snapshot.get("winner")
            state["game_over"] = True
            print("🏁 Winner detectado:", state["winner"])

        # barcos del enemigo
        enemy_ships_raw = snapshot.get(f"{enemy}_ships")
        enemy_ships = []
        if isinstance(enemy_ships_raw, list):
            for ship_cells in enemy_ships_raw:
                try:
                    cells = [(int(c[0]), int(c[1])) for c in ship_cells]
                    enemy_ships.append({"cells": cells, "sunk": False})
                except:
                    continue
        state["enemy_ships"] = enemy_ships

        # disparos del enemigo
        enemy_hits_raw = snapshot.get(f"{enemy}_hits") or {}
        enemy_hits = []
        if isinstance(enemy_hits_raw, dict):
            for k, shot in enemy_hits_raw.items():
                try:
                    enemy_hits.append((
                        int(shot.get("x", 0)),
                        int(shot.get("y", 0)),
                        bool(shot.get("hit", False)),
                        shot.get("curve", []) or []
                    ))
                except:
                    continue

        state["enemy_hits"] = enemy_hits

        # conectado = ambos jugadores existen
        state["connected"] = bool(snapshot.get("player1") and snapshot.get("player2"))

    def _run_stream():
        nonlocal mid
        try:
            stream_obj = db.child("matches").child(mid).stream(watcher)
            # guardar el objeto stream globalmente para poder cerrarlo después
            with _listener_lock:
                global _listener
                _listener = stream_obj
            # la llamada a stream suele retornar sólo cuando se cierra, así que aquí termina el thread
        except Exception as e:
            print("⚠ Error en listener thread:", e)
            with _listener_lock:
                _listener = None

    # lanzar el hilo
    t = threading.Thread(target=_run_stream, daemon=True)
    t.start()
    with _listener_lock:
        _listener_thread = t
    print(f"🟢 Listener thread iniciado para sala {mid}")


# ============================================
#   VERIFICAR SI PERDÍ
# ============================================
def check_my_defeat():
    my_ships = state.get("ships", [])
    if not my_ships:
        return

    enemy_hits = [(x, y) for (x, y, hit, *_)
                  in state.get("enemy_hits", []) if hit]

    enemy_hits_set = set(enemy_hits)

    total_cells = 0
    destroyed = 0
    for ship in my_ships:
        cells = ship.get("cells", [])
        total_cells += len(cells)
        for c in cells:
            if (int(c[0]), int(c[1])) in enemy_hits_set:
                destroyed += 1

    if total_cells > 0 and destroyed >= total_cells:
        mid = state.get("match_id")
        enemy_pid = "p2" if state.get("player_id") == "p1" else "p1"

        try:
            db.child("matches").child(mid).update({"winner": enemy_pid})
        except:
            pass

        state["winner"] = enemy_pid
        state["game_over"] = True
        print("💀 Has perdido (todos tus barcos fueron destruidos).")


# ============================================
#   DETENER LISTENER
# ============================================
def stop_listener(timeout=1.0):
    """
    Cierra el stream y espera al thread un tiempo razonable.
    """
    global _listener, _listener_thread
    with _listener_lock:
        if _listener:
            try:
                _listener.close()
            except Exception:
                pass
            _listener = None

    # esperar que el thread termine (no obligatorio porque es daemon)
    try:
        if _listener_thread and _listener_thread.is_alive():
            _listener_thread.join(timeout)
    except Exception:
        pass

    _listener_thread = None
    state["connected"] = False
    print("🔴 Listener detenido.")

