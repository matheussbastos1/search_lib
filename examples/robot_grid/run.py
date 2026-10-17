import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import GraphSearch
from search_lib.problems import Direction, RobotGridProblem, RobotState


def main():
    problem = RobotGridProblem(
        map_size=(5, 5),
        initial_state=RobotState(0, 0, Direction.EAST),
        goal_position=(4, 2),
        obstacles={(2, 0), (2, 1), (2, 2)},
    )
    result = GraphSearch(problem).search(problem.initial_state)
    if result.solution_node is None:
        print("Caminho não encontrado.")
        return
    print("Ações:", " ".join(map(str, result.solution_node.get_path())))
    print(f"Custo: {result.solution_node.cost}")
    print(f"Profundidade: {result.solution_node.depth}")
    print(f"Nós expandidos: {result.metrics.nodes_expanded}")


if __name__ == "__main__":
    main()
