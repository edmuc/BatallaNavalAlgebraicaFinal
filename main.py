# main.py — Integración con Firebase (ajustado a firebase_config.py + multiplayer.py)
import pygame
import sys
import time

from config import WIDTH, HEIGHT, FPS, SMALL, FONT_BIG, FONT_VICTORY, GRID_LEFT, GRID_TOP, GRID_SIZE, TEXTO
from state import state
from logic import new_game, fire_shot, use_hint, calculate_score
from ui.grid import setup_grid_params, draw_grid
from ui.effects import draw_flash_effects, draw_animations
# IMPORTANTE: ahora traemos también draw_multiplayer_menu y draw_room_input
from ui.menu import draw_menu, draw_howto, draw_multiplayer_menu, draw_room_input
from ui.panel import draw_panel, draw_button

# usar tu configuración existente
from firebase_config import auth, db

# intentar usar el módulo multiplayer (el que contiene create_match/create_game, join_match/join_game, upload_my_ships, start_listener, stop_listener, etc.)
try:
    import multiplayer as mp_module
    MULTI_IMPL = True
except Exception:
    mp_module = None
    MULTI_IMPL = False

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Batalla Naval Algebraica")

# Inicializaciones defensivas en el state
state.setdefault("input_function", "")
state.setdefault("active_field", None)
state.setdefault("cursor_show", True)
state.setdefault("last_cursor_toggle", time.time())
state.setdefault("victoria", False)
state.setdefault("derrota", False)
state.setdefault("screen_state", "menu")  # "menu", "howto", "multiplayer_menu", "playing", "room_input"
state.setdefault("start_in_multiplayer", False)
state.setdefault("multiplayer_mode", None)  # "create" or "join" when selected
state.setdefault("mp_initialized", False)
state.setdefault("match_id", None)
state.setdefault("player_id", None)
state.setdefault("user_email", None)

# estado para input de sala
state.setdefault("room_input_text", "")
state.setdefault("room_action", None)  # "create" or "join"

# Si quieres login automático demo (opcional; puedes dejar False si usas login UI)
AUTO_LOGIN_DEMO = False
DEMO_EMAIL = "demo@correo.com"
DEMO_PASS = "demopass"


def draw_debug_ships(screen):
    # intenta usar world_to_screen si está disponible
    try:
        from ui.grid import world_to_screen
    except Exception:
        world_to_screen = None

    for ship in state.get("ships", []):
        for (cx, cy) in ship.get("cells", []):
            if world_to_screen:
                sx, sy = world_to_screen((cx, cy))
            else:
                sx = GRID_LEFT + (cx + state.get("grid_range", 5)) * state.get("cell_size", 20)
                sy = GRID_TOP + (state.get("grid_range", 5) - cy) * state.get("cell_size", 20)
            if ship.get("image") is None:
                pygame.draw.circle(screen, (255, 80, 80), (int(sx), int(sy)), 6)
            else:
                screen.blit(ship["image"], ship["image"].get_rect(center=(int(sx), int(sy))))


# ----------------------------
# Helpers robustos para multiplayer (soportan nombres distintos de API)
# ----------------------------
def _mp_create_game(email, sala_key=None):
    """Intenta crear partida. Si sala_key se pasa, lo usa (ej 'sala1'). Devuelve match_id (string) o None."""
    if not MULTI_IMPL:
        return None
    try:
        if sala_key and hasattr(mp_module, "create_match"):
            # muchos create_match esperan (email, sala)
            return mp_module.create_match(email, sala_key)
        if hasattr(mp_module, "create_match") and sala_key is None:
            # algunos create_match manejan la sala internamente
            return mp_module.create_match(email)
        if hasattr(mp_module, "create_game"):
            return mp_module.create_game()
        # fallback: escribir directamente en db
        gid = str(int(time.time()))
        db.child("games").child(gid).set({"created": time.time(), "host": email})
        return gid
    except Exception as e:
        print("Error create_game:", e)
        return None


