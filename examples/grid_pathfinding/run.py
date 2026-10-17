import os
import sys

# Garante que o Python encontra a pasta raiz do projeto e o arquivo problem.py
DIR_ATUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.abspath(os.path.join(DIR_ATUAL, "../.."))

if DIR_ATUAL not in sys.path:
    sys.path.insert(0, DIR_ATUAL)
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)

from search_lib import BFS, DFS
from problem import GridPathfinding


def main():
    # Caminho do arquivo de mapa
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_path = os.path.join(current_dir, "map.txt")

    # Carrega o problema da malha via arquivo
    problema = GridPathfinding(file=map_path)

    print("=== BUSCA EM LARGURA (BFS) ===")
    resultado_bfs = BFS(problema).search(problema.initial_state)

    if resultado_bfs.solution_node:
        caminho = resultado_bfs.solution_node.get_path()
        node = resultado_bfs.solution_node
        print(f"Sucesso BFS!")
        print(f" -> Custo Total: {node.cost}")
        print(f" -> Profundidade (Depth): {node.depth}")
        print(f" -> Passos no caminho ({len(caminho)}):")
        for passo in caminho:
            print(f"    {passo}")
    else:
        print("Caminho não encontrado.")

    print("\n--- Métricas da Busca (BFS) ---")
    m = resultado_bfs.metrics
    print(f"Nós Expandidos:          {m.nodes_expanded}")
    print(f"Nós Gerados:             {m.nodes_generated}")
    print(f"Tamanho Máx. Fronteira:  {m.max_frontier_size}")
    print(f"Tempo de Execução:       {m.execution_time * 1000:.3f} ms")

    print("\n" + "="*40 + "\n")

    # === BUSCA EM PROFUNDIDADE (DFS) ===
    # NOTA: O DFS em versão árvore (sem controlo de estados visitados/fechados)
    # pode entrar em ciclo infinito na malha devido a movimentos reversíveis (ex: CIMA -> BAIXO).
    # Para testar o DFS com segurança, descomente o bloco abaixo consciente desta limitação:
    
    """
    print("=== BUSCA EM PROFUNDIDADE (DFS) ===")
    resultado_dfs = DFS(problema).search(problema.initial_state)
    if resultado_dfs.solution_node:
        print(f"Sucesso DFS! Custo: {resultado_dfs.solution_node.cost}")
    """


if __name__ == "__main__":
    main()