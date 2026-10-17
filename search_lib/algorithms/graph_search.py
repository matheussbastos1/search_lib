from collections import deque
import time

from search_lib.core import (
    Problem,
    SearchMetrics,
    SearchNode,
    SearchResult,
    SearchStrategy,
    State,
)


class GraphSearch(SearchStrategy):
    """Busca em grafo com fronteira FIFO (BFS) ou LIFO (DFS).

    Cada estado é marcado como visitado no momento em que é gerado. Assim,
    estados repetidos não entram novamente na fronteira e ciclos não impedem
    a conclusão da busca em espaços finitos.
    """

    MODES = ("bfs", "dfs")

    def __init__(self, problem: Problem, mode: str = "bfs"):
        super().__init__(problem)
        if mode not in self.MODES:
            raise ValueError(f"mode deve ser um de {self.MODES}, recebido: {mode!r}")
        self.mode = mode

    def search(self, initial_state: State) -> SearchResult:
        start_time = time.perf_counter()
        metrics = SearchMetrics()

        root = SearchNode(initial_state)
        frontier = deque([root])
        visited = {initial_state}
        metrics.nodes_generated = 1
        metrics.max_frontier_size = 1

        while frontier:
            node = frontier.popleft() if self.mode == "bfs" else frontier.pop()
            metrics.nodes_expanded += 1

            if self.problem.is_goal(node.state):
                metrics.execution_time = time.perf_counter() - start_time
                return SearchResult(solution_node=node, metrics=metrics)

            for action in self.problem.actions(node.state):
                result = action.apply(node.state)
                if result is None:
                    continue

                next_state, action_cost = result
                if next_state in visited:
                    continue

                visited.add(next_state)
                child = SearchNode(
                    state=next_state,
                    parent=node,
                    action=action,
                    cost=node.cost + action_cost,
                )
                metrics.nodes_generated += 1
                frontier.append(child)
                metrics.max_frontier_size = max(metrics.max_frontier_size, len(frontier))

        metrics.execution_time = time.perf_counter() - start_time
        return SearchResult(solution_node=None, metrics=metrics)
