from dataclasses import dataclass
import unittest

from search_lib import Action, GraphSearch, Problem, State


@dataclass(frozen=True)
class TinyState(State):
    value: int


@dataclass(frozen=True)
class StepAction(Action):
    delta: int

    def apply(self, state):
        if not isinstance(state, TinyState):
            return None
        next_value = state.value + self.delta
        if not 0 <= next_value <= 2:
            return None
        return TinyState(next_value), 1.0


class TinyCyclicProblem(Problem):
    def actions(self, state):
        return [StepAction(-1), StepAction(1)]

    def is_goal(self, state):
        return state == TinyState(2)


class CoreAlgorithmTests(unittest.TestCase):
    def test_graph_search_reconstructs_path_and_accumulates_cost(self):
        result = GraphSearch(TinyCyclicProblem()).search(TinyState(0))
        self.assertIsNotNone(result.solution_node)
        self.assertEqual(result.solution_node.get_path(), [StepAction(1), StepAction(1)])
        self.assertEqual(result.solution_node.depth, 2)
        self.assertEqual(result.solution_node.cost, 2.0)

    def test_graph_search_does_not_generate_repeated_states(self):
        result = GraphSearch(TinyCyclicProblem()).search(TinyState(0))
        self.assertEqual(result.metrics.nodes_generated, 3)
        self.assertEqual(result.metrics.nodes_expanded, 3)
        self.assertGreaterEqual(result.metrics.max_frontier_size, 1)
        self.assertGreaterEqual(result.metrics.nodes_generated, result.metrics.nodes_expanded)


if __name__ == "__main__":
    unittest.main()
