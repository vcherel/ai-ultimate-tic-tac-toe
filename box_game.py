from variables import variables
from box_draw import BoxDraw
import random


class BoxGame:
    """
    A box that only contains the game logic
    """
    def __init__(self, depth, id_box, parent, draw=False, x=None, y=None, width=None, width_line=None, debug=False):
        """
        draw is a boolean that indicates if the box is going to be drawn at some point or not, if so, all the other parameters will be used
        debug : if we create a box for debug purposes, we don't want to create the childs
        """
        self.state = None
        self.playable = False
        self.id_box = id_box

        self.parent: BoxGame = parent

        if draw:
            self.box_draw = BoxDraw(x, y, width, width_line)
        else:
            self.box_draw = None

        self.childs: list[BoxGame] = []
        self.depth = depth  # Depth is in decreasing order (lower number = deeper)
        if self.depth > 0 and not debug:
            if not draw:
                for i in range(9):
                    self.childs.append(BoxGame(depth - 1, i, self))

            else:
                width_line = int(width_line // 2)
                self.childs.append(BoxGame(depth - 1, 0, self, draw=True, x=x, y=y, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 1, self, draw=True, x=x + width // 3, y=y, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 2, self, draw=True, x=x + 2 * width // 3, y=y, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 3, self, draw=True, x=x, y=y + width // 3, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 4, self, draw=True, x=x + width // 3, y=y + width // 3, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 5, self, draw=True, x=x + 2 * width // 3, y=y + width // 3, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 6, self, draw=True, x=x, y=y + 2 * width // 3, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 7, self, draw=True, x=x + width // 3, y=y + 2 * width // 3, width=width // 3, width_line=width_line))
                self.childs.append(BoxGame(depth - 1, 8, self, draw=True, x=x + 2 * width // 3, y=y + 2 * width // 3, width=width // 3, width_line=width_line))

        if self.depth == 0:
            self.make_playable()

        
    def __str__(self, indent=0):
        result = f'{" " * indent}BoxGame(depth = {self.depth}, id = {self.id_box}, state = {self.state}, playable = {self.playable}, uid = {id(self)})\n'
        for child in self.childs:
            result += child.__str__(indent + 3)
        return result
    

    def __eq__(self, other):
        if not isinstance(other, BoxGame):
            return False

        return (
            self.state == other.state and
            self.playable == other.playable and
            len(self.childs) == len(other.childs) and
            all(child1 == child2 for child1, child2 in zip(self.childs, other.childs))
        )
    

    def copy(self, parent=None):
        if self.box_draw is not None:
            new_box = BoxGame(self.depth, self.id_box, parent, draw=True, x=self.box_draw.x, y=self.box_draw.y, width=self.box_draw.width, width_line=self.box_draw.width_line)
        else:
            new_box = BoxGame(self.depth, self.id_box, parent, draw=False)
    
        new_box.state = self.state
        new_box.playable = self.playable

        # If the box is a leaf, we don't have to copy the children
        new_box.childs = [child.copy(parent=new_box) for child in self.childs] if self.depth > 0 else []

        return new_box


    def draw(self):
        """
        We will arrive in this function only if the box can be drawn
        """
        self.box_draw.draw(self.childs == [], self.parent is None, self.state)


    def draw_all(self):
        """
        We will arrive in this function only if the box can be drawn
        """
        if variables.display_game:        
            for child in self.childs:
                child.draw_all()

            self.draw()  # If we don't redraw here the lines around the box will disappear


    def search_click(self, pos, playable_boxes):
        """
        We will arrive in this function only if the box can be drawn
        """
        result_search = self.box_draw.search_click(self.childs == [], self.state, self.playable, pos)

        # We could'nt click the box
        if result_search is None:
            return None
        
        # If the box has been clicked
        if result_search is True:
            self.play(variables.get_current_team(), playable_boxes)
            variables.update_previous_mcts(path_played=self.get_path())
            return True
        
        # If we hava to go deeper in the box
        box_clicked: BoxDraw = self.childs[result_search]
        return box_clicked.search_click(pos, playable_boxes)
    

    def make_playable(self):
        """
        Returns True if the box has been made playable
        We do this because of the make_childs_playable()
        """
        if self.state is not None:
            return False
        
        self.playable = True
        if self.box_draw:
            self.box_draw.make_playable()
        return True


    def make_all_playable(self):
        if self.childs == []:
            self.make_playable()

        for child in self.childs:
            child.make_all_playable()


    def make_childs_playable(self):
        """
        Make all the direct childs of the box playable
        If it was impossible, we make all the box playable
        """
        no_child_playable = True
        for child in self.childs:
            if child.make_playable():
                no_child_playable = False
        
        if no_child_playable:
            self.get_first_box().make_all_playable()


    def get_first_box(self):
        first_box = self
        while first_box.parent is not None:
            first_box = first_box.parent
        return first_box


    def make_unplayable(self, victory=False):
        self.playable = False
        if self.box_draw is not None:
            self.box_draw.make_unplayable(victory)


    def make_all_unplayable(self):
        self.make_unplayable()
        
        for child in self.childs:
            child.make_all_unplayable()

    
    def play(self, current_team, playable_boxes):
        """
        When the current box is played
        Sometimes we have to play a specific box (when doing simulations for example)
        """
        self.state = current_team

        if self.parent is not None and self.parent.detect_victory():
            self.parent.victory(self.state)

        # Find the next box in which the player can play
        first_box = self.get_first_box()

        if first_box.childs == []:
            return

        for playable_box in playable_boxes:
            playable_box.make_unplayable()

        next_box_to_play: BoxGame = first_box.childs[self.id_box]

        next_box_to_play.make_childs_playable()

        return


    def detect_victory(self):
        """
        Returns True if the box has been won
        """
        for i in range(3):
            # Check rows
            if all(self.childs[i * 3 + j].state == self.childs[i * 3].state and self.childs[i * 3 + j].state is not None for j in range(1, 3)):
                return True

            # Check columns
            if all(self.childs[i + j * 3].state == self.childs[i].state and self.childs[i + j * 3].state is not None for j in range(1, 3)):
                return True

        # Check diagonals
        if all(self.childs[i * 4].state == self.childs[0].state and self.childs[i * 4].state is not None for i in range(1, 3)):
            return True

        if all(self.childs[i * 2 + 2].state == self.childs[2].state and self.childs[i * 2 + 2].state is not None for i in range(1, 3)):
            return True

        return False


    def victory(self, current_team):
        """
        Function called when the box is won by a player
        """
        self.childs = []
        self.state = current_team

        self.make_unplayable(victory=self.parent is None)

        if self.parent is None:
            # The game has been won
            variables.set_finished(True)
            variables.set_winner(self.state)

        # Maybe there is multiple wins at the same time
        elif self.parent.detect_victory():
            self.parent.victory(current_team)


    def get_all_playable_boxes(self):
        """
        Returns a list of all the boxes that are playable
        """
        if self.childs == []:
            return [self] if self.playable else []

        playable_boxes = []
        for child in self.childs:
            playable_boxes += child.get_all_playable_boxes()

        return playable_boxes
    

    def simulate(self, next_team_to_play):
        """
        Simulate a game from the current state and return the result
        """
        box_game_copy = self.copy()  # We don't want to modify the original game

        while True:
            # box_game_copy.childs == [] means that the game has been won (the main box has been won)
            if box_game_copy.childs == [] or box_game_copy.detect_victory():
                return not next_team_to_play
        
            playable_boxes = box_game_copy.get_all_playable_boxes()

            if playable_boxes == []:
                return None
            
            box_to_play = get_next_move_random_best_strategy(next_team_to_play, playable_boxes)
            box_to_play.play(next_team_to_play, playable_boxes)

            next_team_to_play = not next_team_to_play


    def get_path(self):
        path = []

        box = self
        finished = False
        while not finished:
            path.append(box.id_box)
            box = box.parent
            if box is None:
                finished = True

        return ' '.join(map(str, reversed(path)))

    
def find_same_box_in_other_board(box_bottom: BoxGame, box_board: BoxGame, debug=False):
    ids_to_play = []
    while box_bottom.parent:
        ids_to_play.append(box_bottom.id_box)
        box_bottom = box_bottom.parent

    same_box = box_board
    for id_to_play in reversed(ids_to_play):
        same_box = same_box.childs[id_to_play]

    return same_box


def get_next_move_random_best_strategy(team, playable_boxes: list[BoxGame]) -> BoxGame:
    playing_on_same_board = True
    # Detect if all playable_boxes are in the same board
    playing_on_same_board = are_all_boxes_in_same_board(playable_boxes)
    # We search the board that we will first want to complete
    if not playing_on_same_board:
        box_to_play: BoxGame = random.choice(playable_boxes).parent
    else:
        box_to_play: BoxGame = playable_boxes[0].parent
    boxes = box_to_play.childs
    # Count the number of box taken by the actual player or by the other
    states = []
    for box in boxes:
        states.append(box.state)
        
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
        
    # If we can win in one turn, we do it
    for combination in winning_combinations:
        if states[combination[0]] == team and states[combination[1]] == team and states[combination[2]] == None:
            return boxes[combination[2]]
        if states[combination[0]] == team and states[combination[1]] == None and states[combination[2]] == team:
            return boxes[combination[1]]
        if states[combination[0]] == None and states[combination[1]] == team and states[combination[2]] == team:
            return boxes[combination[0]]
        
    # If the other can win in one turn, we block him
    for combination in winning_combinations:
        if states[combination[0]] == (not team) and states[combination[1]] == (not team) and states[combination[2]] == None:
            return boxes[combination[2]]
        if states[combination[0]] == (not team) and states[combination[1]] == None and states[combination[2]] == (not team):
            return boxes[combination[1]]
        if states[combination[0]] == None and states[combination[1]] == (not team) and states[combination[2]] == (not team):
            return boxes[combination[0]]
    
    # Else we play randomly
    return random.choice(playable_boxes)


def are_all_boxes_in_same_board(boxes: list[BoxGame]) -> bool:
    """
    Detect if all playable_boxes are in the same board
    """
    if len(boxes) > 9:
            return False
    
    id_parent = boxes[0].parent.id_box
    
    for box in boxes:
        if box.parent.id_box != id_parent:
            return False
    return True