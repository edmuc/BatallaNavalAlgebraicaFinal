# events.py (ARREGLADO)
import pygame
from logic import *
from config import *

def handle_events(state, interactive):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # ------------------------------------
        # 1. MANEJO DE CLICS DEL RATÓN
        # ------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Clic en campo f(x)
            if interactive and interactive.get("input_func", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                state["active_field"] = "func"
            else:
                state["active_field"] = None

            # Clic en botón DISPARAR
            if interactive and interactive.get("fire_btn", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                fire_shot()

            # Toggle mostrar barcos
            if interactive and interactive.get("btn_show_ships", pygame.Rect(0,0,0,0)).collidepoint(mouse_pos):
                state["show_ships"] = not state.get("show_ships", False)

            # Botones de dificultad
            if interactive and interactive.get("diff_boxes"):
                for dif, rect in interactive["diff_boxes"]:
                    if rect.collidepoint(mouse_pos):
                        state["difficulty"] = dif
                        new_game()

        # ------------------------------------
        # 2. MANEJO DE TECLADO PARA f(x)
        # ------------------------------------
        if state.get("active_field") == "func":
            if event.type == pygame.KEYDOWN:
                current_input = state.get("input_function", "")

                if event.key == pygame.K_BACKSPACE:
                    state["input_function"] = current_input[:-1]

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    fire_shot()

                else:
                    new_char = event.unicode
                    if new_char and (new_char.isalnum() or new_char in "+-*/().=<>^ e"):
                        state["input_function"] = current_input + new_char

    return True
