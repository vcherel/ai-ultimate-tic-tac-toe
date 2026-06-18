from variables import variables, WHITE
from box_game import BoxGame

if variables.display_game:
    import pygame


class Board:
    def __init__(self, size):
        variables.set_screen_size(size)
        self.width, self.length = int(size * 7.5), int(size * 9)

        if variables.display_game:
            variables.set_screen(pygame.display.set_mode((self.width, self.length)))
            variables.screen.fill(WHITE)
            pygame.display.set_caption("Ultimate Tic Tac Toe")

        self.width_board = self.width
        self.length_board = self.length * 5 // 6
        self.width_lines = self.width_board // 50
        self.first_box: BoxGame = None

    def draw(self):
        self.first_box.draw_all()

    def try_click(self, pos):
        if 0 < pos[0] < self.width_board and 0 < pos[1] < self.length_board:
            return self.first_box.search_click(pos, self.get_all_playable_boxes())

    def get_all_playable_boxes(self):
        return self.first_box.get_all_playable_boxes()

    def init(self):
        if variables.display_game:
            self.first_box = BoxGame(
                depth=2,
                id_box=-1,
                parent=None,
                draw=True,
                x=0,
                y=0,
                width=self.width_board,
                width_line=self.width_lines,
            )
        else:
            self.first_box = BoxGame(depth=2, id_box=-1, parent=None, draw=False)


board = Board(variables.size_board)
