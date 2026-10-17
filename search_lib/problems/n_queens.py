from dataclasses import dataclass
from typing import Optional, Tuple

from search_lib.core import Action, Problem, State


@dataclass(frozen=True)
class NQueensState(State):
    """Colunas ocupadas, uma entrada para cada linha já preenchida."""

    positions: tuple[int, ...]


@dataclass(frozen=True)
class PlaceQueenAction(Action):
    column: int
    size: int

    def apply(self, state: State) -> Optional[Tuple[State, float]]:
        if not isinstance(state, NQueensState):
            return None
        row = len(state.positions)
        if row >= self.size or not (0 <= self.column < self.size):
            return None

        for previous_row, previous_column in enumerate(state.positions):
            same_column = previous_column == self.column
            same_diagonal = abs(previous_row - row) == abs(previous_column - self.column)
            if same_column or same_diagonal:
                return None

        return NQueensState(state.positions + (self.column,)), 1.0

    def __repr__(self) -> str:
        return f"QUEEN(col={self.column})"


class NQueensProblem(Problem):
    """Problema de posicionamento de N rainhas, uma linha por vez."""

    def __init__(self, size: int = 8):
        if size < 1:
            raise ValueError("size deve ser positivo")
        self.size = size
        self.initial_state = NQueensState(())

    def actions(self, state: State) -> list[Action]:
        if not isinstance(state, NQueensState):
            return []
        return [
            action
            for action in (PlaceQueenAction(column, self.size) for column in range(self.size))
            if action.apply(state) is not None
        ]

    def is_goal(self, state: State) -> bool:
        return isinstance(state, NQueensState) and len(state.positions) == self.size

