import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from search_lib import GraphSearch
from search_lib.problems import Direction, RobotGridProblem, RobotState


def print_separator(title: str = ""):
    if title:
        print(f"\n{'=' * 22} {title} {'=' * 22}")
    else:
        print("=" * 66)


def reconstruct_states(initial_state: RobotState, actions) -> list[RobotState]:
    states = [initial_state]
    current = initial_state
    for action in actions:
        res = action.apply(current)
        if res is not None:
            current = res[0]
            states.append(current)
    return states


DIRECTION_NAMES = {
    Direction.NORTH: "NORTE (cima ^)",
    Direction.EAST: "LESTE (direita >)",
    Direction.SOUTH: "SUL (baixo v)",
    Direction.WEST: "OESTE (esquerda <)",
}

ACTION_NAMES = {
    "L": "Giro Anti-horário (vira 90° à esquerda)",
    "R": "Giro Horário (vira 90° à direita)",
    "F": "Avançar 1 célula à frente",
    "B": "Marcha-ré (recua 1 célula para trás)",
}


def pause_prompt(message: str = "Pressione [ENTER] para continuar...") -> str:
    if not sys.stdin.isatty():
        return ""
    try:
        return input(f"\n> {message} ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "q"


def animate_path(problem: RobotGridProblem, initial_state: RobotState, actions):
    states = reconstruct_states(initial_state, actions)
    total_steps = len(actions)

    print("\n--- INÍCIO DA MOVIMENTAÇÃO DO ROBÔ ---")
    print(f"Estado Inicial: Posição {initial_state.position} | Visada: {DIRECTION_NAMES[initial_state.direction]}")
    print(problem.render(current_state=initial_state))

    for i, action in enumerate(actions, start=1):
        cmd = pause_prompt(f"[{i}/{total_steps}] Pressione ENTER para executar '{action}':")
        if cmd == "q":
            print("\n[Animação interrompida pelo usuário]")
            break

        current = states[i]
        act_desc = ACTION_NAMES.get(str(action), str(action))
        print(f"\nPasso {i}/{total_steps}: Ação [{action}] -> {act_desc}")
        print(f"Nova Posição: {current.position} | Visada: {DIRECTION_NAMES[current.direction]}")
        print(problem.render(current_state=current))

    if cmd != "q":
        print("\n[OK] O robô atingiu o objetivo com sucesso!")


def main():
    print_separator("1. CONFIGURAÇÃO DO AMBIENTE")
    map_size = (5, 5)
    initial_state = RobotState(0, 0, Direction.EAST)
    goal_position = (4, 2)
    obstacles = {(2, 0), (2, 1), (2, 2)}

    problem = RobotGridProblem(
        map_size=map_size,
        initial_state=initial_state,
        goal_position=goal_position,
        obstacles=obstacles,
    )

    print("Grid: 5x5 | Início: (0, 0) olhando LESTE | Objetivo: (4, 2)")
    print("Barreira de obstáculos: células (2, 0), (2, 1) e (2, 2)")
    print("\nMapa Inicial:")
    print("Legenda: [>] Robô | [G] Objetivo | [#] Obstáculo | [.] Livre")
    print(problem.render(current_state=initial_state))

    pause_prompt("Pressione ENTER para executar o algoritmo de Busca em Grafo (BFS)...")

    print_separator("2. BUSCA EM GRAFO (GraphSearch BFS) - BASELINE")
    result = GraphSearch(problem, mode="bfs").search(initial_state)

    if result.solution_node is None:
        print("Caminho não encontrado.")
        return

    path_actions = result.solution_node.get_path()
    print(f"Solução encontrada com {len(path_actions)} ações:")
    print(f"Sequência: {' '.join(str(a) for a in path_actions)}")

    pause_prompt("Pressione ENTER para iniciar a movimentação passo a passo do robô...")
    animate_path(problem, initial_state, path_actions)

    print_separator("3. MÉTRICAS DE DESEMPENHO DA BUSCA BASELINE")
    m = result.metrics
    print(f"  - Custo total:           {result.solution_node.cost}")
    print(f"  - Profundidade:          {result.solution_node.depth}")
    print(f"  - Nós expandidos:        {m.nodes_expanded}")
    print(f"  - Nós gerados:           {m.nodes_generated}")
    print(f"  - Tamanho máx fronteira: {m.max_frontier_size}")
    print(f"  - Tempo de execução:     {m.execution_time * 1000:.3f} ms")

    pause_prompt("Pressione ENTER para testar as variações de BLOQUEIO DE MOVIMENTO...")

    print_separator("4. LABORATÓRIO DE BLOQUEIOS E RESTRIÇÕES DE MOVIMENTO")
    print("Para testar a flexibilidade e forçar os limites da biblioteca, avaliamos 6 cenários:")

    scenarios = [
        {
            "id": "1",
            "title": "Baseline Completo (Sem restrições)",
            "desc": "Ações livres [F, L, R]. Menor custo ótimo padrão.",
            "kwargs": {},
            "problem": problem,
        },
        {
            "id": "2",
            "title": "Bloqueio Anti-horário (Sem 'L')",
            "desc": "Bloqueia giro à esquerda. Força sequências de 3 giros 'R' para virar à esquerda.",
            "kwargs": {"blocked_actions": ["ANTI_HORARIO"]},
        },
        {
            "id": "3",
            "title": "Bloqueio Horário (Sem 'R')",
            "desc": "Bloqueia giro à direita. Força sequências de 3 giros 'L' para virar à direita.",
            "kwargs": {"blocked_actions": ["HORARIO"]},
        },
        {
            "id": "4",
            "title": "Habilitar Marcha-Ré ('B')",
            "desc": "Adiciona ré [F, B, L, R]. Robô recua para manobrar economizando giros.",
            "kwargs": {"allowed_actions": ["FRENTE", "RE", "HORARIO", "ANTI_HORARIO"]},
        },
        {
            "id": "5",
            "title": "Proibido olhar para o OESTE",
            "desc": "Restrição cardeal: robô nunca pode apontar para o Oeste (vento/sensor).",
            "kwargs": {"blocked_directions": ["OESTE"]},
        },
        {
            "id": "6",
            "title": "Proibido olhar NORTE + Marcha-Ré",
            "desc": "Subir exige olhar Norte OU dar ré voltado para o Sul. A busca deduz ré!",
            "kwargs": {
                "blocked_directions": ["NORTE"],
                "allowed_actions": ["FRENTE", "RE", "HORARIO", "ANTI_HORARIO"],
            },
        },
        {
            "id": "7",
            "title": "Bloqueio Total de Rotação (Apenas 'F')",
            "desc": "Sem giros. Robô só translada no eixo X. Prova a completude: detecta impossibilidade.",
            "kwargs": {"blocked_actions": ["HORARIO", "ANTI_HORARIO"]},
        },
    ]

    results_table = []
    scenario_objects = {}

    for sc in scenarios:
        if "problem" in sc:
            sc_prob = sc["problem"]
        else:
            sc_prob = RobotGridProblem(
                map_size=map_size,
                initial_state=initial_state,
                goal_position=goal_position,
                obstacles=obstacles,
                **sc["kwargs"],
            )
        scenario_objects[sc["id"]] = (sc, sc_prob)

        res = GraphSearch(sc_prob, mode="bfs").search(initial_state)
        sol = res.solution_node
        if sol:
            cost_str = f"{sol.cost:.0f}"
            depth_str = f"{sol.depth}"
            status = "SUCESSO"
            path_str = " ".join(str(a) for a in sol.get_path())
        else:
            cost_str = "-"
            depth_str = "-"
            status = "SEM CAMINHO"
            path_str = "Insolúvel (Completude da busca comprovada)"

        results_table.append({
            "id": sc["id"],
            "title": sc["title"],
            "status": status,
            "cost": cost_str,
            "depth": depth_str,
            "exp": res.metrics.nodes_expanded,
            "gen": res.metrics.nodes_generated,
            "time_ms": f"{res.metrics.execution_time * 1000:.3f}",
            "path": path_str,
            "result": res,
        })

    # Imprimir tabela comparativa
    print("\nTABELA COMPARATIVA DE ESTRESSE DA BIBLIOTECA:")
    header = f"{'ID':<3} | {'Cenário de Restrição':<35} | {'Status':<11} | {'Custo':<5} | {'Exp':<5} | {'Ger':<5} | {'Tempo (ms)':<10}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for row in results_table:
        print(
            f"{row['id']:<3} | {row['title']:<35} | {row['status']:<11} | "
            f"{row['cost']:<5} | {row['exp']:<5} | {row['gen']:<5} | {row['time_ms']:<10}"
        )
    print("-" * len(header))

    print("\nANÁLISE DOS COMPORTAMENTOS OBSERVADOS:")
    for row in results_table:
        print(f"\n[{row['id']}] {row['title']}:")
        print(f"    Sequência de Ações: {row['path']}")
        if row["id"] == "2":
            print("    -> Nota: Onde o robô precisaria de 'L', a busca encontrou a tríade ótima 'R R R'.")
        elif row["id"] == "3":
            print("    -> Nota: Onde o robô precisaria de 'R', a busca encontrou a tríade ótima 'L L L'.")
        elif row["id"] == "6":
            print("    -> Nota: Proibido de olhar para o Norte, o robô virou para o Sul e subiu de marcha-ré!")
        elif row["id"] == "7":
            print("    -> Nota: Como o objetivo está na linha Y=2 e o robô só anda em Y=0, a busca encerra")
            print("             garantindo que não há solução (prova de completude da busca em grafo).")

    # Opção para animar qualquer cenário
    choice = pause_prompt("Digite o número do cenário (1-7) para animá-lo passo a passo, ou [ENTER] para continuar:")
    if choice in scenario_objects:
        selected_sc, selected_prob = scenario_objects[choice]
        selected_res = [r for r in results_table if r["id"] == choice][0]["result"]
        if selected_res.solution_node:
            print_separator(f"ANIMANDO CENÁRIO {choice}: {selected_sc['title']}")
            animate_path(selected_prob, initial_state, selected_res.solution_node.get_path())
        else:
            print(f"\n[Aviso] O Cenário {choice} é comprovadamente impossível, não há rota para animar.")

    print_separator("5. POR QUE BUSCA EM GRAFO É ESSENCIAL NO ROBÔ?")
    print("- No robô em grid existem ciclos infinitos: 4 giros no mesmo lugar retornam ao mesmo estado.")
    print("- Uma busca em árvore pura (Tree-DFS) ficaria presa em loop infinito.")
    print("- O GraphSearch mantém uma tabela de estados já visitados, garantindo término e optimalidade.")
    print_separator()


if __name__ == "__main__":
    main()
