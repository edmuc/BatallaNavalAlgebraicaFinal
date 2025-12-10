# ui/effects.py
# Animaciones y efectos visuales del juego

import pygame
from ui.grid import world_to_screen, CELL_SIZE
from state import state

# ------------------------------
# EFECTOS FLASH
# ------------------------------

def draw_flash_effects(screen):
    """
    Efectos breves de expansión circular semitransparente.
    """
    new_effects = []

    for fx in state["flash_effects"]:
        fx["t"] += 1
        px, py = world_to_screen(fx["pos"])
        frac = fx["t"] / fx["max"]
        radius = int(6 + frac * 40)
        alpha = max(0, 255 - int(frac * 255))

        surf = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
        color = (*fx["color"], alpha)
        pygame.draw.circle(surf, color, (radius + 3, radius + 3), radius, 3)

        screen.blit(surf, (px - radius - 3, py - radius - 3))

        if fx["t"] < fx["max"]:
            new_effects.append(fx)

    state["flash_effects"] = new_effects


# ------------------------------
# ANIMACIONES DE IMPACTOS
# ------------------------------

def draw_animations(screen, explosion_image=None):
    """
    Efectos para impactos o eventos especiales.
    """
    new_list = []

    for anim in state["animating"]:
        anim["t"] += 1
        px, py = world_to_screen(anim["pos"])
        frac = anim["t"] / anim["max"]
        radius = int(5 + frac * 60)
        alpha = max(0, 255 - int(frac * 255))

        surf = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*anim["color"], alpha), (radius + 3, radius + 3), radius, 3)
        screen.blit(surf, (px - radius - 3, py - radius - 3))

        # Imagen de explosión opcional
        if explosion_image and anim.get("image"):
            w = int(CELL_SIZE * 0.9)
            h = int(CELL_SIZE * 0.9)
            try:
                scaled = pygame.transform.smoothscale(explosion_image, (w, h))
                rect = scaled.get_rect(center=(px, py))
                screen.blit(scaled, rect.topleft)
            except Exception:
                pass

        if anim["t"] < anim["max"]:
            new_list.append(anim)

    state["animating"] = new_list
