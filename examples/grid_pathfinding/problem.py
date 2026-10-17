from dataclasses import dataclass
from typing import Optional, Tuple, List
from search_lib.core import Action, Problem, State


@dataclass(frozen=True)
class GridState(State):
    x: int
    y: int


class MoveAction(Action):
    def __init__(
        self, 
        dx: int, 
        dy: int, 
        name: str, 
        limits: Optional[Tuple[int, int]] = None,
        cost: float = 1.0
    ):
        self.dx = dx
        self.dy = dy
        self.name = name
        self.limits = limits
        self.step_cost = cost

    def apply(self, state: State) -> Optional[Tuple[State, float]]:
        if not isinstance(state, GridState):
            return None
        
        nx, ny = state.x + self.dx, state.y + self.dy
        
        if self.limits:
            max_x, max_y = self.limits
            if not (0 <= nx < max_x and 0 <= ny < max_y):
                return None
                
        return GridState(nx, ny), self.step_cost

    def __repr__(self) -> str:
        return f"MOVER({self.name})"


def manhattan_distance(state: State, goal: State) -> float:
    if isinstance(state, GridState) and isinstance(goal, GridState):
        return float(abs(state.x - goal.x) + abs(state.y - goal.y))
    return 0.0


class GridPathfinding(Problem):
    """
    Problema de busca de caminhos em malha 2D.
    Pode ser inicializado via parâmetros directos ou carregado a partir de um arquivo de texto.
    """
    def __init__(
        self, 
        map_limits: Optional[Tuple[int, int]] = None, 
        initial_state: Optional[GridState] = None,
        goal: Optional[GridState] = None, 
        permite_diag: bool = False,
        obstacles: Optional[set[GridState]] = None,
        file: Optional[str] = None
    ):
        self.permite_diag = permite_diag
        self.obstacles: set[GridState] = obstacles or set()
        self.initial_state = initial_state or GridState(0, 0)
        self.goal = goal
        self.width = map_limits[0] if map_limits else 10
        self.height = map_limits[1] if map_limits else 10

        if file:
            self._load_from_file(file)

    def _load_from_file(self, filepath: str) -> None:
        """Carrega o mapa a partir de um arquivo de texto."""
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        self.height = len(lines)
        self.width = len(lines[0]) if self.height > 0 else 0
        self.obstacles = set()

        for y, row in enumerate(lines):
            for x, char in enumerate(row):
                if char == '#':
                    self.obstacles.add(GridState(x, y))
                elif char == 'S':
                    self.initial_state = GridState(x, y)
                elif char == 'G':
                    self.goal = GridState(x, y)

    def actions(self, state: State) -> List[Action]:
        if not isinstance(state, GridState):
            return []

        moves = [
            MoveAction(0, -1, "CIMA", (self.width, self.height)),
            MoveAction(0, 1, "BAIXO", (self.width, self.height)),
            MoveAction(-1, 0, "ESQUERDA", (self.width, self.height)),
            MoveAction(1, 0, "DIREITA", (self.width, self.height)),
        ]

        if self.permite_diag:
            # Movimentos diagonais têm custo maior (ex: sqrt(2) ≈ 1.414)
            moves.extend([
                MoveAction(-1, -1, "DIAG_SUP_ESQ", (self.width, self.height), cost=1.414),
                MoveAction(1, -1, "DIAG_SUP_DIR", (self.width, self.height), cost=1.414),
                MoveAction(-1, 1, "DIAG_INF_ESQ", (self.width, self.height), cost=1.414),
                MoveAction(1, 1, "DIAG_INF_DIR", (self.width, self.height), cost=1.414),
            ])

        valid_actions = []
        for move in moves:
            res = move.apply(state)
            if res is not None:
                nxt_state, _ = res
                if nxt_state not in self.obstacles:
                    valid_actions.append(move)

        return valid_actions

    def is_goal(self, state: State) -> bool:
        return state == self.goal

    def heuristic(self, state: State) -> float:
        if self.goal is None:
            return 0.0
        return manhattan_distance(state, self.goal)