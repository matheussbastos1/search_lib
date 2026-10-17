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

from search_lib.algorithms.bfs_tree import BFS
from search_lib.algorithms.dls_tree import DLS
from problem import GridPathfinding, GridState

SIZES = [4, 5, 6, 7]


def plot_metric(sizes, metric_name, data, y_label):
    """Gera um gráfico simples (BFS x DLS) para uma métrica."""
    plt.figure()
    for algo, values in data.items():
        plt.plot(sizes, values, marker="o", label=algo)
    plt.xlabel("Tamanho do grid (N x N)")
    plt.ylabel(y_label)
    plt.title(f"{y_label} por tamanho de grid")
    plt.xticks(sizes)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_ATUAL, f"{metric_name}.png"))
    plt.close()


def run_experiments():
    results = {
        "nodes_number": {"BFS": [], "DLS": []},
        "b_time": {"BFS": [], "DLS": []},
    }

    for N in SIZES:
        problem = GridPathfinding(
            map_limits=(N, N),
            initial_state=GridState(0, 0),
            goal=GridState(N - 1, N - 1),
            obstacles=set(),
        )
        initial = problem.initial_state

        # BFS
        res_bfs = BFS(problem).search(initial)
        results["nodes_number"]["BFS"].append(res_bfs.metrics.nodes_expanded)
        results["b_time"]["BFS"].append(res_bfs.metrics.execution_time)

        # DLS (limite = profundidade da solução ótima: 2*(N-1) passos)
        res_dls = DLS(problem, depth_limit=2 * (N - 1)).search(initial)
        results["nodes_number"]["DLS"].append(res_dls.metrics.nodes_expanded)
        results["b_time"]["DLS"].append(res_dls.metrics.execution_time)

        print(f"{N}x{N} | BFS: {res_bfs.metrics.nodes_expanded} nós | "
              f"DLS: {res_dls.metrics.nodes_expanded} nós")

    plot_metric(SIZES, "nodes_number", results["nodes_number"], "Nós expandidos")
    plot_metric(SIZES, "b_time", results["b_time"], "Tempo de execução (s)")
    print("Gráficos salvos em:", DIR_ATUAL)


if __name__ == "__main__":
    run_experiments()