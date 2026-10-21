from dataclasses import dataclass
from typing import Optional, Tuple

from search_lib.core import Action, Problem, State


@dataclass(frozen=True)
class NQueensState(State):

    positions: tuple[int, ...]

    def board_string(self, size: Optional[int] = None) -> str:
        """Retorna representação gráfica do tabuleiro formatado."""
        return format_board(self.positions, size=size or len(self.positions))


@dataclass(frozen=True)
class PlaceQueenAction(Action):
    """Ação de posicionar uma rainha na próxima linha disponível."""

    column: int
    size: int

    def apply(self, state: State) -> Optional[Tuple[State, float]]:
        if not isinstance(state, NQueensState):
            return None

        current_row = len(state.positions)
        if current_row >= self.size or not (0 <= self.column < self.size):
            return None

        for prev_row, prev_col in enumerate(state.positions):
            same_column = prev_col == self.column
            same_diagonal = abs(prev_row - current_row) == abs(prev_col - self.column)

            if same_column or same_diagonal:
                return None

        next_positions = state.positions + (self.column,)
        return NQueensState(next_positions), 1.0

    def __repr__(self) -> str:
        col_letter = chr(ord("A") + self.column) if self.column < 26 else str(self.column)
        return f"QUEEN(col={col_letter})"


class NQueensProblem(Problem):
    """Definição do problema para o framework de busca."""

    def __init__(self, size: int = 8):
        if size < 1:
            raise ValueError("size deve ser positivo")
        self.size = size
        self.initial_state = NQueensState(())

    def actions(self, state: State) -> list[Action]:
        """Gera apenas as ações válidas para o estado atual."""
        if not isinstance(state, NQueensState):
            return []

        valid_actions: list[Action] = []
        for col in range(self.size):
            action = PlaceQueenAction(column=col, size=self.size)
            if action.apply(state) is not None:
                valid_actions.append(action)
        return valid_actions

    def is_goal(self, state: State) -> bool:
        """Objetivo: todas as N rainhas posicionadas sem conflito."""
        return isinstance(state, NQueensState) and len(state.positions) == self.size


def format_board(positions: tuple[int, ...], size: Optional[int] = None) -> str:
    """Renderiza um tabuleiro limpo e compacto com coordenadas de xadrez."""
    board_size = size if size is not None else len(positions)
    if board_size <= 0:
        return "(tabuleiro vazio)"

    col_headers = [chr(ord("A") + i) if i < 26 else str(i) for i in range(board_size)]
    header = "     " + "   ".join(col_headers)

    inner_width = board_size * 4 + 1
    top_border = "   ┌" + "─" * inner_width + "┐"
    bot_border = "   └" + "─" * inner_width + "┘"

    lines = [header, top_border]

    for row in range(board_size):
        row_label = f"{row + 1:>2} │ "
        queen_col = positions[row] if row < len(positions) else None

        cells = ["Q" if col == queen_col else "·" for col in range(board_size)]
        lines.append(f"{row_label}{'   '.join(cells)} │")

    lines.append(bot_border)
    return "\n".join(lines)
