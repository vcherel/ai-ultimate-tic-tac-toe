from text import change_text_victory
from draw import draw_actual_player
from variables import variables
from player import Player
from board import board
import random


class Game:
    """
    The game define who is playing and when the game is finished
    """
    def __init__(self):
        player1 = Player(team=True, auto=variables.player1_auto, strategy=variables.player1_strategy)
        player2 = Player(team=False, auto=variables.player2_auto, strategy=variables.player2_strategy)
        self.players = [player1, player2]
        self.first_move = True

    def start(self):
        """
        Called at the beginning of the game
        """
        self.first_move = True
        board.init()
        variables.set_winner(None)
        variables.set_finished(False)
        variables.actual_player = random.choice(self.players)
        
        if variables.display_game:
            change_text_victory('This is the turn of : ')
            board.draw()
            draw_actual_player(variables.get_current_team())

    def play(self, pos=None):
        """
        Pos is the position of the click (if it is not None, it means that the player 
        is not automatic and that he clicked on the screen)
        """
        playable_boxes = board.get_all_playable_boxes()
        
        # If there is no playable box left, the game is a draw
        if playable_boxes == []:
            variables.set_finished(True)
            if variables.display_game:
                change_text_victory('The game is a draw')
                draw_actual_player(variables.get_current_team(), erase=True)
            return
        
        if pos is not None:
            # Play by clicking on the screen
            if not board.try_click(pos):
                return  # If we clicked outside a playable box we don't want to change player
        else:
            # Play automatically
            actual_player: Player = variables.actual_player
            box_to_play = actual_player.choose_move(playable_boxes, self.first_move)
            
            if box_to_play not in playable_boxes:
                raise ValueError(f'Error: The chosen box to play is not in the list of playable boxes')
            else:
                box_to_play.play(actual_player.team, playable_boxes)
        
        # If the game continues
        if not variables.finished:
            self.change_player()
            if variables.display_game:
                board.draw()

    def change_player(self):
        """
        Called when a player has played
        """
        self.first_move = False
        current_team = variables.get_current_team()
        
        # Update the actual player
        variables.actual_player = self.players[1] if current_team else self.players[0]
        
        if variables.display_game:
            # Erase the actual player (the one who just played)
            draw_actual_player(current_team, erase=True)
            # Draw the new actual player
            draw_actual_player(not current_team)


game = Game()