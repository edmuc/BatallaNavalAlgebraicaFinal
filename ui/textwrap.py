# ui/textwrap.py
# Renderizado de texto con salto de línea automático


def render_wrapped_text(surface, text, x, y, font, color, max_width, max_lines=None, line_spacing=4):
    """
    Dibuja texto con salto de línea si excede el ancho máximo.
    """
    words = text.split(" ")
    line = ""
    lines_drawn = 0

    for word in words:
        test_line = (line + " " + word).strip()
        w, h = font.size(test_line)

        if w <= max_width:
            line = test_line
        else:
            # Renderiza la línea actual
            if line:
                surface.blit(font.render(line, True, color), (x, y))
                y += h + line_spacing
                lines_drawn += 1

                if max_lines and lines_drawn >= max_lines:
                    # Indicar que hay más texto
                    ellipsis = font.render("...", True, color)
                    surface.blit(ellipsis, (x + max_width - 20, y - h))
                    return

            line = word

    # Línea final
    if line:
        surface.blit(font.render(line, True, color), (x, y))