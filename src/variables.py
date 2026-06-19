from enum import Enum


class Strategy(Enum):
    RANDOM = "random"
    RANDOM_BEST = "random_best"
    MCTS = "mcts"


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (175, 250, 175)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Variables:
    def __init__(self):
        self.nb_games = None
        self.display_game = None
        self.size_board = None
        self.player1_auto = None
        self.player1_strategy = None
        self.player2_auto = None
        self.player2_strategy = None
        self.save_results = None
        self.mcts_time = None

        self.screen_size = None
        self.screen = None
        self.text_victory = None  # tuple (text, textRect)
        self.finished = None
        self.winner = None  # True: circle won, False: cross won
        self.actual_player = None
        self.list_result = []
        self.simulating = False
        self.previous_mcts = None
        self.debug = False

    def set_game_parameters(
        self, player1_auto, player1_strategy, player2_auto, player2_strategy
    ):
        self.player1_auto = player1_auto
        self.player1_strategy = player1_strategy
        self.player2_auto = player2_auto
        self.player2_strategy = player2_strategy

        if (
            self.player1_auto
            and self.player2_auto
            and self.player1_strategy == Strategy.MCTS
            and self.player2_strategy == Strategy.MCTS
        ):
            print("Error: Both players cannot have the strategy MCTS")
            exit()

    def get_current_team(self):
        return self.actual_player.get_team()

    def set_simulating(self, simulating):
        self.simulating = simulating

    def set_finished(self, finished):
        if self.simulating:
            return
        else:
            self.finished = finished

    def set_winner(self, winner):
        if self.simulating:
            return
        else:
            self.winner = winner

    def set_screen(self, screen):
        self.screen = screen

    def set_screen_size(self, screen_size):
        self.screen_size = screen_size

    def set_text_victory(self, text, textRect):
        self.text_victory = (text, textRect)

    def add_to_list_result(self, result):
        self.list_result.append(result)

    def decrease_nb_games(self):
        self.nb_games -= 1

    def update_previous_mcts(self, path_played):
        if self.previous_mcts is not None:
            for child in self.previous_mcts.childs:
                if child.previous_box_played.get_path() == path_played:
                    self.previous_mcts = child
                    return
            self.previous_mcts = None
            return


variables = Variables()
