from variables import variables, Strategy
import sys
import time


# Parse command line arguments
if len(sys.argv) != 9:
    print('Usage: python3 main.py <depth> <nb_games> <display_game> <size_board> <player1_auto> <player1_strategy> <player2_auto> <player2_strategy>')
    print('Example: python3 main.py 2 1 True 100 True mcts False random_best')
    sys.exit(1)

# Set basic game parameters
variables.depth_board = int(sys.argv[1])
if variables.depth_board not in [2, 3]:
    raise SystemExit(f'Depth must be 2 or 3')

variables.nb_games = int(sys.argv[2])
variables.display_game = sys.argv[3].lower() == 'true'

# Set additional parameters
size_board = int(sys.argv[4])
player1_auto = sys.argv[5].lower() == 'true'
player1_strategy = Strategy(sys.argv[6])
player2_auto = sys.argv[7].lower() == 'true'
player2_strategy = Strategy(sys.argv[8])

# Apply parameters
variables.set_parameters(size_board, player1_auto, player1_strategy, player2_auto, player2_strategy)

# Check if we need to force display
if not variables.display_game and (not variables.player1_auto or not variables.player2_auto):
    print('Error: You must display the game if at least one player is not automatic\nTurning display on...')
    variables.display_game = True


from player import Player
from game import game

if variables.display_game:
    import pygame
    KEY_SPACE = pygame.K_SPACE


def start_one_game():
    variables.previous_mcts = None
    if variables.nb_games > 0:
        print(f'~~ Game number {original_nb_games - variables.nb_games + 1} / {original_nb_games} ~~')

    game.start()

    # Main loop
    running = True
    while running:
        actual_player: Player = variables.actual_player

        # If the player is automatic and not finished we play
        if actual_player.auto:
            game.play()
    
        if variables.display_game:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # We don't want to play if the game is finished or if the player is automatic
                    if actual_player.auto:
                        continue

                    # Detect if a box has been clicked
                    pos = pygame.mouse.get_pos()
                    game.play(pos)

                if event.type == pygame.KEYDOWN:
                    if pygame.key.name(event.key) == 'up':
                        game.play()

                if event.type == pygame.QUIT:
                    exit_game()

            # If player is manual and space is pressed, we play automatically random moves
            if pygame.key.get_pressed()[KEY_SPACE] and not actual_player.auto:
                game.play()

            pygame.display.flip()

        if variables.finished:
            variables.add_to_list_result(variables.winner)
            variables.decrease_nb_games()
            running = False

        # Limit the frame rate
        if variables.display_game:
            clock.tick(60)


def exit_game(quit_all=True):
    """
    quit_all = We leave the game window
    """
    analyze_results()
    if variables.display_game:
        if not quit_all:
            # Sometimes we finished the game but we still want to see the result
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

    # Calculate percentages
    percentage_draw = (nb_draw / nb_games) * 100 if nb_games != 0 else 0
    percentage_circles = (nb_circles / nb_games) * 100 if nb_games != 0 else 0
    percentage_crosses = (nb_crosses / nb_games) * 100 if nb_games != 0 else 0

    with open('results.txt', 'a') as file:
        file.write(f'Number of games: {nb_games}\n')
        file.write(f'Time of execution: {time.time() - time_begin:.2f} seconds\n\n')
        if variables.player1_auto:
            file.write(f'Player 1 : Automatic, strategy = {variables.player1_strategy.value}\n')
        else:
            file.write(f'Player 1 : Manual\n')
        if variables.player2_auto:
            file.write(f'Player 2 : Automatic, strategy = {variables.player2_strategy.value}\n')
        else:
            file.write(f'Player 2 : Manual\n')
        file.write(f'Number of draws: {nb_draw} ({percentage_draw:.2f}% of the game)\n')
        file.write(f'Number of player 1 wins: {nb_circles} ({percentage_circles:.2f}%)\n')
        file.write(f'Number of player 2 wins: {nb_crosses} ({percentage_crosses:.2f}%)\n\n')
        file.write(f'******************************************************\n\n')


time_begin = time.time()
original_nb_games = variables.nb_games

if variables.display_game:
    clock = pygame.time.Clock()  # Creates a clock object to control FPS

start_one_game()  # The game starts at the beginning

if variables.nb_games == 0:
    exit_game(quit_all=False)

running = True
while running:
    if variables.nb_games == 1:
        running = False

    if variables.display_game and (not variables.player1_auto or not variables.player2_auto):
        wait_for_next_game = True
        print('Click to start the next game')
        while wait_for_next_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    wait_for_next_game = False

    start_one_game()

exit_game(quit_all=False)