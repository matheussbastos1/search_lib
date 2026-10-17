import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import DFS
from search_lib.problems import NQueensProblem


def main():
    print("N,profundidade,nos_expandidos,tempo_s")
    for size in range(1, 11):
        problem = NQueensProblem(size)
        result = DFS(problem).search(problem.initial_state)
        node = result.solution_node
        print(
            f"{size},{node.depth if node else ''},"
            f"{result.metrics.nodes_expanded},{result.metrics.execution_time:.8f}"
        )


if __name__ == "__main__":
    main()
