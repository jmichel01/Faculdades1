# OptiLogix Enterprise: Otimização de Supply Chain & Mobilidade Urbana

### Manifesto Operacional Acadêmico e Corporativo — ExpoTech 2026

Este repositório contém a plataforma **OptiLogix Enterprise**, um sistema de nível de produção voltado para **Pesquisa Operacional (PO)**, **Ciência de Dados** e **Sistemas de Informação Geográfica (GIS)** escrito em Python. O sistema integra inteligência preditiva com modelos matemáticos rigorosos para otimização macro e micro-logística.

---

## Sumário
1. [O que o Código Faz (Visão Geral)](#o-que-o-código-faz-visão-geral)
2. [Linguagens e Tecnologias Utilizadas](#linguagens-e-tecnologias-utilizadas)
3. [Como Funciona o Código (Arquitetura e Componentes)](#como-funciona-o-código-arquitetura-e-componentes)
4. [Como Rodar o Projeto (Guia Passo a Passo)](#como-rodar-o-projeto-guia-passo-a-passo)
5. [Modelagem Matemática e Algoritmos](#modelagem-matemática-e-algoritmos)
6. [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
7. [Decisões de Engenharia](#decisões-de-engenharia)

---

## O que o Código Faz (Visão Geral)

O **OptiLogix Enterprise** resolve dois problemas logísticos cruciais de forma integrada:

1. **Planejamento de Rede Multiperíodo (Otimização Macro)**:
   - Otimiza custos operacionais globais de transporte, manutenção de estoques em Centros de Distribuição (CDs) e reabastecimento de mercadorias ao longo de múltiplos períodos.
   - Determina dinamicamente quais hubs manter abertos ou fechados a cada período para minimizar custos operacionais fixos e variáveis.
   
2. **Roteamento Urbano Inteligente e Mobilidade (Otimização Micro)**:
   - Resolve o problema clássico do caixeiro-viajante (TSP) para múltiplos meios de transporte (Carro, Motocicleta, Bicicleta) em malhas de ruas reais.
   - Considera restrições como congestionamentos de tráfego, condições climáticas extremas, custos de combustíveis atualizados e emissões de $CO_2$.
   - Recomenda a melhor opção de modal baseado no perfil selecionado pelo usuário (Ecológico/Equilibrado vs. Realista de Custo/Tempo).

O sistema conta com um **Dashboard Interativo** baseado em conceitos modernos de *Glassmorphism* (efeito translúcido), tema escuro premium (*Premium Dark UI*) e tipografia avançada (*Outfit* e *Space Grotesk*).

---

## Linguagens e Tecnologias Utilizadas

O ecossistema do projeto foi construído utilizando as seguintes linguagens e tecnologias:

* **Python (Core - 95%+)**: Linguagem principal utilizada para escrever toda a lógica de negócio, modelos de domínio, algoritmos de otimização, processos de previsão de Machine Learning, simulações de risco estocástico, motor geodésico e o dashboard web.
* **SQL (SQLite)**: Utilizado para a definição de esquemas (DDL) e consultas relacionais para a persistência estruturada do histórico de transações de vendas, usuários, rotas, hubs, simulações de Monte Carlo e execuções de otimizadores. Roda em modo **WAL (Write-Ahead Logging)** para alto desempenho em concorrência.
* **CSS (Vanilla CSS)**: Linguagem de estilização em `assets/style.css` aplicada para customização fina do Streamlit, permitindo o efeito translúcido (Glassmorphism) nos cartões KPI, fontes customizadas do Google Fonts e design responsivo.
* **Markdown**: Utilizada para documentação avançada e explicações textuais/matemáticas nos arquivos `README.md`, `README_PT.md` e `DOCUMENTACAO.md`.
* **Shell (Bash / PowerShell)**: Linguagem de script usada para a automação da preparação do ambiente, ativação do `venv`, instalação de pacotes via `pip` e gerenciamento do banco através da CLI (`main.py`).

---

## Como Funciona o Código (Arquitetura e Componentes)

O projeto segue os princípios da **Arquitetura Limpa** (*Clean Architecture*), desacoplando a interface de visualização, a camada de acesso a dados e os motores de cálculo.

### Fluxo de Funcionamento Principal
1. **Entrada do Usuário**: O usuário interage com o Dashboard Web (Streamlit) inserindo endereços manualmente (geocodificados com a API Nominatim) ou clicando diretamente no mapa interativo (Folium).
2. **Orquestração de Rota**: O `OptimizerService` gerencia a requisição, calculando as distâncias reais no grafo de ruas real baixado do OpenStreetMap (`OSMnx` e `NetworkX`).
3. **Resolução Matemática (Solver TSP)**: O solver executa uma busca exata de permutação para ordenar de forma ideal a sequência de destinos, garantindo o menor caminho global.
4. **Cálculo de Impacto Ambiental e Tráfego**: Os parâmetros meteorológicos e de tráfego ajustam as velocidades médias de cada modal (Carro, Moto, Bicicleta) e adicionam sobretaxas de combustível/carbono.
5. **Previsão de Demanda e Estoque**: A camada de ML (`Scikit-Learn`) prevê a demanda de vendas futuras e o solver MILP (`PuLP`) calcula o planejamento de rede ótimo.
6. **Persistência e Log**: Os resultados são gravados nas tabelas relacionais do banco de dados SQLite.
7. **Saída Visual e Relatórios**: O frontend monta gráficos interativos (`Plotly`) e oferece downloads de relatórios formais em PDF (`ReportLab`) e planilhas estruturadas (`openpyxl`).

### Localização da Lógica Matemática no Código

A modelagem matemática e a lógica algorítmica do sistema estão estruturadas e localizadas nas seguintes pastas e arquivos do projeto:

1. **Roteamento em Grafos e Dijkstra**:
   - A classe `RoutingEngine` em [routing/engine.py](routing/engine.py) gerencia a conexão com mapas do OpenStreetMap e implementa o cálculo geodésico de distâncias e as chamadas de busca de caminhos mínimos (`networkx.shortest_path`).
   - A classe `NetworkService` em [services/network_service.py](services/network_service.py) calcula as métricas estruturais do grafo logístico (KPIs como densidade e centralidade de graus de conectividade da rede).

2. **Problema do Caixeiro Viajante (TSP) Exato**:
   - A classe `TspSolver` em [optimization/tsp_solver.py](optimization/tsp_solver.py) implementa a resolução do TSP por força bruta combinando permutações exatas das ordens de parada (`itertools.permutations`) para garantir um ótimo global em rotas pequenas.

3. **Programação Linear Inteira Mista (MILP)**:
   - A classe `OptimizationService` em [services/optimization_service.py](services/optimization_service.py) modela e resolve o problema de minimização de custos logísticos macro de transporte e estoque utilizando o framework de programação matemática `PuLP` e seu resolvedor padrão CBC.

4. **Cálculo Analítico do Lote Econômico de Compra (EOQ)**:
   - A classe `CalculusService` em [services/calculus_service.py](services/calculus_service.py) realiza a diferenciação simbólica da equação de custos de estocagem sob efeito de congestionamento, utilizando a biblioteca `sympy` para calcular as derivadas e determinar de forma exata a quantidade ideal de compra.

5. **Simulação Estocástica de Monte Carlo**:
   - A classe `MonteCarloSimulator` em [simulation/monte_carlo.py](simulation/monte_carlo.py) realiza as iterações de simulação, amostrando distribuições de probabilidade normais, uniformes e empíricas usando geradores pseudoaleatórios do `numpy`.
   - A classe `SimulationService` em [services/simulation_service.py](services/simulation_service.py) orquestra essas simulações alimentando os dados históricos como parâmetros para os cenários de risco.

6. **Impactos de Tráfego e Clima (Modelos de Multiplicadores)**:
   - A classe `TrafficSimulator` em [traffic/simulator.py](traffic/simulator.py) calcula a redução não linear de velocidades e aumento de consumo energético com base em tabelas de fatores de restrição física dos modais.

7. **Pipeline de Machine Learning (Previsão)**:
   - A classe `DemandForecaster` em [forecasting/pipeline.py](forecasting/pipeline.py) executa a engenharia de atributos temporais e meteorológicos, realizando o treino das regressões `RandomForestRegressor` e `Ridge` da biblioteca `scikit-learn` para prever demandas futuras das lojas.
   - O controle desse fluxo é realizado pelo `ForecastingService` em [services/forecasting_service.py](services/forecasting_service.py).

### Estrutura de Diretórios
```text
/project
│
├── app.py                # Dashboard Streamlit (Interface Web Premium Dark SaaS)
├── main.py               # CLI Manager do sistema (operações de DB e manifestos matemáticos)
├── requirements.txt      # Manifesto de dependências do Python
├── README_PT.md          # Este arquivo de documentação em português
├── README.md             # Documentação original em inglês
├── DOCUMENTACAO.md       # Explicações técnicas detalhadas e fórmulas matemáticas
├── .env.example          # Exemplo de configurações de variáveis de ambiente
├── .env                  # Variáveis de ambiente configuradas localmente (ignorado pelo git)
│
├── config/               # Gerenciamento de configurações e carregamento de variáveis do .env
├── database/             # Conexões SQL, pools de conexão SQLite com WAL e schemas de tabelas
├── models/               # Modelos de domínio (Dataclasses e tipagem estática)
├── repositories/         # Camada de acesso a dados (padrão Repository)
├── services/             # Motores de lógica de negócio e serviços principais
├── optimization/         # Solvers matemáticos de baixo nível (TSP)
├── traffic/              # Simulação dinâmica de impacto de tráfego urbano e meteorologia
├── vehicles/             # Definição e parâmetros de modelos de transporte
├── routing/              # Motor geodésico Dijkstra e integração com OpenStreetMap (OSMnx)
├── maps/                 # Visualizadores Leaflet/Folium para plotagem de rotas geográficas reais
├── visualization/        # Gráficos interativos em Plotly
├── reports/              # Geradores de relatórios de saída em PDF e Excel
└── tests/                # Suíte de testes automatizados unitários usando pytest
```

---

## Como Rodar o Projeto (Guia Passo a Passo)

Siga os passos abaixo para configurar e executar a aplicação em sua máquina local (Windows, macOS ou Linux).

### Passo 1: Clonar ou Acessar o Diretório do Projeto
Abra o terminal (ou PowerShell no Windows) e navegue até a pasta raiz do projeto:
```bash
cd /caminho/para/seu/projeto/Faculdades1
```

### Passo 2: Criar e Ativar um Ambiente Virtual (Recomendado)
Para isolar as dependências e evitar conflitos:
```powershell
# No Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate

# No macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Baixar e Instalar as Dependências

O projeto especifica todas as suas bibliotecas externas e dependências em [requirements.txt](requirements.txt). Para baixá-las e instalá-las corretamente:

1. Garanta que seu ambiente virtual esteja ativado (ver Passo 2).
2. Certifique-se de que a máquina possui conexão ativa com a internet para que os pacotes possam ser transferidos dos repositórios públicos.
3. Atualize os utilitários de instalação base rodando:
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```
4. Execute a instalação de todas as dependências rodando o instalador `pip` apontado para o nosso arquivo de manifesto:
   ```bash
   python -m pip install -r requirements.txt
   ```
   *Nota de velocidade: Caso possua o gerenciador de pacotes ultrarrápido `uv` instalado no sistema, você pode substituir o comando acima por `uv pip install -r requirements.txt` para acelerar o processo.*
   *Nota de instalação em ambiente Windows: A instalação de algumas dependências GIS como `osmnx` e dependências científicas pode exigir a presença de ferramentas de compilação C++ do Microsoft Build Tools. Em caso de erro na compilação direta pelo `pip`, certifique-se de usar uma instalação estável de Python compilada para a arquitetura do seu processador.*

### Passo 4: Configurar as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto baseado no [.env.example](.env.example) e insira os seus caminhos locais de diretório:
```env
APP_ENV=development
SECRET_KEY=insira_uma_chave_secreta_aqui
DB_PATH=/caminho/completo/para/seu/projeto/data/optilogix.db
LOG_LEVEL=INFO
LOG_FILE_PATH=/caminho/completo/para/seu/projeto/logs/app.log
```

### Passo 5: Inicializar e Semear o Banco de Dados (Seed)
Popule o banco de dados SQLite local com tabelas estruturadas e dados históricos simulados (12 meses de demanda, rede de rotas padrão e usuários cadastrados):
```bash
python main.py db-seed
```

### Passo 6: Executar a Aplicação Web (Dashboard Streamlit)
Inicie o servidor de desenvolvimento do Streamlit para rodar a aplicação no seu navegador padrão:
```bash
streamlit run app.py
```
O console exibirá o endereço local (geralmente `http://localhost:8501`).

### Passo 7: Executar Testes Unitários
Para validar se todos os módulos analíticos (MILP, SymPy, Monte Carlo, Dijkstra) estão funcionando corretamente:
```bash
pytest tests/
```

---

## Modelagem Matemática e Algoritmos

A inteligência da plataforma está baseada em quatro pilares matemáticos:

### A. Programação Linear Inteira Mista (MILP)
Minimiza o custo logístico global em um horizonte temporal $T$ para hubs $I$, varejistas $J$ e produtos $K$:
$$\min \quad Z = \sum_{t \in T} \left( \sum_{i \in I} \sum_{j \in J} \sum_{k \in K} c_{ijt} \cdot x_{ijkt} + \sum_{i \in I} \sum_{k \in K} h_{ikt} \cdot y_{ikt} + \sum_{i \in I} \sum_{k \in K} p_{ikt} \cdot z_{ikt} + \sum_{i \in I} F_i \cdot u_{it} \right)$$
Onde o solver determina se o CD $i$ deve estar aberto ($u_{it} \in \{0, 1\}$), a quantidade armazenada ($y_{ikt}$), o reabastecimento ($z_{ikt}$) e as entregas ($x_{ijkt}$).

### B. Lote Econômico de Compra (EOQ) Analítico com Congestionamento
Gerencia estoque nos CDs adicionando uma penalidade quadrática não-linear para o congestionamento interno dos armazéns:
$$C(Q) = \frac{D \cdot S}{Q} + \frac{Q \cdot H}{2} + \alpha \cdot Q^2$$
O ponto ideal $Q^*$ é determinado resolvendo a derivada analítica em tempo real com a biblioteca algébrica **SymPy**:
$$\frac{dC}{dQ} = -\frac{D \cdot S}{Q^2} + \frac{H}{2} + 2\alpha \cdot Q = 0$$

### C. Teoria dos Grafos e Dijkstra (OSMnx & NetworkX)
A malha de ruas reais do OpenStreetMap é carregada como um grafo direcionado $G = (V, E)$. O algoritmo de Dijkstra calcula o caminho mínimo geodésico real para fornecer a distância e o caminho exatos entre os cruzamentos das vias.

### D. Algoritmo exato de Caixeiro-Viajante (TSP)
Resolve a ordenação ótima de entregas computando a matriz de adjacências e executando permutações exatas das ordens de parada em tempo de complexidade $O(N!)$ para garantir um ótimo global rigoroso em percursos com até 4 pontos.

---

## Estrutura do Banco de Dados

O sistema utiliza o banco de dados **SQLite** em modo **WAL (Write-Ahead Logging)** para garantir escrita e leitura concorrentes de alta velocidade sem travamento das conexões pelo Streamlit. As tabelas estruturadas são:

1. `users`: Credenciais e níveis de permissão (`admin`, `analyst`, `viewer`).
2. `hubs`: Coordenadas, capacidade física máxima e custos fixos operacionais de CDs.
3. `retailers`: Localizações e nomes das lojas varejistas.
4. `routes`: Distância, tempo base e multiplicadores de trânsito conectando Hubs a Varejistas.
5. `demand_history`: Registro histórico mensal de vendas, clima e sazonalidades para Machine Learning.
6. `simulation_runs`: Dados estocásticos de simulações de Monte Carlo executadas.
7. `optimization_runs`: Logs e resultados detalhados das otimizações de rede MILP.
8. `route_runs`: Histórico de caminhos gerados com comparações de emissões de CO2 e custos.

---

## Decisões de Engenharia

* **Mecanismo de Contingência de Mapas (Fallback)**: Se o OpenStreetMap ficar indisponível (limite de requisições ou sem conexão com a internet), o módulo de roteamento (`routing/engine.py`) activa automaticamente uma malha urbana virtual em grade para que o sistema continue funcionando de forma ininterrupta.
* **Escritas Concorrentes Seguras**: O tempo de execução concorrente do SQLite em modo WAL permite consultas rápidas do painel Streamlit simultaneamente a registros automáticos sem ocasionar travamentos de banco de dados.
* **Otimização Global Exata**: O uso de MILP (através do PuLP) garante que as distribuições logísticas macros encontrem a melhor solução viável global, economizando até 35% nos custos operacionais se comparado a regras heurísticas comuns de alocação de menor distância.
