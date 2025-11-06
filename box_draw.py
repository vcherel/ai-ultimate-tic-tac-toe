from variables import variables, BLACK, GREEN, WHITE
from draw import draw_circle, draw_cross
from text import change_text_victory

if variables.display_game:
    import pygame


class BoxDraw:
    """
    The box represent any square in the tic tac toe game, in the file, 
    there is mainly drawing functions, the game logic is in the BoxGame class
    """
    def __init__(self, x, y, width, width_line):
        self.x, self.y = x, y  # Top left corner coordinates
        self.width = width
        self.width_line = width_line
        self.box_size = width // 3
        self.center = (x + width // 2, y + width // 2)
        self.color = WHITE

    def draw(self, small_box, big_box, state):
        """
        small_box : True if the box doesn't have childs
        big_box : True if the box is the biggest one (the one that contains all the others)
        """
        # Draw the background if it is a box at the end of the board
        if small_box:
            pygame.draw.rect(variables.screen, self.color, (self.x, self.y, self.width, self.width))
        
        # Draw the lines around the box
        if not big_box:  # We don't draw the lines around the big box (it's ugly)
            screen = variables.screen
            pygame.draw.line(screen, BLACK, (self.x, self.y), (self.x + self.width, self.y), self.width_line)
            pygame.draw.line(screen, BLACK, (self.x, self.y), (self.x, self.y + self.width), self.width_line)
            pygame.draw.line(screen, BLACK, (self.x + self.width, self.y), (self.x + self.width, self.y + self.width), self.width_line)
            pygame.draw.line(screen, BLACK, (self.x, self.y + self.width), (self.x + self.width, self.y + self.width), self.width_line)
        
        # Draw the symbol if there is one
        if state is not None:
            self.draw_symbol(state)

    def draw_symbol(self, state):
        """
        This function draws the appropriate symbol in the center of the box
        If we arrive here, state cannot be None
        """        
        if state:
            draw_circle(self.center, size=self.box_size * 1.8, width=int(self.box_size * 0.4))
        else:
            draw_cross(self.center, size=self.box_size * 1.4, width=int(self.box_size * 0.5))

    def search_click(self, small_box, state, playable, pos):
        """
        Returns True if the box has been clicked
        """     
        if small_box:
            # If there is already something in the box or if you don't have the right to play here
            if state is not None or not playable:
                return None
            else:
                return True
        
        row = (pos[1] - self.y) // self.box_size
        col = (pos[0] - self.x) // self.box_size
        
        if row < 0 or row > 2 or col < 0 or col > 2:
            return None
        
        return row * 3 + col

    def make_playable(self):
        self.color = GREEN

    def make_unplayable(self, victory):
        self.color = WHITE
        if victory:
            change_text_victory('The winner is :')