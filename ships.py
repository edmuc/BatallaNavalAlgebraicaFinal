# ships.py
# Generación de barcos y asignación de imágenes

import random
import pygame
from config import SHIP_SIZE, DIFFICULTY_CONFIG, IMG_BARCO_H, IMG_BARCO_V
from state import state

# ------------------------------
# GENERACIÓN DE BARCOS
# ------------------------------

def generate_ships():
    cfg = DIFFICULTY_CONFIG[state["difficulty"]]
    rng = cfg["range"]
    num = cfg["ships"]

    ships = []
    occupied = set()
    attempts = 0

    while len(ships) < num and attempts < 5000:
        attempts += 1
        orient = random.choice(["h", "v"])

        if orient == "h":
            x0 = random.randint(-rng, rng - SHIP_SIZE + 1)
            y0 = random.randint(-rng, rng)
            cells = [(x0 + i, y0) for i in range(SHIP_SIZE)]
        else:
            x0 = random.randint(-rng, rng)
            y0 = random.randint(-rng, rng - SHIP_SIZE + 1)
            cells = [(x0, y0 + i) for i in range(SHIP_SIZE)]

        if any(c in occupied for c in cells):
            continue

        ship = {
            "cells": cells,
            "orient": orient,
            "pos": (x0, y0),
            "sunk": False,
            "image": None,
        }
        ships.append(ship)

        for c in cells:
            occupied.add(c)

    return ships


# ------------------------------
# ASIGNAR IMÁGENES
# ------------------------------

def asignar_imagenes_barcos(cell_size):
    if IMG_BARCO_H is None and IMG_BARCO_V is None:
        return

    for ship in state["ships"]:
        orient = ship["orient"]
        pixel_w = max(2, int(abs(cell_size) * SHIP_SIZE))
        pixel_h = max(2, int(abs(cell_size)))

        try:
            if orient == "h":
                if IMG_BARCO_H is not None:
                    img = pygame.transform.smoothscale(IMG_BARCO_H, (pixel_w, pixel_h))
                else:
                    img = pygame.transform.rotate(
                        pygame.transform.smoothscale(IMG_BARCO_V, (pixel_h, pixel_w)), -90
                    )
            else:
                if IMG_BARCO_V is not None:
                    img = pygame.transform.smoothscale(IMG_BARCO_V, (pixel_h, pixel_w))
                else:
                    img = pygame.transform.rotate(
                        pygame.transform.smoothscale(IMG_BARCO_H, (pixel_w, pixel_h)), 90
                    )

            ship["image"] = img
        except Exception:
            ship["image"] = None