def _mp_join_game(game_id, email):
    """
    Intenta unirse usando join_match/join_game; devuelve True (o match_id) / False.
    game_id puede ser 'sala1' o 'sala2' o cualquier id que tu implementación use.
    """
    if not MULTI_IMPL:
        return False
    try:
        if hasattr(mp_module, "join_match"):
            res = mp_module.join_match(game_id, email)
            # join_match puede devolver (bool, msg), bool, o match_id. Normalizamos:
            if isinstance(res, tuple):
                ok = bool(res[0])
                return game_id if ok else False
            if isinstance(res, bool):
                return game_id if res else False
            if isinstance(res, str):
                # matches.py devolvía la sala
                return res
            return False
        if hasattr(mp_module, "join_game"):
            return mp_module.join_game(game_id, email)
        # fallback: update db direct
        db.child("games").child(game_id).update({"guest": email})
        return game_id
    except Exception as e:
        print("Error join_game:", e)
        return False


def _mp_upload_my_ships():
    if not MULTI_IMPL:
        return
    try:
        if hasattr(mp_module, "upload_my_ships"):
            mp_module.upload_my_ships()
        elif hasattr(mp_module, "upload_ships"):
            mp_module.upload_ships()
        else:
            # fallback: push ships under games/<id>/ships_<player>
            mid = state.get("match_id")
            pid = state.get("player_id") or "p1"
            if mid:
                serial = []
                for ship in state.get("ships", []):
                    serial.append([[int(c[0]), int(c[1])] for c in ship.get("cells", [])])
                db.child("games").child(mid).child(f"{pid}_ships").set(serial)
    except Exception as e:
        print("Error uploading ships:", e)


def _mp_start_listener():
    if not MULTI_IMPL:
        return
    try:
        if hasattr(mp_module, "start_listener"):
            mp_module.start_listener()
        else:
            # no-op for simple module
            pass
    except Exception as e:
        print("Error starting listener:", e)


def try_create_and_join_match(mode="create"):
    """
    legacy helper kept for console-based flow.
    Prefer UI-based creation (room input) which uses direct calls.
    """
    email = state.get("user_email") or DEMO_EMAIL

    if mode == "create":
        mid = _mp_create_game(email)
        if not mid:
            return None
        state["match_id"] = mid
        state["player_id"] = "p1"
        joined = _mp_join_game(mid, email)
        if not joined:
            print("Warning: no se pudo unirse inmediatamente a la partida creada.")
        return mid

    if mode == "join":
        try:
            code = input("Introduce el código de la sala a unir: ").strip()
        except Exception:
            code = None
        if not code:
            print("No se introdujo código.")
            return None
        joined = _mp_join_game(code, email)
        if joined:
            state["match_id"] = code
            state["player_id"] = "p2"
            return code
        return None

    return None


