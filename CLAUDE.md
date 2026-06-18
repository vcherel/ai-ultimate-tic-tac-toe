# Ultimate Tic-Tac-Toe AI

AI agent that plays Ultimate Tic-Tac-Toe using Monte Carlo Tree Search (MCTS), built with pygame. Game state is a recursive `BoxGame` tree of depth 2 (9×9 board of boards).

## How to run

```bash
uv sync
uv run python src/main.py
```

Common flags: `--player1_auto True`, `--player2_strategy mcts`, `--mcts_iterations 200`

## Key files

- `src/main.py` — entry point; parses CLI args, drives game loop and pygame events
- `src/game.py` — `Game` class; controls turn order and game flow
- `src/box_game.py` — `BoxGame`; core game logic for any node in the nested board tree; also holds MCTS helper functions (`find_same_box_in_other_board`, `get_next_move_random_best_strategy`)
- `src/mcts_node.py` — MCTS implementation: `MCTSNode` and `mcts_search`
- `src/player.py` — `Player`; delegates move choice to the configured strategy
- `src/variables.py` — `Variables` singleton shared across all modules; `Strategy` enum; color constants
- `src/board.py` — `Board`; wraps the root `BoxGame` and pygame window
- `src/draw.py` / `src/box_draw.py` — pygame drawing helpers
- `src/text.py` — victory text overlay

## Conventions

- `team=True` → circle (player 1), `team=False` → cross (player 2)
- Board depth is decreasing: `depth=2` is the root, `depth=0` are leaf cells
- MCTS reuses its tree across turns via `variables.previous_mcts`
