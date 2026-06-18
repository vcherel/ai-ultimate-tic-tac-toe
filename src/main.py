from variables import variables, Strategy
import argparse
import time


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the game with configurable players and display options.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--nb_games", type=int, default=1, help="Number of games to simulate"
    )
    parser.add_argument(
        "--display_game",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Whether to display the game (True/False)",
    )
    parser.add_argument(
        "--size_board", type=int, default=100, help="Size of the game board"
    )
    parser.add_argument(
        "--player1_auto",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Is player 1 automatic?",
    )
    parser.add_argument(
        "--player1_strategy",
        type=str,
        default="random_best",
        help="Strategy for player 1",
    )
    parser.add_argument(
        "--player2_auto",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Is player 2 automatic?",
    )
    parser.add_argument(
        "--player2_strategy", type=str, default="mcts", help="Strategy for player 2"
    )
    parser.add_argument(
        "--mcts_iterations",
        type=int,
        default=80,
        help="Number of iterations per box done by MCTS algorithm",
    )
    parser.add_argument(
        "--save_results",
        type=str,
        default=None,
        help="Folder to save the game results (default to None)",
    )

    return parser.parse_args()


args = parse_args()

variables.nb_games = args.nb_games
variables.display_game = args.display_game
variables.size_board = args.size_board
variables.save_results = args.save_results
variables.mcts_iterations = args.mcts_iterations

variables.set_game_parameters(
    player1_auto=args.player1_auto,
    player1_strategy=Strategy(args.player1_strategy),
    player2_auto=args.player2_auto,
    player2_strategy=Strategy(args.player2_strategy),
)

if not variables.display_game and (
    not variables.player1_auto or not variables.player2_auto
):
    print("Warning: At least one player is manual. Enabling display.")
    variables.display_game = True

from player import Player  # noqa: E402
from game import game  # noqa: E402

if variables.display_game:
    import pygame

    KEY_SPACE = pygame.K_SPACE


def start_one_game():
    variables.previous_mcts = None
    if variables.nb_games > 0:
        print(
            f"~~ Game number {original_nb_games - variables.nb_games + 1} / {original_nb_games} ~~"
        )

    game.start()

    running = True
    while running:
        actual_player: Player = variables.actual_player

        if actual_player.auto:
            game.play()

        if variables.display_game:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if actual_player.auto:
                        continue

                    pos = pygame.mouse.get_pos()
                    game.play(pos)

                if event.type == pygame.KEYDOWN:
                    if pygame.key.name(event.key) == "up":
                        game.play()

                if event.type == pygame.QUIT:
                    exit_game()

            if pygame.key.get_pressed()[KEY_SPACE] and not actual_player.auto:
                game.play()

            pygame.display.flip()

        if variables.finished:
            variables.add_to_list_result(variables.winner)
            variables.decrease_nb_games()
            running = False

        if variables.display_game:
            clock.tick(60)


def exit_game(quit_all=True):
    if variables.save_results:
        analyze_results()
    if variables.display_game:
        if not quit_all:
            # Keep window open so the user can see the final board state
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
        else:
            pygame.quit()
    exit()


def analyze_results():
    nb_games = len(variables.list_result)
    nb_draw = variables.list_result.count(None)
    nb_circles = variables.list_result.count(True)
    nb_crosses = variables.list_result.count(False)

    percentage_draw = (nb_draw / nb_games) * 100 if nb_games != 0 else 0
    percentage_circles = (nb_circles / nb_games) * 100 if nb_games != 0 else 0
    percentage_crosses = (nb_crosses / nb_games) * 100 if nb_games != 0 else 0

    with open(variables.save_results, "a") as file:
        file.write(f"Number of games: {nb_games}\n")
        file.write(f"Time of execution: {time.time() - time_begin:.2f} seconds\n\n")
        if variables.player1_auto:
            file.write(
                f"Player 1 : Automatic, strategy = {variables.player1_strategy.value}\n"
            )
        else:
            file.write("Player 1 : Manual\n")
        if variables.player2_auto:
            file.write(
                f"Player 2 : Automatic, strategy = {variables.player2_strategy.value}\n"
            )
        else:
            file.write("Player 2 : Manual\n")
        file.write(f"Number of draws: {nb_draw} ({percentage_draw:.2f}% of the game)\n")
        file.write(
            f"Number of player 1 wins: {nb_circles} ({percentage_circles:.2f}%)\n"
        )
        file.write(
            f"Number of player 2 wins: {nb_crosses} ({percentage_crosses:.2f}%)\n\n"
        )
        file.write("******************************************************\n\n")


time_begin = time.time()
original_nb_games = variables.nb_games

if variables.display_game:
    clock = pygame.time.Clock()

start_one_game()

if variables.nb_games == 0:
    exit_game(quit_all=False)

running = True
while running:
    if variables.nb_games == 1:
        running = False

    if variables.display_game and (
        not variables.player1_auto or not variables.player2_auto
    ):
        wait_for_next_game = True
        print("Click to start the next game")
        while wait_for_next_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    wait_for_next_game = False

    start_one_game()

exit_game(quit_all=False)
