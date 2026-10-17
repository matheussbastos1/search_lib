import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR_ATUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.abspath(os.path.join(DIR_ATUAL, "../.."))

if DIR_ATUAL not in sys.path:
    sys.path.insert(0, DIR_ATUAL)
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from graph_search import GraphSearch
from problem import GridPathfinding, GridState

SIZES = [5, 6, 7, 8]


def plot_metric(sizes, metric_name, data, y_label):
    """Gera um gráfico simples (BFS x DFS) para uma métrica."""
    plt.figure()
    for algo, values in data.items():
        plt.plot(sizes, values, marker="o", label=algo)
    plt.xlabel("Tamanho do grid (N x N)")
    plt.ylabel(y_label)
    plt.title(f"Graph Search - {y_label} por tamanho de grid")
    plt.xticks(sizes)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_ATUAL, f"graph_{metric_name}.png"))
    plt.close()


def run_experiments():
    results = {
        "nodes_number": {"BFS": [], "DFS": []},
        "b_time": {"BFS": [], "DFS": []},
    }

    for N in SIZES:
        problem = GridPathfinding(
            map_limits=(N, N),
            initial_state=GridState(0, 0),
            goal=GridState(N - 1, N - 1),
            obstacles=set(),
        )
        initial = problem.initial_state

        res_bfs = GraphSearch(problem, mode="bfs").search(initial)
        results["nodes_number"]["BFS"].append(res_bfs.metrics.nodes_expanded)
        results["b_time"]["BFS"].append(res_bfs.metrics.execution_time)

        res_dfs = GraphSearch(problem, mode="dfs").search(initial)
        results["nodes_number"]["DFS"].append(res_dfs.metrics.nodes_expanded)
        results["b_time"]["DFS"].append(res_dfs.metrics.execution_time)

        print(f"{N}x{N} | BFS: {res_bfs.metrics.nodes_expanded} nós | "
              f"DFS: {res_dfs.metrics.nodes_expanded} nós")

    plot_metric(SIZES, "nodes_number", results["nodes_number"], "Nós expandidos")
    plot_metric(SIZES, "b_time", results["b_time"], "Tempo de execução (s)")
    print("Gráficos salvos em:", DIR_ATUAL)


if __name__ == "__main__":
    run_experiments()