# ----------------------------
# MAIN
# ----------------------------
def main():

    # Opcional: login automático demo (sólo si no usas login UI)
    if AUTO_LOGIN_DEMO:
        try:
            auth.sign_in_with_email_and_password(DEMO_EMAIL, DEMO_PASS)
            state["user_email"] = DEMO_EMAIL
            print("Demo: login automático OK")
        except Exception:
            print("Demo: no se pudo iniciar sesión automáticamente")

    # Nuevo juego inicial
    new_game()

    running = True
    while running:
        clock.tick(FPS)

        # Cursor parpadeante
        now = time.time()
        if now - state["last_cursor_toggle"] >= 0.5:
            state["cursor_show"] = not state["cursor_show"]
            state["last_cursor_toggle"] = now

        # DIBUJO de pantallas según state["screen_state"]
        if state.get("screen_state") == "menu":
            interactive = draw_menu(screen, WIDTH, HEIGHT)

        elif state.get("screen_state") == "howto":
            interactive = draw_howto(screen, WIDTH, HEIGHT)

        elif state.get("screen_state") == "multiplayer_menu":
            interactive = draw_multiplayer_menu(screen, WIDTH, HEIGHT)

        elif state.get("screen_state") == "room_input":
            # mostramos la pantalla para escribir la sala (1 o 2)
            interactive = draw_room_input(screen, WIDTH, HEIGHT, state.get("room_input_text", ""))
        else:
            screen.fill((18, 30, 52))

            setup_grid_params()
            draw_grid(screen, SMALL)

            if state.get("reveal_ships", False) or state.get("show_ships", False):
                draw_debug_ships(screen)

            grid_rect = pygame.Rect(GRID_LEFT, GRID_TOP, GRID_SIZE, GRID_SIZE)

            panel_data = draw_panel(
                screen,
                grid_rect,
                WIDTH - (GRID_LEFT + GRID_SIZE + 40),
                GRID_SIZE
            )

            interactive = {
                "input_func": panel_data.get("input_func"),
                "btn_fire": panel_data.get("fire_btn"),
                "diff_boxes": panel_data.get("diff_boxes", []),
                "btn_show_ships": panel_data.get("btn_show_ships"),
            }

            draw_flash_effects(screen)
            draw_animations(screen)

            # Overlay victoria/derrota
            if state.get("victoria") or state.get("derrota"):
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))

                if state.get("victoria"):
                    texto = FONT_VICTORY.render("¡Ganaste!", True, (255, 215, 0))
                    sub = SMALL.render(
                        f"Intentos: {state.get('attempts',0)}  Puntaje: {calculate_score()}",
                        True,
                        TEXTO
                    )
                else:
                    texto = FONT_VICTORY.render("Has perdido", True, (255, 80, 80))
                    sub = SMALL.render("Reinicia para intentarlo nuevamente.", True, TEXTO)

                screen.blit(texto, (WIDTH//2 - texto.get_width()//2, 150))
                screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 210))

                big_rect = pygame.Rect(WIDTH//2 - 80, 260, 160, 50)
                draw_button(screen, big_rect, "Reiniciar")
                interactive["victory_reset"] = big_rect

        pygame.display.flip()

        # EVENTOS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # ---------------- MENU ----------------
            if state.get("screen_state") == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if interactive.get("btn_start") and interactive["btn_start"].collidepoint(event.pos):
                        state["screen_state"] = "playing"
                        new_game()
                    elif interactive.get("btn_multi") and interactive["btn_multi"].collidepoint(event.pos):
                        # abrir submenú multijugador
                        state["screen_state"] = "multiplayer_menu"
                    elif interactive.get("btn_how") and interactive["btn_how"].collidepoint(event.pos):
                        state["screen_state"] = "howto"
                    elif interactive.get("btn_quit") and interactive["btn_quit"].collidepoint(event.pos):
                        running = False
                continue

            # ------------- MULTIPLAYER MENU -------------
            if state.get("screen_state") == "multiplayer_menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if interactive.get("btn_create") and interactive["btn_create"].collidepoint(event.pos):
                        # pasar a pantalla input para pedir la sala (1 o 2)
                        print("🟢 Crear sala seleccionado (abrir input)")
                        state["room_input_text"] = ""
                        state["room_action"] = "create"
                        state["screen_state"] = "room_input"
                    elif interactive.get("btn_join") and interactive["btn_join"].collidepoint(event.pos):
                        print("🟢 Unirse a sala seleccionado (abrir input)")
                        state["room_input_text"] = ""
                        state["room_action"] = "join"
                        state["screen_state"] = "room_input"
                    elif interactive.get("btn_back") and interactive["btn_back"].collidepoint(event.pos):
                        state["screen_state"] = "menu"
                continue

            # --------------- ROOM INPUT ----------------
            if state.get("screen_state") == "room_input":
                # mouse clicks on buttons in input UI
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if interactive.get("btn_ok") and interactive["btn_ok"].collidepoint((mx, my)):
                        # aceptar el texto
                        choice = state.get("room_input_text", "").strip()
                        if choice not in ["1", "2"]:
                            print("Sala inválida. Escribe '1' o '2'.")
                        else:
                            sala_key = f"sala{choice}"  # normalizamos a 'sala1' / 'sala2'
                            email = state.get("user_email") or DEMO_EMAIL
                            action = state.get("room_action")
                            if action == "create":
                                # crear sala específica
                                mid = None
                                if MULTI_IMPL:
                                    # intenta usar la API del módulo
                                    try:
                                        if hasattr(mp_module, "create_match"):
                                            mid = mp_module.create_match(email, sala_key)
                                        else:
                                            mid = _mp_create_game(email, sala_key)
                                    except Exception as e:
                                        print("Error creando sala:", e)
                                else:
                                    mid = sala_key
                                if mid:
                                    state["match_id"] = mid
                                    state["player_id"] = "p1"
                                    state["multiplayer"] = True
                                    state["mp_initialized"] = True
                                    _mp_upload_my_ships()
                                    _mp_start_listener()
                                    state["screen_state"] = "playing"
                                    new_game()
                                else:
                                    print("No se pudo crear la sala.")
                            elif action == "join":
                                joined = False
                                if MULTI_IMPL:
                                    try:
                                        res = _mp_join_game(sala_key, email)
                                        if res:
                                            # res puede ser match_id string
                                            state["match_id"] = res
                                            state["player_id"] = "p2"
                                            joined = True
                                    except Exception as e:
                                        print("Error uniendo a sala:", e)
                                else:
                                    # offline fallback, treat as joined
                                    joined = True
                                    state["match_id"] = sala_key
                                    state["player_id"] = "p2"
                                if joined:
                                    state["multiplayer"] = True
                                    state["mp_initialized"] = True
                                    _mp_upload_my_ships()
                                    _mp_start_listener()
                                    state["screen_state"] = "playing"
                                    new_game()
                                else:
                                    print("No se unió a la sala.")
                    elif interactive.get("btn_back") and interactive["btn_back"].collidepoint(event.pos):
                        state["screen_state"] = "multiplayer_menu"
                        state["room_input_text"] = ""
                        state["room_action"] = None

                # teclado para escribir la sala (1 o 2)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state["screen_state"] = "multiplayer_menu"
                        state["room_input_text"] = ""
                        state["room_action"] = None
                    elif event.key == pygame.K_BACKSPACE:
                        state["room_input_text"] = state.get("room_input_text", "")[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # simular click en aceptar
                        choice = state.get("room_input_text", "").strip()
                        if choice in ["1", "2"]:
                            # trigger same logic as click ok by posting a fake mouse event at btn_ok center
                            # but simpler: reuse branch by directly calling the acceptance logic:
                            # we reuse the same code path by synthesizing a MOUSEBUTTONDOWN handled above (but here simply call)
                            sala_key = f"sala{choice}"
                            email = state.get("user_email") or DEMO_EMAIL
                            action = state.get("room_action")
                            if action == "create":
                                mid = None
                                if MULTI_IMPL:
                                    try:
                                        if hasattr(mp_module, "create_match"):
                                            mid = mp_module.create_match(email, sala_key)
                                        else:
                                            mid = _mp_create_game(email, sala_key)
                                    except Exception as e:
                                        print("Error creando sala:", e)
                                else:
                                    mid = sala_key
                                if mid:
                                    state["match_id"] = mid
                                    state["player_id"] = "p1"
                                    state["multiplayer"] = True
                                    state["mp_initialized"] = True
                                    _mp_upload_my_ships()
                                    _mp_start_listener()
                                    state["screen_state"] = "playing"
                                    new_game()
                                else:
                                    print("No se pudo crear la sala.")
                            elif action == "join":
                                joined = False
                                if MULTI_IMPL:
                                    try:
                                        res = _mp_join_game(sala_key, email)
                                        if res:
                                            state["match_id"] = res
                                            state["player_id"] = "p2"
                                            joined = True
                                    except Exception as e:
                                        print("Error uniendo a sala:", e)
                                else:
                                    joined = True
                                    state["match_id"] = sala_key
                                    state["player_id"] = "p2"
                                if joined:
                                    state["multiplayer"] = True
                                    state["mp_initialized"] = True
                                    _mp_upload_my_ships()
                                    _mp_start_listener()
                                    state["screen_state"] = "playing"
                                    new_game()
                                else:
                                    print("No se unió a la sala.")
                        else:
                            print("Sala inválida. Escribe '1' o '2'.")
                    else:
                        # aceptar solo caracteres numéricos sencillos (1 o 2)
                        char = event.unicode
                        if char and char in "12" and len(state.get("room_input_text","")) < 2:
                            state["room_input_text"] = (state.get("room_input_text","") + char)[:2]

                continue

            # ---------------- HOWTO ----------------
            if state.get("screen_state") == "howto":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if interactive.get("btn_back") and interactive["btn_back"].collidepoint(event.pos):
                        state["screen_state"] = "menu"
                continue

            # ---------------- PLAYING ----------------
            if state.get("screen_state") == "playing":
                # Reiniciar en overlay
                if (state.get("victoria") or state.get("derrota")) and event.type == pygame.MOUSEBUTTONDOWN:
                    if "victory_reset" in interactive and interactive["victory_reset"].collidepoint(event.pos):
                        new_game()
                        # si estamos online, re-subir barcos
                        if MULTI_IMPL and state.get("multiplayer") and state.get("match_id"):
                            _mp_upload_my_ships()
                        state["active_field"] = None
                    continue

                # CLICK RATÓN
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # activar input
                    if interactive.get("input_func") and interactive["input_func"].collidepoint((mx, my)):
                        state["active_field"] = "func"
                        continue
                    else:
                        state["active_field"] = None

                    # dificultad
                    for dif, rect in interactive.get("diff_boxes", []):
                        if rect.collidepoint((mx, my)):
                            state["difficulty"] = dif
                            new_game()
                            # si multijugador: re-subir barcos
                            if MULTI_IMPL and state.get("multiplayer") and state.get("match_id"):
                                _mp_upload_my_ships()
                            state["active_field"] = None
                            break
                    else:
                        # disparo
                        if interactive.get("btn_fire") and interactive["btn_fire"].collidepoint((mx, my)):
                            fire_shot()
                            state["active_field"] = None
                            # logic.fire_shot() manda al multiplayer si está habilitado
                            continue

                        # toggle mostrar barcos
                        if interactive.get("btn_show_ships") and interactive["btn_show_ships"].collidepoint((mx, my)):
                            state["show_ships"] = not state.get("show_ships", False)
                            state["msg"] = f"Mostrar barcos: {state['show_ships']}"
                            state["active_field"] = None
                            continue

                # TECLADO
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state["screen_state"] = "menu"
                        state["active_field"] = None
                        continue

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if not (state.get("victoria") or state.get("derrota")):
                            fire_shot()
                            state["active_field"] = None
                        continue

                    # escribir función
                    if state.get("active_field") == "func":
                        if event.key == pygame.K_BACKSPACE:
                            state["input_function"] = state.get("input_function", "")[:-1]
                            continue
                        if event.unicode:
                            char = event.unicode
                            if char.isalnum() or char in "+-*/().=<>^e, ":
                                state["input_function"] = state.get("input_function", "") + char
                            continue

                    if event.key == pygame.K_m:
                        state["show_ships"] = not state.get("show_ships", False)
                        continue

        # small sleep to reduce CPU (optional)
        time.sleep(0.001)

    # Al salir, si hay listener en multiplayer, detenerlo
    if MULTI_IMPL:
        try:
            if hasattr(mp_module, "stop_listener"):
                mp_module.stop_listener()
        except Exception:
            pass

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
