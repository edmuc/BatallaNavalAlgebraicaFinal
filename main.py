# main.py
# Punto de entrada del juego con estructura modular (versión corregida)

import pygame
import sys
import time
import config

from config import WIDTH, HEIGHT, FPS, SMALL, FONT_BIG, FONT_VICTORY, GRID_LEFT, GRID_TOP, GRID_SIZE, TEXTO
from state import state
from logic import new_game, fire_shot, use_hint, calculate_score
from ui.grid import setup_grid_params, draw_grid, world_to_screen
from ui.effects import draw_flash_effects, draw_animations
from ui.menu import draw_menu, draw_howto
from ui.panel import draw_panel, draw_button

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Batalla Naval Algebraica")

# Map index -> difficulty string
DIFF_INDEX_TO_STR = {0: "easy", 1: "medium", 2: "hard"}
DIFF_STR_TO_INDEX = {v: k for k, v in DIFF_INDEX_TO_STR.items()}


def draw_debug_ships(screen):
    """Dibuja los barcos cuando state['show_ships'] o reveal_ships está activo."""
    for ship in state.get("ships", []):
        for (cx, cy) in ship.get("cells", []):
            sx, sy = world_to_screen((cx, cy))
            if ship.get("image") is None:
                pygame.draw.circle(screen, (255, 80, 80), (sx, sy), 6)
            else:
                screen.blit(ship["image"], ship["image"].get_rect(center=(sx, sy)))


def main():

    # Inicializar variables del input
    state.setdefault("input_function", "")
    state.setdefault("active_field", None)

    new_game()
    running = True

    while running:
        clock.tick(FPS)

        # Cursor parpadeante
        now = time.time()
        if now - state["last_cursor_toggle"] >= 0.5:
            state["cursor_show"] = not state["cursor_show"]
            state["last_cursor_toggle"] = now

        # ============================
        # DIBUJO
        # ============================

        if state["screen_state"] == "menu":
            interactive = draw_menu(screen, WIDTH, HEIGHT)

        elif state["screen_state"] == "howto":
            interactive = draw_howto(screen, WIDTH, HEIGHT)

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

            # IMPORTANTE: USAMOS input_func (de panel.py)
            interactive = {
                "input_func": panel_data.get("input_func"),
                "btn_fire": panel_data.get("fire_btn"),
                "diff_boxes": panel_data.get("diff_boxes", []),
                "btn_show_ships": panel_data.get("btn_show_ships"),
            }

            draw_flash_effects(screen)
            draw_animations(screen)

            # Overlay victoria/derrota
            if state["victoria"] or state["derrota"]:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))

                if state["victoria"]:
                    texto = FONT_VICTORY.render("¡Ganaste!", True, (255, 215, 0))
                    sub = SMALL.render(
                        f"Intentos: {state['attempts']}  Puntaje: {calculate_score()}",
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

        # ============================
        # EVENTOS
        # ============================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # ---------------- MENU ----------------
            if state["screen_state"] == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if interactive["btn_start"].collidepoint(event.pos):
                        state["screen_state"] = "playing"
                        new_game()
                    elif interactive["btn_how"].collidepoint(event.pos):
                        state["screen_state"] = "howto"
                    elif interactive["btn_quit"].collidepoint(event.pos):
                        running = False
                continue

            # -------------- HOW TO ----------------
            if state["screen_state"] == "howto":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if interactive["btn_back"].collidepoint(event.pos):
                        state["screen_state"] = "menu"
                continue

            # ============== JUGANDO ==============
            if state["screen_state"] == "playing":

                # Reset en victoria
                if (state["victoria"] or state["derrota"]) and event.type == pygame.MOUSEBUTTONDOWN:
                    if "victory_reset" in interactive and interactive["victory_reset"].collidepoint(event.pos):
                        new_game()
                        state["active_field"] = None
                    continue

                # -------- CLICK RATÓN --------
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # Activar input
                    if interactive.get("input_func") and interactive["input_func"].collidepoint((mx, my)):
                        state["active_field"] = "func"
                    else:
                        state["active_field"] = None

                    # Dificultad
                    for dif, rect in interactive.get("diff_boxes", []):
                        if rect.collidepoint((mx, my)):
                            state["difficulty"] = dif
                            new_game()
                            state["active_field"] = None
                            break

                    else:
                        # Disparo
                        if interactive.get("btn_fire") and interactive["btn_fire"].collidepoint((mx, my)):
                            fire_shot()
                            state["active_field"] = None
                            continue

                        # Toggle mostrar barcos
                        if interactive.get("btn_show_ships") and interactive["btn_show_ships"].collidepoint((mx, my)):
                            state["show_ships"] = not state.get("show_ships", False)
                            state["msg"] = f"Mostrar barcos: {state['show_ships']}"
                            state["active_field"] = None
                            continue

                # -------- TECLADO --------
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        state["screen_state"] = "menu"
                        state["active_field"] = None
                        continue

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if not (state["victoria"] or state["derrota"]):
                            fire_shot()
                            state["active_field"] = None
                        continue

                    # --- ESCRIBIR FUNCIÓN ---
                    if state["active_field"] == "func":

                        # borrar
                        if event.key == pygame.K_BACKSPACE:
                            state["input_function"] = state["input_function"][:-1]
                            continue

                        # escribir
                        if event.unicode:
                            char = event.unicode
                            if char.isalnum() or char in "+-*/().=<>^e, ":
                                state["input_function"] += char
                            continue

                    # Toggle M
                    if event.key == pygame.K_m:
                        state["show_ships"] = not state.get("show_ships", False)
                        continue

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
