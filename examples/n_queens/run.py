"""Execução e demonstração do problema das N-Rainhas.

Mostra a resolução por busca em profundidade (DFS), a reconstrução do caminho
linha a linha, a renderização gráfica do tabuleiro e a comparação com BFS.
"""

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import BFS, DFS
from search_lib.core import SearchNode
from search_lib.problems import NQueensProblem


def col_to_letter(col: int) -> str:
    """Converte índice numérico de coluna para notação de xadrez (0 -> A, etc.)."""
    return chr(ord("A") + col) if 0 <= col < 26 else str(col)


def get_path_steps(node: SearchNode) -> list[tuple[int, int]]:
    """Extrai os pares (linha, coluna) percorridos da raiz até o nó objetivo."""
    path = []
    curr = node
    while curr is not None and curr.state.positions:
        row = len(curr.state.positions)
        col = curr.state.positions[-1]
        path.append((row, col))
        curr = curr.parent
    path.reverse()
    return path


def print_step_by_step(steps: list[tuple[int, int]]) -> None:
    """Imprime o passo a passo da solução em duas colunas organizadas."""
    print("[2] Reconstrução do Caminho (Passo a Passo):")
    half = (len(steps) + 1) // 2
    for i in range(half):
        row1, col1 = steps[i]
        item1 = f"  • Linha {row1} ➔ Coluna {col_to_letter(col1)} ({col1})"
        if i + half < len(steps):
            row2, col2 = steps[i + half]
            item2 = f"  • Linha {row2} ➔ Coluna {col_to_letter(col2)} ({col2})"
            print(f"{item1:<32} {item2}")
        else:
            print(item1)
    print()


def print_comparison_table(problem: NQueensProblem, dfs_res, bfs_res) -> None:
    """Imprime uma tabela comparativa limpa e alinhada entre DFS e BFS."""
    dfs_m = dfs_res.metrics
    bfs_m = bfs_res.metrics
    dfs_node = dfs_res.solution_node
    bfs_node = bfs_res.solution_node

    print("[4] Comparação de Desempenho (DFS vs BFS):")
    print("   ┌───────────────────────────┬──────────────┬──────────────┐")
    print("   │ Métrica                   │ DFS (Árvore) │ BFS (Árvore) │")
    print("   ├───────────────────────────┼──────────────┼──────────────┤")
    print(f"   │ Solução encontrada?       │ {'Sim':<12} │ {'Sim':<12} │")
    print(f"   │ Profundidade da meta      │ {str(dfs_node.depth if dfs_node else '-'):<12} │ {str(bfs_node.depth if bfs_node else '-'):<12} │")
    print(f"   │ Nós expandidos            │ {dfs_m.nodes_expanded:<12,d} │ {bfs_m.nodes_expanded:<12,d} │".replace(",", "."))
    print(f"   │ Nós gerados               │ {dfs_m.nodes_generated:<12,d} │ {bfs_m.nodes_generated:<12,d} │".replace(",", "."))
    print(f"   │ Fronteira máxima (RAM)    │ {f'{dfs_m.max_frontier_size} nós':<12} │ {f'{bfs_m.max_frontier_size} nós':<12} │")
    print(f"   │ Tempo de execução         │ {f'{dfs_m.execution_time * 1000:.2f} ms':<12} │ {f'{bfs_m.execution_time * 1000:.2f} ms':<12} │")
    print("   └───────────────────────────┴──────────────┴──────────────┘")


def main():
    parser = argparse.ArgumentParser(description="Demonstração do problema das N-Rainhas")
    parser.add_argument("--size", type=int, default=8, help="Número de rainhas (padrão: 8)")
    parser.add_argument("--no-compare", action="store_true", help="Pula a comparação com o BFS")
    args = parser.parse_args()

    size = args.size
    problem = NQueensProblem(size=size)

    print()
    print("=" * 60)
    print(f"    PROBLEMA DAS {size} RAINHAS — BUSCA NO ESPAÇO DE ESTADOS")
    print("=" * 60)
    print()

    print("[1] Executando Busca em Profundidade (DFS)...")
    dfs_result = DFS(problem).search(problem.initial_state)

    if dfs_result.solution_node is None:
        print(f"    ✗ Nenhuma solução encontrada para N={size}.\n")
        return

    sol_node = dfs_result.solution_node
    print(f"    ✓ Solução encontrada em {dfs_result.metrics.execution_time * 1000:.2f} ms")
    print(f"    ✓ Nós expandidos: {dfs_result.metrics.nodes_expanded} | Nós gerados: {dfs_result.metrics.nodes_generated}")
    print()

    steps = get_path_steps(sol_node)
    print_step_by_step(steps)

    print("[3] Tabuleiro Final (Configuração Válida):")
    print(sol_node.state.board_string(size=size))
    print()

    if not args.no_compare:
        bfs_result = BFS(problem).search(problem.initial_state)
        print_comparison_table(problem, dfs_result, bfs_result)
        print()

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
