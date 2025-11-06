from box_game import BoxGame, find_same_box_in_other_board
from variables import variables
from tqdm import tqdm
import random
import math


class MCTSNode:
    def __init__(self, box_game_board: BoxGame, team_root, team_to_play, parent=None, previous_box_played: BoxGame=None):
        self.box_game_board: BoxGame = box_game_board
        self.team_root = team_root  # The team for which we want to maximize the score
        self.team_to_play = team_to_play  # The team that is playing at this node (playing in the expand part of the algorithm)

        self.id = previous_box_played.get_path() if previous_box_played is not None else -1
         
        self.visits = 0  # How many time this node has been visited
        self.score = 0  # Cumulated score of this node

        self.childs: list[MCTSNode] = []  # List of child nodes

        self.parent: MCTSNode = parent  # Parent node
        self.previous_box_played: BoxGame = previous_box_played  # The box that was played to get to this node


    def __str__(self, indent=0, depth=-1):
        """
        When the depth is at -1, it will print the whole tree
        """
        result = f'{" " * indent}MCTSNode : id = {self.id}, visits = {self.visits}, score = {self.score}, uct_value = {self.uct_value():.6f}\n'
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
            return float('inf')
        
        # Try different exploration constants
        exploration = math.sqrt(math.log(self.parent.visits) / self.visits)
        return (self.score / self.visits) + 1.4 * exploration  # Adjust 1.4 as needed
    
    def confidence_value(self):
        """
        Return the confidence value of this node
        """
        confidence = self.score / self.visits if self.visits != 0 else 0
        return confidence * 100 / 3 # We want the confidence to be between 0 and 100


def mcts_search(box_game_board: BoxGame, team, num_iterations):
    """
    Perform a MCTS search from a given state of the board and the team that is playing and return the best box to play
    num_iterations is the number of iterations to perform per box
    """
    variables.set_simulating(True)  # To indicates that if a game finish here it does not means the real game is finished

    box_game_board_copy = box_game_board.copy()
    box_game_board_copy.box_draw = None  # We don't need to draw the board for the MCTS search

    if variables.previous_mcts is not None:
        root = variables.previous_mcts
    else:
        root = MCTSNode(box_game_board=box_game_board_copy, team_root=team, team_to_play=team)
    
    num_iterations = num_iterations * len(root.box_game_board.get_all_playable_boxes())
    
    # Create tqdm progress bar with description and total iterations
    pbar = tqdm(
        desc=f'MCTS Search ({num_iterations:,} iterations)',
        total=num_iterations,
        unit='iterations',
        colour='green'
    )
    
    for _ in range(num_iterations):
        node = select(root)
        nodes_to_simulate = expand(node)
        for node_to_simulate in nodes_to_simulate:
            score = simulate(node_to_simulate)
            backpropagate(node_to_simulate, score)
        pbar.update(1)  # Update progress bar
        
    pbar.close()  # Close the progress bar
    
    # Choose the best move based on the UCT value if there are more than 3 boxes left
    use_uct = True
    if len(root.box_game_board.get_all_playable_boxes()) <= 3:
        use_uct = False
    best_child: MCTSNode = select_best_direct_child(root, use_uct=use_uct)

    confidence = round(best_child.confidence_value(), 2)

    if confidence >= 99:
        message = "Absolutely unstoppable!"
    elif confidence >= 95:
        message = "You're cooked!"
    elif confidence >= 90:
        message = "Nothing can stop me now!"
    elif confidence >= 85:
        message = "I’ve got this in the bag."
    elif confidence >= 80:
        message = "Victory is near!"
    elif confidence >= 75:
        message = "On my way to win!"
    elif confidence >= 70:
        message = "Feeling confident!"
    elif confidence >= 65:
        message = "This should go well."
    elif confidence >= 60:
        message = "I think I can handle this."
    elif confidence >= 55:
        message = "Hmm… I think I can pull this off."
    elif confidence >= 50:
        message = "It’s anyone’s game!"
    elif confidence >= 45:
        message = "This is tricky… fingers crossed!"
    elif confidence >= 40:
        message = "I need to focus here."
    elif confidence >= 35:
        message = "Sweating bullets…"
    elif confidence >= 30:
        message = "I’m nervous…"
    elif confidence >= 25:
        message = "I’m sweating here…"
    elif confidence >= 20:
        message = "This isn’t looking great…"
    elif confidence >= 15:
        message = "I might be in trouble…"
    elif confidence >= 10:
        message = "Yikes… this could go badly."
    else:
        message = "Absolutely doomed…"

    print(f"Confidence value: {confidence}% — {message}")


    # print(f'MCTS node at the end : {root.__str__(depth=2)}')
    # print(f'Chosen move : {best_child.previous_box_played.get_path()}\n')

    # We save the best child to be able to use it in the next iteration
    best_child.parent = None  # We don't need the parent anymore
    variables.previous_mcts = best_child

    variables.set_simulating(False)

    return find_same_box_in_other_board(best_child.previous_box_played, box_game_board, debug=True)



def select(node: MCTSNode):
    # Traverse until we find a node that needs expansion
    while node.childs and len(node.childs) == len(node.box_game_board.get_all_playable_boxes()):
        # Select child with highest UCT value
        node = max(node.childs, key=lambda child: child.uct_value())
    
    # If node has unexpanded children, return it for expansion
    # If it's a terminal node, return it
    return node


def select_best_direct_child(node: MCTSNode, use_uct=True):
    if use_uct:
        max_score = max(child.uct_value() for child in node.childs)
        max_children = [child for child in node.childs if child.uct_value() == max_score]
    else:
        max_score = max((child.score / child.visits) if child.visits > 0 else 0 for child in node.childs)
        max_children = [
            child for child in node.childs
            if (child.score / child.visits if child.visits > 0 else 0) == max_score
        ]

    return random.choice(max_children)


def expand(node: MCTSNode):
    """
    Expand the current node by adding all possible child nodes
    """
    possible_boxes_to_play = node.box_game_board.get_all_playable_boxes()

    new_nodes = []
    for box_to_play in possible_boxes_to_play:
        copy_box_game_board = node.box_game_board.copy()
        box_to_play_copy = find_same_box_in_other_board(box_to_play, copy_box_game_board)

        # We want the possible boxes to play to be in the same board
        possible_boxes_to_play_copy = []
        for possible_box_to_play in possible_boxes_to_play:
            possible_boxes_to_play_copy.append(find_same_box_in_other_board(possible_box_to_play, copy_box_game_board))

        box_to_play_copy.play(node.team_to_play, possible_boxes_to_play_copy)
        new_node = MCTSNode(box_game_board=copy_box_game_board, team_root=node.team_root, team_to_play=not node.team_to_play, parent=node, previous_box_played=box_to_play_copy)
        node.childs.append(new_node)
        new_nodes.append(new_node)

    if new_nodes == []:
        if variables.debug:
            print('No new nodes')
        return [node]

    return new_nodes


def simulate(node: MCTSNode):
    """
    Randomly simulate a game from the current state and return the result
    """
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