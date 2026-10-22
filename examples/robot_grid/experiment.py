import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from search_lib import GraphSearch
from search_lib.problems import Direction, RobotGridProblem, RobotState


def main():
    print("tamanho,profundidade,custo,nos_expandidos,nos_gerados,fronteira_max,tempo_ms")
    for size in range(2, 9):
        problem = RobotGridProblem(
            map_size=(size, size),
            initial_state=RobotState(0, 0, Direction.EAST),
            goal_position=(size - 1, size - 1),
        )
        result = GraphSearch(problem, mode="bfs").search(problem.initial_state)
        node = result.solution_node
        metrics = result.metrics
        depth = node.depth if node else ""
        cost = node.cost if node else ""
        print(
            f"{size}x{size},{depth},{cost},"
            f"{metrics.nodes_expanded},{metrics.nodes_generated},"
            f"{metrics.max_frontier_size},{metrics.execution_time * 1000:.4f}"
        )


if __name__ == "__main__":
    main()
