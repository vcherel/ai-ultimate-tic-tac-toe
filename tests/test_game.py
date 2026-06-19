import math
import pytest

from variables import variables
from box_game import BoxGame, get_next_move_random_best_strategy
from mcts_node import MCTSNode, simulate as mcts_simulate, backpropagate


@pytest.fixture(autouse=True)
def guard_global_state():
    """Prevent victory/simulate calls from mutating the global variables singleton."""
    variables.simulating = True
    variables.finished = None
    variables.winner = None
    yield
    variables.simulating = False


def make_board(depth=1):
    return BoxGame(depth=depth, id_box=0, parent=None)


def set_states(board, states):
    """Set child states on a depth-1 board."""
    for i, s in enumerate(states):
        board.childs[i].state = s


# ── detect_victory ────────────────────────────────────────────────────────────


class TestDetectVictory:
    def test_empty_board(self):
        assert make_board().detect_victory() is False

    def test_row_0(self):
        b = make_board()
        set_states(b, [True, True, True, None, None, None, None, None, None])
        assert b.detect_victory() is True

    def test_row_1(self):
        b = make_board()
        set_states(b, [None, None, None, False, False, False, None, None, None])
        assert b.detect_victory() is True

    def test_row_2(self):
        b = make_board()
        set_states(b, [None, None, None, None, None, None, True, True, True])
        assert b.detect_victory() is True

    def test_col_0(self):
        b = make_board()
        set_states(b, [True, None, None, True, None, None, True, None, None])
        assert b.detect_victory() is True

    def test_col_1(self):
        b = make_board()
        set_states(b, [None, False, None, None, False, None, None, False, None])
        assert b.detect_victory() is True

    def test_col_2(self):
        b = make_board()
        set_states(b, [None, None, True, None, None, True, None, None, True])
        assert b.detect_victory() is True

    def test_diagonal_main(self):
        b = make_board()
        set_states(b, [True, None, None, None, True, None, None, None, True])
        assert b.detect_victory() is True

    def test_diagonal_anti(self):
        b = make_board()
        set_states(b, [None, None, False, None, False, None, False, None, None])
        assert b.detect_victory() is True

    def test_partial_no_victory(self):
        b = make_board()
        set_states(b, [True, False, True, False, True, None, False, True, None])
        assert b.detect_victory() is False

    def test_two_in_row_blocked_by_opponent(self):
        b = make_board()
        set_states(b, [True, True, False, None, None, None, None, None, None])
        assert b.detect_victory() is False

    def test_full_draw_no_victory(self):
        # F T F / F F T / T F T — verified draw position
        b = make_board()
        set_states(b, [False, True, False, False, False, True, True, False, True])
        assert b.detect_victory() is False


# ── get_all_playable_boxes ────────────────────────────────────────────────────


class TestGetAllPlayableBoxes:
    def test_depth0_leaf_is_playable(self):
        b = make_board(depth=0)
        assert len(b.get_all_playable_boxes()) == 1

    def test_depth1_fresh_all_9_playable(self):
        b = make_board(depth=1)
        assert len(b.get_all_playable_boxes()) == 9

    def test_depth2_fresh_all_81_playable(self):
        b = make_board(depth=2)
        assert len(b.get_all_playable_boxes()) == 81

    def test_occupied_cells_excluded(self):
        b = make_board(depth=1)
        b.childs[0].state = True
        b.childs[0].playable = False
        b.childs[4].state = False
        b.childs[4].playable = False
        assert len(b.get_all_playable_boxes()) == 7

    def test_won_mini_board_has_no_playable(self):
        b = make_board(depth=1)
        b.victory(True)  # clears childs, sets state
        assert b.get_all_playable_boxes() == []

    def test_all_cells_occupied_no_playable(self):
        b = make_board(depth=1)
        for child in b.childs:
            child.state = True
            child.playable = False
        assert b.get_all_playable_boxes() == []


# ── simulate ──────────────────────────────────────────────────────────────────


class TestSimulate:
    def test_won_board_returns_previous_team(self):
        # won board → childs cleared → simulate returns not next_team_to_play
        b = make_board(depth=2)
        b.victory(True)
        assert b.simulate(True) is False  # not True
        assert b.simulate(False) is True  # not False

    def test_draw_board_returns_none(self):
        # Full, draw-positioned depth-1 board has no playable cells → None
        b = make_board(depth=1)
        draw_states = [False, True, False, False, False, True, True, False, True]
        for i, s in enumerate(draw_states):
            b.childs[i].state = s
            b.childs[i].playable = False
        assert b.simulate(True) is None

    def test_fresh_board_returns_valid_result(self):
        b = make_board(depth=2)
        assert b.simulate(True) in (True, False, None)

    def test_does_not_mutate_original_board(self):
        b = make_board(depth=1)
        original_states = [c.state for c in b.childs]
        b.simulate(True)
        assert [c.state for c in b.childs] == original_states


# ── get_next_move_random_best_strategy ────────────────────────────────────────


