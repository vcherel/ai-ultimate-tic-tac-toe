from box_game import BoxGame, find_same_box_in_other_board
from variables import variables
from tqdm import tqdm
import multiprocessing
import random
import math
import time


def _simulate_once(args):
    """Top-level for multiprocessing pickling. Runs one rollout and returns the score."""
    board, team_to_play, team_root = args
    winner = board.simulate(team_to_play)
    if winner == team_root:
        return 3
    elif winner is None:
        return 1
    else:
        return 0.0


class MCTSNode:
    def __init__(
        self,
        box_game_board: BoxGame,
        team_root,
        team_to_play,
        parent=None,
        previous_box_played: BoxGame = None,
    ):
        self.box_game_board: BoxGame = box_game_board
        self.team_root = team_root
        self.team_to_play = team_to_play

        self.id = (
            previous_box_played.get_path() if previous_box_played is not None else -1
        )

        self.visits = 0
        self.score = 0

        self.childs: list[MCTSNode] = []

        self.parent: MCTSNode = parent
        self.previous_box_played: BoxGame = previous_box_played

    def __str__(self, indent=0, depth=-1):
        """
        When the depth is at -1, it will print the whole tree
        """
        result = f"{' ' * indent}MCTSNode : id = {self.id}, visits = {self.visits}, score = {self.score}, uct_value = {self.uct_value():.6f}\n"
        if depth == 0:
            return result

        if depth == -1:
            depth = -1
        else:
            depth -= 1

        for child in self.childs:
            result += child.__str__(indent + 3, depth)
        return result

    def uct_value(self):
        if self.visits == 0:
            return float("inf")

        exploration = math.sqrt(math.log(self.parent.visits) / self.visits)
        return (
            self.score / self.visits
        ) + 1.4 * exploration  # 1.4 is the exploration constant

    def confidence_value(self):
        confidence = self.score / self.visits if self.visits != 0 else 0
        return confidence * 100 / 3  # score is in [0, 3]; normalize to [0, 100]


def mcts_search(box_game_board: BoxGame, team, time_budget):
    variables.set_simulating(True)

    num_workers = multiprocessing.cpu_count()

    box_game_board_copy = box_game_board.copy(no_draw=True)

    if variables.previous_mcts is not None:
        root = variables.previous_mcts
    else:
        root = MCTSNode(
            box_game_board=box_game_board_copy, team_root=team, team_to_play=team
        )

    pbar = tqdm(
        desc=f"MCTS Search ({num_workers} workers, {time_budget}s budget)",
        unit="sim",
        colour="green",
    )

    start_time = time.time()
    with multiprocessing.Pool(processes=num_workers) as pool:
        while time.time() - start_time < time_budget:
            node = select(root)
            node = expand(node)
            sim_args = [
                (node.box_game_board, node.team_to_play, node.team_root)
            ] * num_workers
            for score in pool.map(_simulate_once, sim_args):
                backpropagate(node, score)
            pbar.update(num_workers)

    elapsed = time.time() - start_time
    total_sims = pbar.n
    pbar.set_description(
        f"MCTS Search ({total_sims:,} simulations in {elapsed:.2f}s, {num_workers} workers)"
    )
    pbar.close()

    use_uct = len(root.box_game_board.get_all_playable_boxes()) > 3
    best_child: MCTSNode = select_best_direct_child(root, use_uct=use_uct)

    confidence = round(best_child.confidence_value(), 2)

    messages_by_threshold = [
        (
            99,
            [
                "Absolutely unstoppable!",
                "Resistance is futile.",
                "Already celebrating.",
                "You never stood a chance.",
                "GG, no re.",
            ],
        ),
        (
            95,
            [
                "You’re cooked!",
                "Pack it up.",
                "It’s over.",
                "Just give up already.",
                "Checkmate… wrong game, same result.",
            ],
        ),
        (
            90,
            [
                "Nothing can stop me now!",
                "The end is near — for you.",
                "I’m basically invincible.",
                "Dominance unlocked.",
                "This is my board now.",
            ],
        ),
        (
            85,
            [
                "I’ve got this in the bag.",
                "Sit back and watch.",
                "Looking very comfortable.",
                "Almost too easy.",
                "I see the finish line.",
            ],
        ),
        (
            80,
            [
                "Victory is near!",
                "I can smell the win.",
                "One foot in the winner’s circle.",
                "The momentum is all mine.",
                "Just a matter of time.",
            ],
        ),
        (
            75,
            [
                "On my way to win!",
                "Feeling strong out here.",
                "Things are looking up.",
                "I like where this is going.",
                "Slowly but surely.",
            ],
        ),
        (
            70,
            [
                "Feeling confident!",
                "I’ve got the edge.",
                "Good position, good vibes.",
                "I’ll take these odds.",
                "Cautiously optimistic.",
            ],
        ),
        (
            65,
            [
                "This should go well.",
                "Leaning in my favor.",
                "I’m ahead — let’s keep it that way.",
                "The stars are aligning.",
                "Looking decent from here.",
            ],
        ),
        (
            60,
            [
                "I think I can handle this.",
                "Slight advantage, I’ll take it.",
                "Not bad, not bad.",
                "Inch by inch.",
                "Better than a coin flip!",
            ],
        ),
        (
            55,
            [
                "Hmm… I think I can pull this off.",
                "It’s close, but I’ll manage.",
                "Every bit counts now.",
                "Grinding through it.",
                "Staying focused.",
            ],
        ),
        (
            50,
            [
                "It’s anyone’s game!",
                "Dead even — let’s see who blinks.",
                "Totally unpredictable.",
                "Flip a coin and pray.",
                "May the best AI win.",
            ],
        ),
        (
            45,
            [
                "This is tricky… fingers crossed!",
                "Tightrope walking here.",
                "One wrong move…",
                "Holding on by a thread.",
                "Please don’t blow this.",
            ],
        ),
        (
            40,
            [
                "I need to focus here.",
                "Time to dig deep.",
                "Uphill battle starting.",
                "Gotta earn it now.",
                "No more easy moves.",
            ],
        ),
        (
            35,
            [
                "Sweating bullets…",
                "Things are not great.",
                "Starting to feel the pressure.",
                "This is getting uncomfortable.",
                "Not ideal, not ideal.",
            ],
        ),
        (
            30,
            [
                "I’m nervous…",
                "Uh oh.",
                "I may have miscalculated.",
                "The walls are closing in.",
                "Someone help.",
            ],
        ),
        (
            25,
            [
                "I’m sweating here…",
                "It’s looking bleak.",
                "I’ve made a terrible mistake.",
                "Damage control mode activated.",
                "Can I take that back?",
            ],
        ),
        (
            20,
            [
                "This isn’t looking great…",
                "Falling apart at the seams.",
                "I need a miracle.",
                "Please make a mistake.",
                "Praying for blunders.",
            ],
        ),
        (
            15,
            [
                "I might be in trouble…",
                "Clinging to hope.",
                "Is this salvageable?",
                "Running out of options.",
                "Desperate times…",
            ],
        ),
        (
            10,
            [
                "Yikes… this could go badly.",
                "I don’t see a way out.",
                "The math is not mathing.",
                "Abandoning all hope.",
                "Send help.",
            ],
        ),
        (
            0,
            [
                "Absolutely doomed…",
                "Well, it was fun while it lasted.",
                "I accept my fate.",
                "RIP me.",
                "You win this round.",
            ],
        ),
    ]

    for threshold, candidates in messages_by_threshold:
        if confidence >= threshold:
            message = random.choice(candidates)
            break

    variables.confidence_message = f"{confidence}% {message}"
    if not variables.display_game:
        print(f"Confidence value: {confidence}% {message}")

    best_child.parent = None  # detach from tree so the subtree can be GC'd
    variables.previous_mcts = best_child  # reuse this subtree next turn

    variables.set_simulating(False)

    return find_same_box_in_other_board(
        best_child.previous_box_played, box_game_board, debug=True
    )


