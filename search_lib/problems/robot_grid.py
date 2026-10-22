from dataclasses import dataclass
from enum import Enum
import random
from typing import Iterable, Optional, Tuple

from search_lib.core import Action, Problem, State


class Direction(Enum):
    NORTH = (0, -1, "N")
    EAST = (1, 0, "E")
    SOUTH = (0, 1, "S")
    WEST = (-1, 0, "W")

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    @property
    def symbol(self) -> str:
        return self.value[2]

    @property
    def arrow(self) -> str:
        arrows = {
            Direction.NORTH: "^",
            Direction.EAST: ">",
            Direction.SOUTH: "v",
            Direction.WEST: "<",
        }
        return arrows[self]

    def turn_left(self) -> "Direction":
        directions = tuple(Direction)
        return directions[(directions.index(self) - 1) % len(directions)]

    def turn_right(self) -> "Direction":
        directions = tuple(Direction)
        return directions[(directions.index(self) + 1) % len(directions)]


@dataclass(frozen=True)
class RobotState(State):
    x: int
    y: int
    direction: Direction

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y


class RobotActionKind(Enum):
    TURN_LEFT = "L"
    TURN_RIGHT = "R"
    FORWARD = "F"
    BACKWARD = "B"


def _parse_direction(value: Direction | str) -> Direction:
    if isinstance(value, Direction):
        return value
    aliases = {
        "N": Direction.NORTH,
        "NORTH": Direction.NORTH,
        "NORTE": Direction.NORTH,
        "E": Direction.EAST,
        "EAST": Direction.EAST,
        "LESTE": Direction.EAST,
        "S": Direction.SOUTH,
        "SOUTH": Direction.SOUTH,
        "SUL": Direction.SOUTH,
        "W": Direction.WEST,
        "WEST": Direction.WEST,
        "OESTE": Direction.WEST,
    }
    try:
        return aliases[value.upper()]
    except (AttributeError, KeyError) as error:
        raise ValueError(f"Direção desconhecida: {value!r}") from error


def _parse_action_kind(value: RobotActionKind | str) -> RobotActionKind:
    if isinstance(value, RobotActionKind):
        return value
    aliases = {
        "L": RobotActionKind.TURN_LEFT,
        "LEFT": RobotActionKind.TURN_LEFT,
        "ANTI_HORARIO": RobotActionKind.TURN_LEFT,
        "ANTI-HORARIO": RobotActionKind.TURN_LEFT,
        "ANTIHORARIO": RobotActionKind.TURN_LEFT,
        "SENTIDO_ANTI_HORARIO": RobotActionKind.TURN_LEFT,
        "CCW": RobotActionKind.TURN_LEFT,
        "R": RobotActionKind.TURN_RIGHT,
        "RIGHT": RobotActionKind.TURN_RIGHT,
        "HORARIO": RobotActionKind.TURN_RIGHT,
        "SENTIDO_HORARIO": RobotActionKind.TURN_RIGHT,
        "CW": RobotActionKind.TURN_RIGHT,
        "F": RobotActionKind.FORWARD,
        "FORWARD": RobotActionKind.FORWARD,
        "FRENTE": RobotActionKind.FORWARD,
        "AVANCAR": RobotActionKind.FORWARD,
        "B": RobotActionKind.BACKWARD,
        "BACK": RobotActionKind.BACKWARD,
        "BACKWARD": RobotActionKind.BACKWARD,
        "RE": RobotActionKind.BACKWARD,
        "MARCHA_RE": RobotActionKind.BACKWARD,
        "TRAS": RobotActionKind.BACKWARD,
    }
    try:
        return aliases[value.upper()]
    except (AttributeError, KeyError) as error:
        raise ValueError(f"Ação de robô desconhecida: {value!r}") from error


@dataclass(frozen=True)
class RobotAction(Action):
    kind: RobotActionKind
    width: Optional[int] = None
    height: Optional[int] = None
    obstacles: frozenset[tuple[int, int]] = frozenset()

    def apply(self, state: State) -> Optional[Tuple[State, float]]:
        if not isinstance(state, RobotState):
            return None

        if self.kind == RobotActionKind.TURN_LEFT:
            return RobotState(state.x, state.y, state.direction.turn_left()), 1.0
        if self.kind == RobotActionKind.TURN_RIGHT:
            return RobotState(state.x, state.y, state.direction.turn_right()), 1.0

        if self.kind == RobotActionKind.FORWARD:
            nx = state.x + state.direction.dx
            ny = state.y + state.direction.dy
        elif self.kind == RobotActionKind.BACKWARD:
            nx = state.x - state.direction.dx
            ny = state.y - state.direction.dy
        else:
            return None

        if self.width is not None and not (0 <= nx < self.width):
            return None
        if self.height is not None and not (0 <= ny < self.height):
            return None
        if (nx, ny) in self.obstacles:
            return None
        return RobotState(nx, ny, state.direction), 1.0

    def __repr__(self) -> str:
        return self.kind.value


