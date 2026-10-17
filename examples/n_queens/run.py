import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import DFS
from search_lib.problems import NQueensProblem


def main():
    problem = NQueensProblem(8)
    result = DFS(problem).search(problem.initial_state)
    if result.solution_node is None:
        print("Solução não encontrada.")
        return
    print("Colunas por linha:", result.solution_node.state.positions)
    print(f"Profundidade: {result.solution_node.depth}")
    print(f"Nós expandidos: {result.metrics.nodes_expanded}")


if __name__ == "__main__":
    main()
