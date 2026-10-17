# search_lib

Biblioteca desenvolvida para implementação e experimentação de algoritmos de busca em espaços de estados.

A `search_lib` fornece uma arquitetura modular para representar problemas, estados, ações e estratégias de busca. A estrutura permite adicionar novos problemas e algoritmos sem modificar o núcleo da biblioteca.

## Equipe

* **Erik Vinicius**
* **Kélven Alves**
* **João Pedro Araújo**
* **Matheus Bastos**

## Sobre o projeto

A biblioteca foi projetada para separar a representação de um problema da estratégia utilizada para solucioná-lo.

A arquitetura principal é composta por:

```text
Problem
├── State
├── Action
└── SearchStrategy
    └── SearchNode
```

Essa separação permite que diferentes problemas sejam executados utilizando diferentes algoritmos de busca.

## Objetivo do projeto

O projeto consiste em utilizar a biblioteca de busca já disponibilizada para
modelar e validar problemas clássicos de Inteligência Artificial. A equipe
reutilizou as abstrações existentes de `State`, `Action`, `Problem` e
`SearchStrategy`, implementando os problemas Torre de Hanoi, 8-Queens e Robô
em Grid sem duplicar a lógica dos algoritmos de busca.

Além dos problemas, foi consolidada a busca em grafo (`GraphSearch`) para lidar
com estados repetidos e ciclos, especialmente no Robô em Grid. Cada problema
possui estados imutáveis, ações válidas, teste de objetivo e exemplos de
execução parametrizáveis.

## Componentes principais

| Componente       | Responsabilidade                                                       |
| ---------------- | ---------------------------------------------------------------------- |
| `State`          | Representa uma configuração ou estado do problema.                     |
| `Action`         | Representa uma transformação entre estados.                            |
| `Problem`        | Define as regras do problema, suas ações, objetivo e heurística.       |
| `SearchNode`     | Representa um nó durante a busca e mantém o estado, pai, ação e custo. |
| `SearchStrategy` | Define a estrutura base para os algoritmos de busca.                   |

## `State`

Representa uma configuração do problema.

Um estado deve permitir **comparação e hash**, pois pode ser utilizado em estruturas como `set` e `dict`. Sempre que possível, sua representação interna deve utilizar estruturas imutáveis, como `tuple` ou `frozenset`.

## `Action`

Representa uma ação capaz de transformar um estado em outro.

O método `apply(state)` deve:

* receber o estado atual;
* retornar o novo estado quando a ação for válida;
* retornar `None` quando a ação não puder ser aplicada.

Ações não devem alterar diretamente o estado recebido.

## `Problem`

Representa as regras e características do problema de busca.

Toda implementação deve fornecer:

* `actions(state)` — retorna as ações válidas para o estado;
* `is_goal(state)` — verifica se o estado é um estado objetivo;
* `heuristic(state)` — fornece uma estimativa do custo restante, quando aplicável.

A classe `Problem` deve representar as regras do problema e não controlar o estado da busca. Informações como estados visitados devem ser responsabilidade da estratégia de busca.

## `SearchNode`

Representa um nó gerado durante a busca.

Cada nó mantém:

| Atributo | Responsabilidade                    |
| -------- | ----------------------------------- |
| `state`  | Estado representado pelo nó.        |
| `parent` | Nó que gerou o estado atual.        |
| `action` | Ação utilizada para gerar o nó.     |
| `cost`   | Custo acumulado desde o nó inicial. |

A relação entre `parent` e os nós permite reconstruir o caminho encontrado pela busca.

## `SearchStrategy`

Classe base para implementação dos algoritmos de busca.

Novos algoritmos devem estender `SearchStrategy` e utilizar a interface fornecida pelo núcleo da biblioteca.

Podem ser implementadas estratégias como:

* Busca em Largura (BFS);
* Busca em Profundidade (DFS);
* Busca de Custo Uniforme;
* Busca Gulosa;
* A*;
* IDA*;
* RBFS;
* Busca Bidirecional;
* Graph Search.

A estratégia de busca é responsável pelo controle da fronteira, dos estados explorados e das características específicas do algoritmo.


## Métricas

Estratégias utilizadas em experimentos podem coletar métricas para análise de desempenho, como:

| Métrica             | Descrição                              |
| ------------------- | -------------------------------------- |
| `nodes_expanded`    | Quantidade de nós expandidos.          |
| `max_frontier_size` | Maior tamanho atingido pela fronteira. |
| `execution_time`    | Tempo de execução do algoritmo.        |
| `cost`              | Custo da solução encontrada.           |

As métricas devem ser mantidas separadas da representação do problema.

## Adição de novos problemas

A implementação de um novo problema deve seguir a estrutura:

1. Criar uma implementação de `State` para representar suas configurações.
2. Criar as `Action` necessárias para representar suas transições.
3. Criar uma implementação de `Problem` contendo suas regras.
4. Implementar `actions()`, `is_goal()` e `heuristic()` quando aplicável.
5. Validar o problema utilizando uma ou mais implementações de `SearchStrategy`.

O novo problema deve ser compatível com as abstrações existentes, sem exigir alterações no núcleo da biblioteca.

## Boas práticas