class RobotGridProblem(Problem):
    """Robô em grid com ações de giro e avanço configuráveis."""

    DEFAULT_ACTIONS = (
        RobotActionKind.TURN_LEFT,
        RobotActionKind.TURN_RIGHT,
        RobotActionKind.FORWARD,
    )

    def __init__(
        self,
        map_size: tuple[int, int],
        initial_state: Optional[RobotState] = None,
        goal_position: tuple[int, int] = (0, 0),
        obstacles: Optional[Iterable[tuple[int, int]]] = None,
        allowed_actions: Optional[Iterable[RobotActionKind | str]] = None,
        blocked_actions: Optional[Iterable[RobotActionKind | str]] = None,
        blocked_directions: Optional[Iterable[Direction | str]] = None,
        goal_direction: Optional[Direction | str] = None,
    ):
        width, height = map_size
        if width < 1 or height < 1:
            raise ValueError("map_size deve conter dimensões positivas")
        if not (0 <= goal_position[0] < width and 0 <= goal_position[1] < height):
            raise ValueError("goal_position fora do grid")

        self.width = width
        self.height = height
        self.obstacles = frozenset(obstacles or ())
        if goal_position in self.obstacles:
            raise ValueError("goal_position não pode estar sobre um obstáculo")

        if blocked_directions is not None:
            self.blocked_directions = frozenset(_parse_direction(d) for d in blocked_directions)
        else:
            self.blocked_directions = frozenset()

        if initial_state is not None:
            if not (0 <= initial_state.x < width and 0 <= initial_state.y < height):
                raise ValueError("initial_state fora do grid")
            if initial_state.position in self.obstacles:
                raise ValueError("initial_state não pode estar sobre um obstáculo")
            if initial_state.direction in self.blocked_directions:
                raise ValueError("initial_state não pode estar voltado para uma direção bloqueada")

        parsed_goal_direction = _parse_direction(goal_direction) if goal_direction is not None else None
        if parsed_goal_direction in self.blocked_directions:
            raise ValueError("goal_direction não pode ser uma direção bloqueada")

        self.initial_state = initial_state
        self.goal_position = goal_position
        self.goal_direction = parsed_goal_direction

        kinds = self.DEFAULT_ACTIONS if allowed_actions is None else allowed_actions
        normalized = [_parse_action_kind(kind) for kind in kinds]

        if blocked_actions is not None:
            blocked_set = {_parse_action_kind(k) for k in blocked_actions}
            normalized = [k for k in normalized if k not in blocked_set]

        if len(set(normalized)) != len(normalized):
            raise ValueError("allowed_actions não pode conter ações repetidas")

        self.allowed_actions = tuple(normalized)
        self._actions = tuple(
            RobotAction(kind, width, height, self.obstacles) for kind in normalized
        )

    def actions(self, state: State) -> list[Action]:
        if not isinstance(state, RobotState):
            return []
        valid = []
        for action in self._actions:
            res = action.apply(state)
            if res is not None:
                next_state = res[0]
                if isinstance(next_state, RobotState) and next_state.direction in self.blocked_directions:
                    continue
                valid.append(action)
        return valid

    def is_goal(self, state: State) -> bool:
        if not isinstance(state, RobotState):
            return False
        return (
            state.position == self.goal_position
            and (
                self.goal_direction is None
                or state.direction == self.goal_direction
            )
        )

    def heuristic(self, state: State) -> float:
        if not isinstance(state, RobotState):
            return 0.0
        return float(abs(state.x - self.goal_position[0]) + abs(state.y - self.goal_position[1]))

    def random_walk(
        self,
        start_state: RobotState,
        n_steps: int,
        avoid_cycles: bool = False,
        seed: Optional[int] = None,
    ) -> RobotState:
        """Gera um estado aleatório por random walk após n_steps ações aplicáveis."""
        rng = random.Random(seed)
        current = start_state
        visited = {current} if avoid_cycles else None

        for _ in range(n_steps):
            possible = self.actions(current)
            if not possible:
                break

            candidates = []
            for act in possible:
                nxt = act.apply(current)
                if nxt is not None:
                    next_state = nxt[0]
                    if isinstance(next_state, RobotState):
                        if not avoid_cycles or next_state not in visited:
                            candidates.append(next_state)

            if not candidates:
                if avoid_cycles:
                    all_nxt = [
                        res[0] for act in possible
                        if (res := act.apply(current)) is not None
                        and isinstance(res[0], RobotState)
                    ]
                    if not all_nxt:
                        break
                    current = rng.choice(all_nxt)
                else:
                    break
            else:
                current = rng.choice(candidates)

            if avoid_cycles and visited is not None:
                visited.add(current)

        return current

    def render(
        self,
        current_state: Optional[RobotState] = None,
        path_states: Optional[Iterable[RobotState]] = None,
    ) -> str:
        """Renderiza o grid em formato ASCII."""
        path_pos = {s.position: s.direction.arrow for s in (path_states or [])}

        lines = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                pos = (x, y)
                if current_state and pos == current_state.position:
                    row.append(current_state.direction.arrow)
                elif pos == self.goal_position:
                    row.append("G")
                elif pos in self.obstacles:
                    row.append("#")
                elif pos in path_pos:
                    row.append(path_pos[pos])
                else:
                    row.append(".")
            lines.append(" ".join(row))
        return "\n".join(lines)