class TestHeuristic:
    def _board_and_playable(self, states):
        """Build a depth-1 board from a state list and return (board, playable_boxes)."""
        b = make_board(depth=1)
        for i, s in enumerate(states):
            b.childs[i].state = s
            if s is not None:
                b.childs[i].playable = False
        return b, b.get_all_playable_boxes()

    def test_takes_winning_row(self):
        b, playable = self._board_and_playable(
            [True, True, None, None, None, None, None, None, None]
        )
        assert get_next_move_random_best_strategy(True, playable) is b.childs[2]

    def test_takes_winning_col(self):
        b, playable = self._board_and_playable(
            [False, None, None, False, None, None, None, None, None]
        )
        assert get_next_move_random_best_strategy(False, playable) is b.childs[6]

    def test_takes_winning_diagonal(self):
        b, playable = self._board_and_playable(
            [True, None, None, None, True, None, None, None, None]
        )
        assert get_next_move_random_best_strategy(True, playable) is b.childs[8]

    def test_blocks_opponent_row(self):
        b, playable = self._board_and_playable(
            [False, False, None, None, None, None, None, None, None]
        )
        assert get_next_move_random_best_strategy(True, playable) is b.childs[2]

    def test_blocks_opponent_col(self):
        b, playable = self._board_and_playable(
            [None, True, None, None, True, None, None, None, None]
        )
        assert get_next_move_random_best_strategy(False, playable) is b.childs[7]

    def test_win_takes_priority_over_block(self):
        # True can win column [2,5,8] AND block opponent row [0,1,2] — both at index 2
        # (also verifies the win branch fires before the block branch)
        b, playable = self._board_and_playable(
            [False, False, None, None, None, True, None, None, True]
        )
        assert get_next_move_random_best_strategy(True, playable) is b.childs[2]


# ── MCTS node scoring ─────────────────────────────────────────────────────────


class TestMCTSNode:
    def test_uct_unvisited_is_inf(self):
        root = MCTSNode(make_board(2), team_root=True, team_to_play=True)
        root.visits = 1
        child = MCTSNode(make_board(2), team_root=True, team_to_play=False, parent=root)
        assert child.uct_value() == float("inf")

    def test_uct_formula(self):
        root = MCTSNode(make_board(2), team_root=True, team_to_play=True)
        root.visits = 10
        child = MCTSNode(make_board(2), team_root=True, team_to_play=False, parent=root)
        child.visits = 4
        child.score = 8
        expected = 8 / 4 + 1.4 * math.sqrt(math.log(10) / 4)
        assert abs(child.uct_value() - expected) < 1e-10

    def test_confidence_zero_visits(self):
        node = MCTSNode(make_board(2), team_root=True, team_to_play=True)
        assert node.confidence_value() == 0

    def test_confidence_formula(self):
        root = MCTSNode(make_board(2), team_root=True, team_to_play=True)
        child = MCTSNode(make_board(2), team_root=True, team_to_play=False, parent=root)
        child.visits = 6
        child.score = 3
        assert abs(child.confidence_value() - (3 / 6) * 100 / 3) < 1e-10


class TestMCTSSimulateScore:
    def test_win_scores_3(self):
        b = make_board(2)
        b.victory(True)
        # board won by True; simulate(False) → not False = True == team_root → 3
        node = MCTSNode(b, team_root=True, team_to_play=False)
        assert mcts_simulate(node) == 3

    def test_loss_scores_0(self):
        b = make_board(2)
        b.victory(False)
        # board won by False; simulate(True) → not True = False ≠ team_root → 0
        node = MCTSNode(b, team_root=True, team_to_play=True)
        assert mcts_simulate(node) == 0.0

    def test_draw_scores_1(self):
        b = make_board(1)
        draw_states = [False, True, False, False, False, True, True, False, True]
        for i, s in enumerate(draw_states):
            b.childs[i].state = s
            b.childs[i].playable = False
        node = MCTSNode(b, team_root=True, team_to_play=True)
        assert mcts_simulate(node) == 1


class TestBackpropagate:
    def test_propagates_score_to_root(self):
        root = MCTSNode(make_board(2), team_root=True, team_to_play=True)
        child = MCTSNode(make_board(2), team_root=True, team_to_play=False, parent=root)
        grandchild = MCTSNode(
            make_board(2), team_root=True, team_to_play=True, parent=child
        )

        backpropagate(grandchild, 3)

        assert grandchild.visits == 1 and grandchild.score == 3
        assert child.visits == 1 and child.score == 3
        assert root.visits == 1 and root.score == 3

    def test_accumulates_across_visits(self):
        root = MCTSNode(make_board(2), team_root=True, team_to_play=True)
        child = MCTSNode(make_board(2), team_root=True, team_to_play=False, parent=root)

        backpropagate(child, 3)
        backpropagate(child, 0)

        assert child.visits == 2 and child.score == 3
        assert root.visits == 2 and root.score == 3
