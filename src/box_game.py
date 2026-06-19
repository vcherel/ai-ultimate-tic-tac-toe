from variables import variables
from box_draw import BoxDraw
import random


class BoxGame:
    """
    A box that only contains the game logic
    """

    def __init__(
        self,
        depth,
        id_box,
        parent,
        draw=False,
        x=None,
        y=None,
        width=None,
        width_line=None,
        debug=False,
    ):
        """
        draw: if True, x/y/width/width_line are required for pygame rendering
        debug: skip creating children (used for isolated test boxes)
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
        self.depth = depth  # decreasing: depth=2 is root, depth=0 are leaf cells
        if self.depth > 0 and not debug:
            if not draw:
                for i in range(9):
                    self.childs.append(BoxGame(depth - 1, i, self))

            else:
                width_line = int(width_line // 2)
                cell = width // 3
                for i in range(9):
                    self.childs.append(
                        BoxGame(
                            depth - 1,
                            i,
                            self,
                            draw=True,
                            x=x + (i % 3) * cell,
                            y=y + (i // 3) * cell,
                            width=cell,
                            width_line=width_line,
                        )
                    )

        if self.depth == 0:
            self.make_playable()

    def __str__(self, indent=0):
        result = f"{' ' * indent}BoxGame(depth = {self.depth}, id = {self.id_box}, state = {self.state}, playable = {self.playable}, uid = {id(self)})\n"
        for child in self.childs:
            result += child.__str__(indent + 3)
        return result

    def __eq__(self, other):
        if not isinstance(other, BoxGame):
            return False

        return (
            self.state == other.state
            and self.playable == other.playable
            and len(self.childs) == len(other.childs)
            and all(
                child1 == child2 for child1, child2 in zip(self.childs, other.childs)
            )
        )

    def copy(self, parent=None, no_draw=False):
        if self.box_draw is not None and not no_draw:
            new_box = BoxGame(
                self.depth,
                self.id_box,
                parent,
                draw=True,
                x=self.box_draw.x,
                y=self.box_draw.y,
                width=self.box_draw.width,
                width_line=self.box_draw.width_line,
            )
        else:
            new_box = BoxGame(self.depth, self.id_box, parent, draw=False)

        new_box.state = self.state
        new_box.playable = self.playable

        new_box.childs = (
            [child.copy(parent=new_box, no_draw=no_draw) for child in self.childs]
            if self.depth > 0
            else []
        )

        return new_box

    def draw(self):
        self.box_draw.draw(self.childs == [], self.parent is None, self.state)

    def draw_all(self):
        if variables.display_game:
            for child in self.childs:
                child.draw_all()

            self.draw()  # redraw self after children so border lines aren't overwritten

    def search_click(self, pos, playable_boxes):
        result_search = self.box_draw.search_click(
            self.childs == [], self.state, self.playable, pos
        )

        if result_search is None:
            return None

        if result_search is True:
            self.play(variables.get_current_team(), playable_boxes)
            variables.update_previous_mcts(path_played=self.get_path())
            return True

        box_clicked: BoxDraw = self.childs[result_search]
        return box_clicked.search_click(pos, playable_boxes)

    def make_playable(self):
        """Returns False if the box already has a state (used by make_childs_playable to detect full boards)"""
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
        """Falls back to making the entire board playable if all children are already won."""
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
        self.state = current_team

        if self.parent is not None and self.parent.detect_victory():
            self.parent.victory(self.state)

        first_box = self.get_first_box()

        if first_box.childs == []:
            return

        for playable_box in playable_boxes:
            playable_box.make_unplayable()

        next_box_to_play: BoxGame = first_box.childs[self.id_box]

        next_box_to_play.make_childs_playable()

        return

    def detect_victory(self):
        for i in range(3):
            if all(
                self.childs[i * 3 + j].state == self.childs[i * 3].state
                and self.childs[i * 3 + j].state is not None
                for j in range(1, 3)
            ):
                return True

            if all(
                self.childs[i + j * 3].state == self.childs[i].state
                and self.childs[i + j * 3].state is not None
                for j in range(1, 3)
            ):
                return True

        if all(
            self.childs[i * 4].state == self.childs[0].state
            and self.childs[i * 4].state is not None
            for i in range(1, 3)
        ):
            return True

        if all(
            self.childs[i * 2 + 2].state == self.childs[2].state
            and self.childs[i * 2 + 2].state is not None
            for i in range(1, 3)
        ):
            return True

        return False

    def victory(self, current_team):
        self.childs = []
        self.state = current_team

        self.make_unplayable(victory=self.parent is None)

        if self.parent is None:
            variables.set_finished(True)
            variables.set_winner(self.state)

        # a single move can trigger cascading wins up multiple board levels
        elif self.parent.detect_victory():
            self.parent.victory(current_team)

    def get_all_playable_boxes(self):
        if self.childs == []:
            return [self] if self.playable else []

        playable_boxes = []
        for child in self.childs:
            playable_boxes += child.get_all_playable_boxes()

        return playable_boxes

    def simulate(self, next_team_to_play):
        box_game_copy = self.copy()  # don't mutate the real board

        while True:
            # childs == [] on the root means the board itself has been won
            if box_game_copy.childs == [] or box_game_copy.detect_victory():
                return not next_team_to_play

            playable_boxes = box_game_copy.get_all_playable_boxes()

            if playable_boxes == []:
                return None

            box_to_play = get_next_move_random_best_strategy(
                next_team_to_play, playable_boxes
            )
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

        return " ".join(map(str, reversed(path)))


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
    playing_on_same_board = are_all_boxes_in_same_board(playable_boxes)
    if not playing_on_same_board:
        box_to_play: BoxGame = random.choice(playable_boxes).parent
    else:
        box_to_play: BoxGame = playable_boxes[0].parent
    boxes = box_to_play.childs
    states = [box.state for box in boxes]

    winning_combinations = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],  # rows
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],  # columns
        [0, 4, 8],
        [2, 4, 6],  # diagonals
    ]

    # win if possible
    for combination in winning_combinations:
        if (
            states[combination[0]] == team
            and states[combination[1]] == team
            and states[combination[2]] is None
        ):
            return boxes[combination[2]]
        if (
            states[combination[0]] == team
            and states[combination[1]] is None
            and states[combination[2]] == team
        ):
            return boxes[combination[1]]
        if (
            states[combination[0]] is None
            and states[combination[1]] == team
            and states[combination[2]] == team
        ):
            return boxes[combination[0]]

    # block opponent's winning move
    for combination in winning_combinations:
        if (
            states[combination[0]] == (not team)
            and states[combination[1]] == (not team)
            and states[combination[2]] is None
        ):
            return boxes[combination[2]]
        if (
            states[combination[0]] == (not team)
            and states[combination[1]] is None
            and states[combination[2]] == (not team)
        ):
            return boxes[combination[1]]
        if (
            states[combination[0]] is None
            and states[combination[1]] == (not team)
            and states[combination[2]] == (not team)
        ):
            return boxes[combination[0]]

    return random.choice(playable_boxes)


def are_all_boxes_in_same_board(boxes: list[BoxGame]) -> bool:
    if len(boxes) > 9:
        return False

    id_parent = boxes[0].parent.id_box

    for box in boxes:
        if box.parent.id_box != id_parent:
            return False
    return True