* Estados utilizados em estruturas de busca devem possuir igualdade e hash consistentes.
* Prefira representações imutáveis para os estados.
* `Action.apply()` deve retornar `None` para ações inválidas.
* Ações não devem modificar diretamente o estado recebido.
* `Problem` não deve controlar estados visitados ou informações específicas da execução da busca.
* `actions(state)` deve ser determinístico para um mesmo estado, quando a natureza do problema permitir.
* A lógica do problema, o algoritmo de busca, as métricas e a visualização devem permanecer separados.
* Novas implementações devem utilizar as abstrações existentes em vez de duplicar funcionalidades do núcleo.

## Problemas-exemplo

Os problemas prontos ficam em `search_lib.problems` e podem ser usados com
qualquer estratégia compatível com a interface da biblioteca.

### Torre de Hanoi

`HanoiProblem(disks=3)` representa a configuração clássica com três hastes.
Os discos são armazenados em tuplas imutáveis, da base para o topo, e a
quantidade de discos pode ser alterada:

Cada estado contém as hastes e a ordem dos discos. Uma ação representa a
transferência do disco do topo de uma haste para outra. A ação é rejeitada
quando a haste de origem está vazia ou quando o movimento coloca um disco
maior sobre um disco menor. O objetivo é transferir todos os discos para a
haste final.

```python
from search_lib import GraphSearch
from search_lib.problems import HanoiProblem

problem = HanoiProblem(disks=3)
result = GraphSearch(problem).search(problem.initial_state)
```

Com custos unitários, a solução ótima para `n` discos possui `2**n - 1`
movimentos.

### Robô em grid

O estado do robô contém `x`, `y` e uma `Direction`. As ações padrão são giro
à esquerda, giro à direita e avanço. O conjunto de ações pode ser reduzido ou
reordenado por `allowed_actions`; obstáculos e uma direção final opcional
também podem ser configurados:

O avanço altera a posição somente quando a nova célula está dentro dos limites
do grid e não é um obstáculo. Os giros alteram apenas a direção do robô. O
objetivo pode exigir uma posição específica e, opcionalmente, uma direção
final. Como as ações permitem retornar a estados anteriores, a validação usa
busca em grafo para evitar ciclos.

```python
from search_lib import GraphSearch
from search_lib.problems import Direction, RobotGridProblem, RobotState

problem = RobotGridProblem(
    map_size=(5, 5),
    initial_state=RobotState(0, 0, Direction.EAST),
    goal_position=(4, 4),
    obstacles={(2, 2)},
    goal_direction=Direction.SOUTH,
)
result = GraphSearch(problem).search(problem.initial_state)
```

O uso de `GraphSearch` é recomendado porque giros e avanços permitem retornar
a estados anteriores.

### N-queens

`NQueensProblem(size=8)` posiciona uma rainha por linha e retorna qualquer
configuração completa sem conflitos de coluna ou diagonal. O tamanho é
parametrizável e instâncias sem solução, como `N=2` e `N=3`, retornam ausência
de solução.

O estado guarda as colunas ocupadas pelas rainhas já posicionadas. Em cada
passo, uma ação tenta colocar uma rainha na próxima linha. A ação é válida
somente quando não existe conflito de coluna ou de diagonal. O caso principal
do projeto é o 8-Queens, mas a implementação também permite testar outros
valores de `N`.

## Algoritmos e optimalidade

- `BFS`: busca em árvore; é completa e ótima para espaços de custo unitário,
  mas pode revisitar estados e entrar em ciclos.
- `DFS`: busca em árvore; é útil para obter uma solução, mas não garante
  optimalidade e pode não terminar em espaços com ciclos.
- `DLS`: DFS com limite de profundidade; a solução depende do limite fornecido.
- `GraphSearch`: BFS ou DFS com estados visitados; termina em espaços finitos.
  O modo BFS é ótimo quando todos os custos das ações são iguais.

## Testes e exemplos

Os problemas foram testados de forma estruturada com `unittest`, verificando
tanto as regras de cada domínio quanto o comportamento dos algoritmos:

* Hanoi: imutabilidade dos estados, movimentos inválidos e soluções ótimas
  para 1, 2 e 3 discos, incluindo os 7 movimentos do caso com 3 discos.
* Robô em Grid: limites do mapa, obstáculos, giros, ações configuráveis,
  objetivo com direção opcional e término correto em espaços com ciclos.
* 8-Queens: rejeição de conflitos, validade das configurações encontradas,
  uso de BFS/DFS/DLS e casos sem solução para `N=2` e `N=3`.
* Biblioteca: reconstrução dos caminhos, custos, profundidades, métricas e
  não repetição de estados na busca em grafo.

Execute toda a suíte automatizada com:

```text
python -m unittest discover -s tests -v
```

Execute os exemplos a partir da raiz do projeto:

```text
python examples/hanoi/run.py
python examples/robot_grid/run.py
python examples/n_queens/run.py
```

Também é possível escolher o problema a partir de um launcher único. Sem
argumentos, ele abre um menu interativo:

```text
python run.py
```

O mesmo menu também pode ser executado com `python examples/run.py`.

Ou escolha diretamente o problema, algoritmo e tamanho da instância:

```text
python examples/run.py hanoi --disks 4 --algorithm graph-bfs
python examples/run.py robot --grid-size 6 --algorithm graph-bfs
python examples/run.py queens --size 8 --algorithm dfs
```

Para busca em profundidade limitada, informe também `--depth-limit`.

Cada exemplo possui também um `experiment.py` que imprime métricas em formato
CSV para vários tamanhos de instância:

```text
python examples/hanoi/experiment.py
python examples/robot_grid/experiment.py
python examples/n_queens/experiment.py
```
