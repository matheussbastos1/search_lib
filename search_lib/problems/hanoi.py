from dataclasses import dataclass
from typing import Optional, Tuple

from search_lib.core import Action, Problem, State


@dataclass(frozen=True)
class HanoiState(State):
    """Configuração das hastes, com cada tupla armazenada da base ao topo."""

    pegs: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class HanoiMove(Action):
    """Move o disco do topo de uma haste para outra."""

    source: int
    target: int
    peg_count: int

    def apply(self, state: State) -> Optional[Tuple[State, float]]:
        if not isinstance(state, HanoiState):
            return None
        if not (0 <= self.source < self.peg_count):
            return None
        if not (0 <= self.target < self.peg_count):
            return None
        if self.source == self.target:
            return None
        if len(state.pegs) != self.peg_count:
            return None

        source_peg = state.pegs[self.source]
        target_peg = state.pegs[self.target]
        if not source_peg:
            return None

        disk = source_peg[-1]
        if target_peg and target_peg[-1] < disk:
            return None

        pegs = list(state.pegs)
        pegs[self.source] = source_peg[:-1]
        pegs[self.target] = target_peg + (disk,)
        return HanoiState(tuple(pegs)), 1.0

    def __repr__(self) -> str:
        return f"MOVE({self.source}->{self.target})"


class HanoiProblem(Problem):
    """Torre de Hanoi parametrizável por número de discos e hastes."""

    def __init__(
        self,
        disks: int = 3,
        peg_count: int = 3,
        start_peg: int = 0,
        goal_peg: int = 2,
    ):
        if disks < 1:
            raise ValueError("disks deve ser positivo")
        if peg_count < 3:
            raise ValueError("Hanoi requer pelo menos três hastes")
        if not (0 <= start_peg < peg_count):
            raise ValueError("start_peg fora do intervalo de hastes")
        if not (0 <= goal_peg < peg_count):
            raise ValueError("goal_peg fora do intervalo de hastes")
        if start_peg == goal_peg:
            raise ValueError("start_peg e goal_peg devem ser diferentes")

        self.disks = disks
        self.peg_count = peg_count
        self.start_peg = start_peg
        self.goal_peg = goal_peg

        pegs = [tuple() for _ in range(peg_count)]
        pegs[start_peg] = tuple(range(disks, 0, -1))
        self.initial_state = HanoiState(tuple(pegs))

    def actions(self, state: State) -> list[Action]:
        if not isinstance(state, HanoiState):
            return []

        actions: list[Action] = []
        for source in range(self.peg_count):
            for target in range(self.peg_count):
                move = HanoiMove(source, target, self.peg_count)
                if move.apply(state) is not None:
                    actions.append(move)
        return actions

    def is_goal(self, state: State) -> bool:
        if not isinstance(state, HanoiState):
            return False
        if len(state.pegs) != self.peg_count:
            return False
        expected = tuple(range(self.disks, 0, -1))
        return (
            state.pegs[self.goal_peg] == expected
            and all(
                not state.pegs[index]
                for index in range(self.peg_count)
                if index != self.goal_peg
            )
        )