def select(node: MCTSNode):
    while node.childs and len(node.childs) == len(
        node.box_game_board.get_all_playable_boxes()
    ):
        node = max(node.childs, key=lambda child: child.uct_value())

    return node


def select_best_direct_child(node: MCTSNode, use_uct=True):
    if use_uct:
        max_score = max(child.uct_value() for child in node.childs)
        max_children = [
            child for child in node.childs if child.uct_value() == max_score
        ]
    else:
        max_score = max(
            (child.score / child.visits) if child.visits > 0 else 0
            for child in node.childs
        )
        max_children = [
            child
            for child in node.childs
            if (child.score / child.visits if child.visits > 0 else 0) == max_score
        ]

    return random.choice(max_children)


def expand(node: MCTSNode):
    possible_boxes_to_play = node.box_game_board.get_all_playable_boxes()

    if not possible_boxes_to_play:
        if variables.debug:
            print("No new nodes")
        return node

    existing_ids = {child.id for child in node.childs}
    unvisited = [b for b in possible_boxes_to_play if b.get_path() not in existing_ids]

    box_to_play = random.choice(unvisited)

    copy_box_game_board = node.box_game_board.copy(no_draw=True)
    box_to_play_copy = find_same_box_in_other_board(box_to_play, copy_box_game_board)
    # playable boxes must come from the copied board, not the original
    possible_boxes_to_play_copy = [
        find_same_box_in_other_board(b, copy_box_game_board)
        for b in possible_boxes_to_play
    ]
    box_to_play_copy.play(node.team_to_play, possible_boxes_to_play_copy)

    new_node = MCTSNode(
        box_game_board=copy_box_game_board,
        team_root=node.team_root,
        team_to_play=not node.team_to_play,
        parent=node,
        previous_box_played=box_to_play_copy,
    )
    node.childs.append(new_node)
    return new_node


def simulate(node: MCTSNode):
    winner_team_simulated = node.box_game_board.simulate(node.team_to_play)

    if winner_team_simulated == node.team_root:
        return 3
    elif winner_team_simulated is None:
        return 1
    else:
        return 0.0


def backpropagate(node: MCTSNode, score):
    while node is not None:
        node.visits += 1
        node.score += score
        node = node.parent
