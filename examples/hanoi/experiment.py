import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import GraphSearch
from search_lib.problems import HanoiProblem


def main():
    print("discos,movimentos,nos_expandidos,tempo_s")
    for disks in range(1, 7):
        problem = HanoiProblem(disks=disks)
        result = GraphSearch(problem).search(problem.initial_state)
        node = result.solution_node
        print(
            f"{disks},{node.depth if node else ''},"
            f"{result.metrics.nodes_expanded},{result.metrics.execution_time:.8f}"
        )


if __name__ == "__main__":
    main()
