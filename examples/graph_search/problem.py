from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from search_lib.core import Action, Problem, State


@dataclass(frozen=True)
class GridState(State):
    """Posição (x = coluna, y = linha). Imutável e hashável."""
    x: int
    y: int


class Move(Action):
    """Movimento em uma direção. Custo 1 se válido, None se bater em parede/obstáculo."""

    def __init__(self, name: str, dx: int, dy: int, problem: "GridPathfinding"):
        self.name = name
        self.dx = dx
        self.dy = dy
        self.problem = problem

    def apply(self, state: GridState) -> Optional[Tuple[State, float]]:
        nx, ny = state.x + self.dx, state.y + self.dy
        if not self.problem.is_free(nx, ny):
            return None
        return GridState(nx, ny), 1.0

    def __repr__(self) -> str:
        return self.name


class GridPathfinding(Problem):
    """Caminho em grid com obstáculos. Movimentos: cima, baixo, esquerda, direita."""

    def __init__(
        self,
        map_limits: Tuple[int, int],
        initial_state: GridState,
        goal: GridState,
        obstacles: Set[Tuple[int, int]],
    ):
        self.width, self.height = map_limits
        self.initial_state = initial_state
        self.goal = goal
        self.obstacles = obstacles
        self._moves = [
            Move("U", 0, -1, self),
            Move("D", 0, 1, self),
            Move("L", -1, 0, self),
            Move("R", 1, 0, self),
        ]

    @classmethod
    def from_file(cls, path: str) -> "GridPathfinding":
        """
        Lê o mapa de um .txt:
            S = início | G = objetivo | # = obstáculo | . = livre
        """
        with open(path, encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f if line.strip()]

        obstacles, start, goal = set(), None, None
        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                if ch == "#":
                    obstacles.add((x, y))
                elif ch == "S":
                    start = GridState(x, y)
                elif ch == "G":
                    goal = GridState(x, y)

        if start is None or goal is None:
            raise ValueError("O mapa precisa ter 'S' (início) e 'G' (objetivo).")

        return cls((max(len(l) for l in lines), len(lines)), start, goal, obstacles)

    def is_free(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.obstacles

    def actions(self, state: GridState) -> List[Action]:
        return self._moves

    def is_goal(self, state: GridState) -> bool:
        return state == self.goal

    def heuristic(self, state: GridState) -> float:
        return abs(state.x - self.goal.x) + abs(state.y - self.goal.y)