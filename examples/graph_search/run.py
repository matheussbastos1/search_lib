import os
import sys

DIR_ATUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.abspath(os.path.join(DIR_ATUAL, "../.."))

if DIR_ATUAL not in sys.path:
    sys.path.insert(0, DIR_ATUAL)
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from graph_search import GraphSearch
from problem import GridPathfinding, GridState


def draw_solution(problem, node):
    """Imprime o mapa com o caminho encontrado marcado por '*'."""
    path_cells = set()
    curr = node
    while curr is not None:
        path_cells.add((curr.state.x, curr.state.y))
        curr = curr.parent

    for y in range(problem.height):
        row = ""
        for x in range(problem.width):
            if (x, y) == (problem.initial_state.x, problem.initial_state.y):
                row += "S"
            elif (x, y) == (problem.goal.x, problem.goal.y):
                row += "G"
            elif (x, y) in problem.obstacles:
                row += "#"
            elif (x, y) in path_cells:
                row += "*"
            else:
                row += "."
        print(row)


def main():
    problem = GridPathfinding.from_file(os.path.join(DIR_ATUAL, "map.txt"))

    for mode in ("bfs", "dfs"):
        result = GraphSearch(problem, mode=mode).search(problem.initial_state)
        m = result.metrics

        print(f"\n=== Graph Search ({mode.upper()}) ===")
        if result.solution_node is None:
            print("Sem solução.")
        else:
            node = result.solution_node
            print("Caminho:", "".join(str(a) for a in node.get_path()))
            print(f"Custo: {node.cost} | Profundidade: {node.depth}")
            draw_solution(problem, node)

        print(f"Nós expandidos: {m.nodes_expanded} | Gerados: {m.nodes_generated} | "
              f"Fronteira máx.: {m.max_frontier_size} | Tempo: {m.execution_time:.6f}s")


if __name__ == "__main__":
    main()