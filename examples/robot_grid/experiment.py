import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import GraphSearch
from search_lib.problems import Direction, RobotGridProblem, RobotState


def main():
    print("tamanho,profundidade,nos_expandidos,tempo_s")
    for size in range(2, 8):
        problem = RobotGridProblem(
            map_size=(size, size),
            initial_state=RobotState(0, 0, Direction.EAST),
            goal_position=(size - 1, size - 1),
        )
        result = GraphSearch(problem).search(problem.initial_state)
        node = result.solution_node
        print(
            f"{size},{node.depth if node else ''},"
            f"{result.metrics.nodes_expanded},{result.metrics.execution_time:.8f}"
        )


if __name__ == "__main__":
    main()
