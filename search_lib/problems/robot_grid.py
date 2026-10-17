from dataclasses import dataclass
from enum import Enum
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


def _parse_action_kind(value: RobotActionKind | str) -> RobotActionKind:
    if isinstance(value, RobotActionKind):
        return value
    aliases = {
        "L": RobotActionKind.TURN_LEFT,
        "LEFT": RobotActionKind.TURN_LEFT,
        "R": RobotActionKind.TURN_RIGHT,
        "RIGHT": RobotActionKind.TURN_RIGHT,
        "F": RobotActionKind.FORWARD,
        "FORWARD": RobotActionKind.FORWARD,
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

        nx = state.x + state.direction.dx
        ny = state.y + state.direction.dy
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
        initial_state: RobotState,
        goal_position: tuple[int, int],
        obstacles: Optional[Iterable[tuple[int, int]]] = None,
        allowed_actions: Optional[Iterable[RobotActionKind | str]] = None,
        goal_direction: Optional[Direction] = None,
    ):
        width, height = map_size
        if width < 1 or height < 1:
            raise ValueError("map_size deve conter dimensões positivas")
        if not (0 <= goal_position[0] < width and 0 <= goal_position[1] < height):
            raise ValueError("goal_position fora do grid")

        self.width = width
        self.height = height
        self.initial_state = initial_state
        self.goal_position = goal_position
        self.goal_direction = goal_direction
        self.obstacles = frozenset(obstacles or ())

        kinds = self.DEFAULT_ACTIONS if allowed_actions is None else allowed_actions
        normalized = tuple(_parse_action_kind(kind) for kind in kinds)
        if len(set(normalized)) != len(normalized):
            raise ValueError("allowed_actions não pode conter ações repetidas")
        self.allowed_actions = normalized
        self._actions = tuple(
            RobotAction(kind, width, height, self.obstacles) for kind in normalized
        )

    def actions(self, state: State) -> list[Action]:
        if not isinstance(state, RobotState):
            return []
        return list(self._actions)

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
