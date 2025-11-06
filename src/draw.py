from variables import variables, RED, BLUE, WHITE
from utils import convert_pos

if variables.display_game:
    import pygame

POS_SYMBOL = 2.7, 8.3
SYMBOL_SIZE = 0.3
CROSS_WIDTH = 9
CIRCLE_WIDTH = 6


def draw_cross(pos, size, width, color=BLUE, convert=False):
    """
    pos = coordinates of the center
    width = INTEGER
    """
    if not variables.display_game:
        raise ValueError('The game is not displayed')
    
    if convert:
        x, y = convert_pos(pos)
        size = convert_pos(size)
    else:
        x, y = pos
    
    x, y = int(x - size/2), int(y - size/2)  # Find the top left corner of the cross
    screen = variables.screen
    pygame.draw.line(screen, color, (x, y), (x + size, y + size), width)
    pygame.draw.line(screen, color, (x + size, y), (x, y + size), width)


def draw_circle(pos, size, width, color=RED, convert=False):
    """
    pos = coordinates of the center
    width = INTEGER
    """
    if not variables.display_game:
        raise ValueError('The game is not displayed')
    
    if convert:
        x, y = convert_pos(pos)
        size = convert_pos(size)
    else:
        x, y = pos
    
    pygame.draw.circle(variables.screen, color, (x, y), size // 2, width)


def draw_actual_player(team, erase=False):
    """
    team = team of the player that we want to draw (True = circle, False = cross)
    """
    if not variables.display_game:
        raise ValueError('The game is not displayed')
    
    if team:
        if erase:
            draw_circle(POS_SYMBOL, size=SYMBOL_SIZE, width=CIRCLE_WIDTH, color=WHITE, convert=True)
        else:
            draw_circle(POS_SYMBOL, size=SYMBOL_SIZE, width=CIRCLE_WIDTH, convert=True)
    else:
        if erase:
            draw_cross(POS_SYMBOL, size=SYMBOL_SIZE, width=CROSS_WIDTH, color=WHITE, convert=True)
        else:
            draw_cross(POS_SYMBOL, size=SYMBOL_SIZE, width=CROSS_WIDTH, convert=True)