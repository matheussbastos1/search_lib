import unittest

from search_lib import BFS, DFS, DLS, GraphSearch
from search_lib.problems import (
    Direction,
    HanoiMove,
    HanoiProblem,
    HanoiState,
    NQueensProblem,
    NQueensState,
    PlaceQueenAction,
    RobotAction,
    RobotActionKind,
    RobotGridProblem,
    RobotState,
)


class HanoiTests(unittest.TestCase):
    def test_state_is_immutable_and_hashable(self):
        state = HanoiState(((2, 1), (), ()))
        self.assertEqual(state, HanoiState(((2, 1), (), ())))
        self.assertIsInstance(hash(state), int)
        with self.assertRaises(AttributeError):
            state.pegs = ()

    def test_invalid_moves_are_rejected(self):
        state = HanoiState(((2,), (1,), ()))
        self.assertIsNone(HanoiMove(0, 1, 3).apply(state))
        self.assertIsNone(HanoiMove(0, 0, 3).apply(state))
        self.assertIsNone(HanoiMove(1, 3, 3).apply(state))

    def test_three_disks_have_optimal_solution_of_seven_moves(self):
        problem = HanoiProblem(disks=3)
        result = GraphSearch(problem, mode="bfs").search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)
        self.assertEqual(result.solution_node.depth, 7)
        self.assertEqual(result.solution_node.cost, 7.0)

    def test_known_hanoi_optimal_lengths(self):
        for disks in (1, 2, 3):
            with self.subTest(disks=disks):
                problem = HanoiProblem(disks=disks)
                result = GraphSearch(problem).search(problem.initial_state)
                self.assertIsNotNone(result.solution_node)
                self.assertEqual(result.solution_node.depth, 2**disks - 1)


class RobotGridTests(unittest.TestCase):
    def make_problem(self, **kwargs):
        defaults = dict(
            map_size=(3, 3),
            initial_state=RobotState(0, 0, Direction.EAST),
            goal_position=(2, 0),
        )
        defaults.update(kwargs)
        return RobotGridProblem(**defaults)

    def test_forward_respects_bounds_and_obstacles(self):
        action = RobotAction(
            RobotActionKind.FORWARD,
            width=3,
            height=3,
            obstacles=frozenset({(1, 0)}),
        )
        self.assertIsNone(action.apply(RobotState(0, 0, Direction.EAST)))
        self.assertIsNone(action.apply(RobotState(0, 0, Direction.NORTH)))

    def test_turn_changes_only_direction(self):
        state = RobotState(1, 1, Direction.NORTH)
        action = RobotAction(RobotActionKind.TURN_RIGHT)
        next_state, cost = action.apply(state)
        self.assertEqual(next_state, RobotState(1, 1, Direction.EAST))
        self.assertEqual(cost, 1.0)

    def test_configurable_actions_and_optional_goal_direction(self):
        problem = self.make_problem(
            allowed_actions=("F",),
            goal_position=(1, 0),
            goal_direction=Direction.EAST,
        )
        self.assertEqual(problem.allowed_actions, (RobotActionKind.FORWARD,))
        result = GraphSearch(problem).search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)
        self.assertEqual(result.solution_node.depth, 1)

        impossible = self.make_problem(
            allowed_actions=(RobotActionKind.FORWARD,),
            goal_position=(0, 1),
        )
        self.assertIsNone(GraphSearch(impossible).search(impossible.initial_state).solution_node)

    def test_graph_search_handles_reversible_actions(self):
        problem = self.make_problem(goal_position=(1, 1))
        result = GraphSearch(problem, mode="bfs").search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)
        self.assertEqual(result.solution_node.depth, 3)
        self.assertLessEqual(result.metrics.nodes_generated, 3 * 3 * 4)

    def test_bfs_finds_minimum_path_for_simple_robot(self):
        problem = self.make_problem(goal_position=(2, 0))
        result = BFS(problem).search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)
        self.assertEqual(result.solution_node.depth, 2)


class NQueensTests(unittest.TestCase):
    @staticmethod
    def assert_valid_solution(test_case, state, size):
        test_case.assertIsInstance(state, NQueensState)
        test_case.assertEqual(len(state.positions), size)
        for row_a, col_a in enumerate(state.positions):
            for row_b, col_b in enumerate(state.positions):
                if row_a >= row_b:
                    continue
                test_case.assertNotEqual(col_a, col_b)
                test_case.assertNotEqual(abs(row_a - row_b), abs(col_a - col_b))

    def test_attacks_are_rejected(self):
        state = NQueensState((0,))
        self.assertIsNone(PlaceQueenAction(0, 4).apply(state))
        self.assertIsNone(PlaceQueenAction(1, 4).apply(state))
        self.assertIsNotNone(PlaceQueenAction(2, 4).apply(state))

    def test_bfs_finds_valid_four_queens_solution(self):
        problem = NQueensProblem(4)
        result = BFS(problem).search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)
        self.assert_valid_solution(self, result.solution_node.state, 4)

    def test_dfs_and_dls_find_eight_queens_solution(self):
        problem = NQueensProblem(8)
        for strategy in (DFS(problem), DLS(problem, depth_limit=8)):
            with self.subTest(strategy=type(strategy).__name__):
                result = strategy.search(problem.initial_state)
                self.assertIsNotNone(result.solution_node)
                self.assert_valid_solution(self, result.solution_node.state, 8)
                self.assertEqual(result.solution_node.depth, 8)

    def test_depth_limit_and_unsolvable_instances(self):
        problem = NQueensProblem(4)
        self.assertIsNone(DLS(problem, depth_limit=3).search(problem.initial_state).solution_node)
        for size in (2, 3):
            with self.subTest(size=size):
                problem = NQueensProblem(size)
                result = GraphSearch(problem).search(problem.initial_state)
                self.assertIsNone(result.solution_node)


if __name__ == "__main__":
    unittest.main()
