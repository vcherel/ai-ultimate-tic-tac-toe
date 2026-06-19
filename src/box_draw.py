from variables import variables, BLACK, GREEN, WHITE
from draw import draw_circle, draw_cross
from text import change_text_victory

if variables.display_game:
    import pygame


class BoxDraw:
    """Drawing counterpart to BoxGame — game logic lives in BoxGame."""

    def __init__(self, x, y, width, width_line):
        self.x, self.y = x, y  # top-left corner
        self.width = width
        self.width_line = width_line
        self.box_size = width // 3
        self.center = (x + width // 2, y + width // 2)
        self.color = WHITE

    def draw(self, small_box, big_box, state):
        """
        small_box: True if the box has no children (leaf cell or won sub-board)
        big_box: True if this is the outermost board
        """
        if small_box:
            pygame.draw.rect(
                variables.screen, self.color, (self.x, self.y, self.width, self.width)
            )
            if state is not None:
                self.draw_symbol(state)

        if not big_box:  # no border around the outermost box — looks cleaner
            screen = variables.screen
            pygame.draw.line(
                screen,
                BLACK,
                (self.x, self.y),
                (self.x + self.width, self.y),
                self.width_line,
            )
            pygame.draw.line(
                screen,
                BLACK,
                (self.x, self.y),
                (self.x, self.y + self.width),
                self.width_line,
            )
            pygame.draw.line(
                screen,
                BLACK,
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.width),
                self.width_line,
            )
            pygame.draw.line(
                screen,
                BLACK,
                (self.x, self.y + self.width),
                (self.x + self.width, self.y + self.width),
                self.width_line,
            )

    def draw_symbol(self, state):
        """state must not be None when called"""
        if state:
            draw_circle(
                self.center, size=self.box_size * 1.8, width=int(self.box_size * 0.4)
            )
        else:
            draw_cross(
                self.center, size=self.box_size * 1.4, width=int(self.box_size * 0.5)
            )

    def search_click(self, small_box, state, playable, pos):
        if small_box:
            if state is not None or not playable:
                return None
            else:
                return True

        row = (pos[1] - self.y) // self.box_size
        col = (pos[0] - self.x) // self.box_size

        if row < 0 or row > 2 or col < 0 or col > 2:
            return None

        return row * 3 + col

    def draw_winning_line(self, start, end, color):
        line_width = max(4, self.width // 25)
        pygame.draw.line(variables.screen, color, start, end, line_width)

    def make_playable(self):
        self.color = GREEN

    def make_unplayable(self, victory):
        self.color = WHITE
        if victory:
            change_text_victory("The winner is :")
