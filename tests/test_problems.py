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

    def test_clockwise_only_reaches_goal_with_extra_turns(self):
        # Apenas giro horário (R) e avanço (F)
        problem_cw = self.make_problem(
            allowed_actions=("HORARIO", "FRENTE"),
            goal_position=(0, 1),  # Precisa ir para o SUL (vira à direita e desce)
        )
        result_cw = GraphSearch(problem_cw).search(problem_cw.initial_state)
        self.assertIsNotNone(result_cw.solution_node)
        # Início (0,0) EAST. Vira R -> SOUTH, avança F -> (0, 1). Total: 2 passos (R, F)
        self.assertEqual(result_cw.solution_node.depth, 2)

        # Se precisar virar para o NORTE partindo de EAST, sem anti-horário (L), precisa virar R 3 vezes
        problem_north = self.make_problem(
            initial_state=RobotState(0, 1, Direction.EAST),
            allowed_actions=("HORARIO", "FRENTE"),
            goal_position=(0, 0),
        )
        result_north = GraphSearch(problem_north).search(problem_north.initial_state)
        self.assertIsNotNone(result_north.solution_node)
        # R, R, R, F = 4 passos (pois não tem L)
        self.assertEqual(result_north.solution_node.depth, 4)

    def test_actions_returns_only_applicable_moves(self):
        # No canto (0,0) virado para NORTH, FORWARD bateria na parede superior
        problem = self.make_problem(map_size=(3, 3))
        facing_wall = RobotState(0, 0, Direction.NORTH)
        valid = problem.actions(facing_wall)
        kinds = [a.kind for a in valid]
        self.assertNotIn(RobotActionKind.FORWARD, kinds)
        self.assertIn(RobotActionKind.TURN_LEFT, kinds)
        self.assertIn(RobotActionKind.TURN_RIGHT, kinds)

    def test_render_ascii_output(self):
        problem = RobotGridProblem(
            map_size=(3, 3),
            initial_state=RobotState(0, 0, Direction.EAST),
            goal_position=(2, 2),
            obstacles={(1, 1)},
        )
        rendered = problem.render(current_state=problem.initial_state)
        lines = rendered.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertIn(">", lines[0])  # Robô virado para leste
        self.assertIn("#", lines[1])  # Obstáculo em (1, 1)
        self.assertIn("G", lines[2])  # Objetivo em (2, 2)

    def test_random_walk_produces_valid_states(self):
        problem = self.make_problem(map_size=(5, 5), obstacles={(2, 2)})
        start = RobotState(0, 0, Direction.EAST)
        walked = problem.random_walk(start, n_steps=10, avoid_cycles=True, seed=42)
        self.assertIsInstance(walked, RobotState)
        self.assertTrue(0 <= walked.x < 5 and 0 <= walked.y < 5)
        self.assertNotEqual(walked.position, (2, 2))

    def test_heuristic_is_admissible(self):
        problem = self.make_problem(
            map_size=(4, 4),
            initial_state=RobotState(0, 0, Direction.EAST),
            goal_position=(3, 3),
        )
        h_val = problem.heuristic(problem.initial_state)
        # Manhattan: |0-3| + |0-3| = 6
        self.assertEqual(h_val, 6.0)
        # O custo real ótimo é pelo menos 6 + giros necessários
        result = GraphSearch(problem).search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)
        self.assertLessEqual(h_val, result.solution_node.cost)

    def test_validation_errors(self):
        with self.assertRaises(ValueError):
            # Dimensão inválida
            RobotGridProblem(map_size=(0, 5), goal_position=(0, 0))
        with self.assertRaises(ValueError):
            # Objetivo fora do mapa
            RobotGridProblem(map_size=(3, 3), goal_position=(5, 5))
        with self.assertRaises(ValueError):
            # Objetivo sobre obstáculo
            RobotGridProblem(map_size=(3, 3), goal_position=(1, 1), obstacles={(1, 1)})
        with self.assertRaises(ValueError):
            # Início sobre obstáculo
            RobotGridProblem(
                map_size=(3, 3),
                initial_state=RobotState(1, 1, Direction.EAST),
                goal_position=(2, 2),
                obstacles={(1, 1)},
            )
        with self.assertRaises(ValueError):
            # Início em direção bloqueada
            RobotGridProblem(
                map_size=(3, 3),
                initial_state=RobotState(0, 0, Direction.NORTH),
                goal_position=(2, 2),
                blocked_directions=["NORTE"],
            )
        with self.assertRaises(ValueError):
            # Objetivo em direção bloqueada
            RobotGridProblem(
                map_size=(3, 3),
                initial_state=RobotState(0, 0, Direction.EAST),
                goal_position=(2, 2),
                goal_direction=Direction.WEST,
                blocked_directions=["WEST"],
            )

    def test_blocked_actions_parameter(self):
        # Bloqueia giro anti-horário via blocked_actions
        problem = self.make_problem(
            blocked_actions=["ANTI_HORARIO"],
            goal_position=(0, 1),
        )
        self.assertEqual(len(problem.allowed_actions), 2)
        kinds = [a.kind for a in problem._actions]
        self.assertNotIn(RobotActionKind.TURN_LEFT, kinds)
        self.assertIn(RobotActionKind.TURN_RIGHT, kinds)
        self.assertIn(RobotActionKind.FORWARD, kinds)

        result = GraphSearch(problem).search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)

    def test_backward_action(self):
        # Robô em (1, 1) olhando para EAST. Ao dar ré, vai para (0, 1) mantendo direção EAST
        start = RobotState(1, 1, Direction.EAST)
        problem = self.make_problem(
            map_size=(3, 3),
            initial_state=start,
            goal_position=(0, 1),
            allowed_actions=["FRENTE", "RE", "HORARIO", "ANTI_HORARIO"],
        )
        result = GraphSearch(problem).search(start)
        self.assertIsNotNone(result.solution_node)
        # O caminho ótimo para (0, 1) partindo de (1, 1) olhando EAST com ré é apenas 1 ação: ['B']!
        path = [str(a) for a in result.solution_node.get_path()]
        self.assertEqual(path, ["B"])
        self.assertEqual(result.solution_node.cost, 1.0)

    def test_blocked_directions(self):
        # Proíbe apontar para o SUL. Robô em (0, 0) olhando EAST precisa chegar em (0, 1)
        # Sem poder apontar para o Sul, ele não pode dar giro horário simples (EAST -> SOUTH).
        problem = self.make_problem(
            map_size=(3, 3),
            initial_state=RobotState(0, 0, Direction.EAST),
            goal_position=(0, 1),
            blocked_directions=["SUL"],
            allowed_actions=["FRENTE", "RE", "HORARIO", "ANTI_HORARIO"],
        )
        result = GraphSearch(problem).search(problem.initial_state)
        self.assertIsNotNone(result.solution_node)
        # Verifica se em nenhum estado do caminho o robô ficou apontado para o SUL
        curr = problem.initial_state
        for act in result.solution_node.get_path():
            curr = act.apply(curr)[0]
            self.assertNotEqual(curr.direction, Direction.SOUTH)

    def test_blocked_all_rotations_fails_when_unreachable(self):
        # Robô não pode rotacionar (somente avançar no eixo X)
        problem = self.make_problem(
            map_size=(3, 3),
            initial_state=RobotState(0, 0, Direction.EAST),
            goal_position=(1, 2),  # em outra linha y
            blocked_actions=["HORARIO", "ANTI_HORARIO"],
        )
        result = GraphSearch(problem).search(problem.initial_state)
        self.assertIsNone(result.solution_node)


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
