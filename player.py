from box_game import BoxGame, get_next_move_random_best_strategy
from variables import Strategy, variables
from mcts_node import mcts_search
import random


class Player:
    """
    The class that represents a player that can play tic tac toe
    """
    def __init__(self, team, auto, strategy):
        self.team = team  # True = Circle, False = Cross 
        self.auto = auto  # True = make moves automatically, False = make moves manually
        self.strategy = strategy  # Strategy to use when auto is True

    def __str__(self):
        return f'Player(team = {self.team}, auto = {self.auto}, strategy = {self.strategy})'

    def choose_move(self, playable_boxes: list[BoxGame], first_move):        
            if self.strategy == Strategy.RANDOM:
                box_to_play = random.choice(playable_boxes)
            
            elif self.strategy == Strategy.RANDOM_BEST:
                box_to_play = get_next_move_random_best_strategy(self.team, playable_boxes)
            
            elif self.strategy == Strategy.MCTS:
                first_box = playable_boxes[0].get_first_box()  # The box that contains all the game
                
                if first_move: # Avoid too much useless computation
                    # Target: Main Box Index 1 (Middle Top), Sub Box Index 8 (Bottom Right) -> Found by playing game with high iteration number
                    main_box_index = 1
                    sub_box_index = 8
                    
                    box_to_play = first_box.childs[main_box_index].childs[sub_box_index]
                    variables.update_previous_mcts(path_played=box_to_play.get_path())
                    return box_to_play

                # Normal MCTS search for non-first moves
                box_to_play = mcts_search(
                    box_game_board=first_box, 
                    team=variables.get_current_team(), 
                    num_iterations=variables.mcts_iterations
                )
                return box_to_play
            
            else:
                print(f'The strategy : {self.strategy} has not been yet implemented, playing randomly')
                box_to_play = random.choice(playable_boxes)
            
            # We arrive here if the strategy is not MCTS 
            # (there can't be two mcts players in the same game)
            variables.update_previous_mcts(path_played=box_to_play.get_path())
            
            return box_to_play

    def get_team(self):
        """
        Used to get the team of the current player in variables.py
        """
        return self.team