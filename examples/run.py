"""Executa os problemas-exemplo a partir de um único ponto de entrada.

Exemplos:
    python examples/run.py
    python examples/run.py hanoi --disks 4
    python examples/run.py robot --grid-size 6 --algorithm graph-bfs
    python examples/run.py queens --size 8 --algorithm dfs
"""

import argparse
import os
import sys
from typing import Callable

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from search_lib import BFS, DFS, DLS, GraphSearch
from search_lib.core import Problem, SearchResult
from search_lib.problems import (
    Direction,
    HanoiProblem,
    NQueensProblem,
    RobotGridProblem,
    RobotState,
    format_board,
)


ALGORITHMS = ("bfs", "dfs", "dls", "graph-bfs", "graph-dfs")
PROBLEMS = ("hanoi", "robot", "queens")


def build_strategy(problem: Problem, algorithm: str, depth_limit: int | None):
    if algorithm == "bfs":
        return BFS(problem)
    if algorithm == "dfs":
        return DFS(problem)
    if algorithm == "dls":
        if depth_limit is None:
            raise ValueError("DLS exige --depth-limit")
        return DLS(problem, depth_limit=depth_limit)
    if algorithm == "graph-bfs":
        return GraphSearch(problem, mode="bfs")
    if algorithm == "graph-dfs":
        return GraphSearch(problem, mode="dfs")
    raise ValueError(f"Algoritmo desconhecido: {algorithm}")


def print_metrics(result: SearchResult) -> None:
    metrics = result.metrics
    print(f"Nós expandidos: {metrics.nodes_expanded}")
    print(f"Nós gerados: {metrics.nodes_generated}")
    print(f"Fronteira máxima: {metrics.max_frontier_size}")
    print(f"Tempo: {metrics.execution_time * 1000:.3f} ms")


def run_hanoi(args: argparse.Namespace) -> SearchResult:
    problem = HanoiProblem(disks=args.disks)
    strategy = build_strategy(problem, args.algorithm or "graph-bfs", args.depth_limit)
    result = strategy.search(problem.initial_state)

    print(f"\n=== Torre de Hanoi ({args.disks} discos) ===")
    if result.solution_node is None:
        print("Solução não encontrada.")
    else:
        print("Movimentos:")
        for index, action in enumerate(result.solution_node.get_path(), start=1):
            print(f"  {index}. {action}")
        print(f"Custo: {result.solution_node.cost}")
        print(f"Profundidade: {result.solution_node.depth}")
    print_metrics(result)
    return result


def run_robot(args: argparse.Namespace) -> SearchResult:
    size = args.grid_size
    problem = RobotGridProblem(
        map_size=(size, size),
        initial_state=RobotState(0, 0, Direction.EAST),
        goal_position=(size - 1, size - 1),
    )
    strategy = build_strategy(problem, args.algorithm or "graph-bfs", args.depth_limit)
    result = strategy.search(problem.initial_state)

    print(f"\n=== Robô em grid ({size}x{size}) ===")
    if result.solution_node is None:
        print("Caminho não encontrado.")
    else:
        print("Ações:", " ".join(map(str, result.solution_node.get_path())))
        print(f"Custo: {result.solution_node.cost}")
        print(f"Profundidade: {result.solution_node.depth}")
    print_metrics(result)
    return result


def print_queens_board(positions: tuple[int, ...]) -> None:
    print(format_board(positions))


def run_queens(args: argparse.Namespace) -> SearchResult:
    problem = NQueensProblem(size=args.size)
    strategy = build_strategy(problem, args.algorithm or "dfs", args.depth_limit)
    result = strategy.search(problem.initial_state)

    print(f"\n=== N-queens (N={args.size}) ===")
    if result.solution_node is None:
        print("Solução não encontrada.")
    else:
        positions = result.solution_node.state.positions
        print("Colunas por linha:", positions)
        print_queens_board(positions)
        print(f"Custo: {result.solution_node.cost}")
        print(f"Profundidade: {result.solution_node.depth}")
    print_metrics(result)
    return result


RUNNERS: dict[str, Callable[[argparse.Namespace], SearchResult]] = {
    "hanoi": run_hanoi,
    "robot": run_robot,
    "queens": run_queens,
}


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executa um problema de busca")
    parser.add_argument("problem", nargs="?", choices=PROBLEMS)
    parser.add_argument("--algorithm", choices=ALGORITHMS)
    parser.add_argument("--depth-limit", type=int)
    parser.add_argument("--disks", type=int, default=3, help="Discos de Hanoi")
    parser.add_argument("--grid-size", type=int, default=5, help="Lado do grid do robô")
    parser.add_argument("--size", type=int, default=8, help="Tamanho de N-queens")
    return parser


def ask_integer(prompt: str, default: int) -> int:
    value = input(f"{prompt} [{default}]: ").strip()
    return default if not value else int(value)


def interactive_args() -> argparse.Namespace | None:
    print("\nEscolha um problema:")
    print("  1. Torre de Hanoi")
    print("  2. Robô em grid")
    print("  3. N-queens")
    print("  0. Sair")

    choice = input("Opção: ").strip()
    if choice == "0":
        return None

    if choice == "1":
        problem = "hanoi"
        disks = ask_integer("Número de discos", 3)
        size = 8
        grid_size = 5
        default_algorithm = "graph-bfs"
    elif choice == "2":
        problem = "robot"
        disks = 3
        size = 8
        grid_size = ask_integer("Tamanho do grid", 5)
        default_algorithm = "graph-bfs"
    elif choice == "3":
        problem = "queens"
        disks = 3
        size = ask_integer("Valor de N", 8)
        grid_size = 5
        default_algorithm = "dfs"
    else:
        print("Opção inválida.")
        return interactive_args()

    print(f"Algoritmo padrão: {default_algorithm}")
    algorithm = input(f"Algoritmo [{default_algorithm}]: ").strip() or default_algorithm
    depth_limit = None
    if algorithm == "dls":
        depth_limit = ask_integer("Limite de profundidade", size if problem == "queens" else 10)

    return argparse.Namespace(
        problem=problem,
        algorithm=algorithm,
        depth_limit=depth_limit,
        disks=disks,
        grid_size=grid_size,
        size=size,
    )


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.problem is None:
        args = interactive_args()
        if args is None:
            return 0

    try:
        RUNNERS[args.problem](args)
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
