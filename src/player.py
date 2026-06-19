from box_game import BoxGame, get_next_move_random_best_strategy
from variables import Strategy, variables
from mcts_node import mcts_search
import random


class Player:
    def __init__(self, team, auto, strategy):
        self.team = team  # True = circle, False = cross
        self.auto = auto
        self.strategy = strategy

    def __str__(self):
        return f"Player(team = {self.team}, auto = {self.auto}, strategy = {self.strategy})"

    def choose_move(self, playable_boxes: list[BoxGame], first_move):
        if self.strategy == Strategy.RANDOM:
            box_to_play = random.choice(playable_boxes)

        elif self.strategy == Strategy.RANDOM_BEST:
            box_to_play = get_next_move_random_best_strategy(self.team, playable_boxes)

        elif self.strategy == Strategy.MCTS:
            first_box = playable_boxes[
                0
            ].get_first_box()  # The box that contains all the game

            if first_move:  # skip costly MCTS on the opening move
                # Hardcoded opening: box 1 (middle-top), cell 8 (bottom-right)
                # determined by running MCTS at high iteration counts
                main_box_index = 1
                sub_box_index = 8

                box_to_play = first_box.childs[main_box_index].childs[sub_box_index]
                variables.update_previous_mcts(path_played=box_to_play.get_path())
                return box_to_play

            box_to_play = mcts_search(
                box_game_board=first_box,
                team=variables.get_current_team(),
                time_budget=variables.mcts_time,
            )
            return box_to_play

        else:
            print(
                f"The strategy : {self.strategy} has not been yet implemented, playing randomly"
            )
            box_to_play = random.choice(playable_boxes)

        # non-MCTS strategies: sync path so MCTS can reuse tree if it takes over next turn
        variables.update_previous_mcts(path_played=box_to_play.get_path())

        return box_to_play

    def get_team(self):
        return self.team
