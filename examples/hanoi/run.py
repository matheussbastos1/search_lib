import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import GraphSearch
from search_lib.problems import HanoiProblem


def main():
    problem = HanoiProblem(disks=3)
    result = GraphSearch(problem).search(problem.initial_state)
    if result.solution_node is None:
        print("Solução não encontrada.")
        return

    print(f"Hanoi com {problem.disks} discos")
    print(" -> ".join(map(str, result.solution_node.get_path())))
    print(f"Movimentos: {result.solution_node.depth}")
    print(f"Nós expandidos: {result.metrics.nodes_expanded}")


if __name__ == "__main__":
    main()
