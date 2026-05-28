# Documentação Completa do Projeto: OptiLogix Enterprise & Smart Mobility

Esta documentação fornece uma explicação detalhada sobre a arquitetura do projeto **OptiLogix Enterprise**, os objetivos de negócio, as tecnologias empregadas e as formulações matemáticas que regem os motores de otimização logística, roteamento urbano e simulação estocástica.

---

## 1. A Ideia do Projeto

O **OptiLogix Enterprise** é uma plataforma profissional de Pesquisa Operacional (PO), Ciência de Dados e Sistemas de Informação Geográfica (GIS) voltada para o planejamento tático e operacional de cadeias de suprimentos (*supply chain*) e mobilidade urbana.

O sistema foi desenvolvido para resolver dois grandes problemas logísticos de forma integrada:
1. **Planejamento de Rede Multiperíodo (Macro)**: Determinar quais Centros de Distribuição (CDs) devem ficar abertos, quanto estoque manter e quanto reabastecer e enviar para os varejistas, minimizando os custos operacionais totais em um horizonte de tempo específico.
2. **Roteamento Urbano Inteligente e Mobilidade (Micro)**: Resolver o problema clássico do caixeiro-viajante (TSP) para veículos como bicicletas, carros e motocicletas, considerando condições dinâmicas de tráfego, condições meteorológicas e pegada de carbono ecológica.

---

## 2. Tecnologias e Linguagens Utilizadas

A fundação do projeto é totalmente construída em **Python**, integrada com uma arquitetura web leve e visualmente atraente para o dashboard de visualização. As tecnologias utilizadas incluem:

### Linguagens
* **Python 3.8+ (Core)**: Toda a lógica de negócio, modelos matemáticos, regressões, simulações e roteamento foram escritos em Python.
* **SQL (SQLite)**: Persistência relacional robusta. O banco de dados SQLite armazena o histórico de demanda, usuários, redes de rotas e históricos de execuções. A plataforma utiliza o modo **WAL (Write-Ahead Logging)** para permitir leituras e escritas concorrentes sem travamentos.
* **HTML/CSS (Vanilla)**: Utilizados na personalização visual do dashboard, implementando conceitos de *Glassmorphism* (efeito translúcido), fontes modernas (como a tipografia *Outfit* do Google Fonts) e layout escuro premium (*Premium Dark SaaS UI*).

### Principais Bibliotecas Python e Frameworks
* **Streamlit**: Orquestração e renderização da interface web rica.
* **PuLP**: Modelagem matemática de Programação Linear Inteira Mista (MILP).
* **SymPy**: Cálculo analítico e derivação simbólica do Lote Econômico de Compra (EOQ).
* **OSMnx & NetworkX**: Download e modelagem de grafos de ruas reais diretamente do OpenStreetMap para caminhos geodésicos baseados em Dijkstra.
* **Scikit-Learn**: Treinamento de modelos preditivos de Machine Learning (Ridge Regression e Random Forest).
* **Numpy & Pandas**: Processamento vetorial para simulações Monte Carlo e manipulação de séries temporais de dados históricos.
* **Plotly**: Geração de gráficos interativos (radar, evolução de custos, emissões de carbono).
* **Folium / Streamlit-Folium**: Renderização de mapas dinâmicos e captura de eventos de clique interativos.

---

## 3. O Cálculo e os Modelos Matemáticos

O projeto baseia-se em quatro pilares matemáticos rigorosos.

### A. Programação Linear Inteira Mista (MILP) - Otimização Macro
A otimização de custos e distribuição logística minimiza o custo operacional total ao longo de um horizonte planejado $T$, cobrindo hubs/CDs $I$, destinos/varejistas $J$, e produtos/commodities $K$.

#### Função Objetivo:
O objetivo é minimizar o custo total de transporte, manutenção de inventário, reposição de estoque e custo fixo de manutenção dos hubs:

$$\min \quad Z = \sum_{t \in T} \left( \sum_{i \in I} \sum_{j \in J} \sum_{k \in K} c_{ijt} \cdot x_{ijkt} + \sum_{i \in I} \sum_{k \in K} h_{ikt} \cdot y_{ikt} + \sum_{i \in I} \sum_{k \in K} p_{ikt} \cdot z_{ikt} + \sum_{i \in I} F_i \cdot u_{it} \right)$$

*Onde:*
* $x_{ijkt} \ge 0$: Quantidade do produto $k$ enviada do CD $i$ para o Varejista $j$ no período $t$.
* $y_{ikt} \ge 0$: Estoque final do produto $k$ mantido no CD $i$ no período $t$.
* $z_{ikt} \ge 0$: Quantidade de reabastecimento recebida pelo CD $i$ para o produto $k$ no período $t$.
* $u_{it} \in \{0, 1\}$: Variável binária que indica se o CD $i$ está aberto ($1$) ou fechado ($0$) no período $t$.
* $c_{ijt}$: Custo unitário de envio da rota do CD $i$ ao varejista $j$.
* $h_{ikt}$: Custo unitário de manutenção de estoque do produto $k$ no CD $i$.
* $p_{ikt}$: Custo unitário de reabastecimento do produto $k$ no CD $i$.
* $F_i$: Custo operacional fixo para manter o CD $i$ aberto.

#### Restrições:
1. **Satisfação de Demanda**: A soma das entregas de todos os CDs para o varejista $j$ deve satisfazer a demanda estimada $\hat{d}_{jkt}$:
   $$\sum_{i \in I} x_{ijkt} \ge \hat{d}_{jkt} \quad \forall j, k, t$$
2. **Equilíbrio de Estoque (Fluxo)**: O estoque no final de um período é igual ao estoque do período anterior, mais o reabastecimento, menos a quantidade despachada:
   $$y_{ikt} = y_{i,k,t-1} + z_{ikt} - \sum_{j \in J} x_{ijkt} \quad \forall i, k, t$$
3. **Capacidade do CD**: O estoque total armazenado no CD não pode exceder sua capacidade física máxima $C_i$, e o estoque só pode existir se o CD estiver aberto ($u_{it}=1$):
   $$\sum_{k \in K} y_{ikt} \le C_i \cdot u_{it} \quad \forall i, t$$
4. **Limite de Vazão de Rota**: A quantidade total de produtos enviados em uma rota não pode exceder o limite físico de capacidade de transporte $T_{ij}$:
   $$\sum_{k \in K} x_{ijkt} \le T_{ij} \quad \forall i, j, t$$

---

### B. Cálculo Contínuo e Lote Econômico de Compra (EOQ) com Congestionamento
Para gerenciar o estoque nos CDs de forma eficiente, a plataforma implementa uma variação analítica da equação de lote econômico clássico, introduzindo uma penalidade quadrática para congestionamento de armazenagem (quando o armazém fica muito cheio, custos logísticos internos crescem de forma não-linear).

A função de custo total $C(Q)$ é definida como:

$$C(Q) = \frac{D \cdot S}{Q} + \frac{Q \cdot H}{2} + \alpha \cdot Q^2$$

*Onde:*
* $Q$: Tamanho do lote de pedido (variável de decisão).
* $D$: Demanda anual/periódica estável.
* $S$: Custo de preparação/pedido (*setup cost*).
* $H$: Custo unitário de estocagem por unidade por período.
* $\alpha$: Coeficiente de penalidade de congestionamento físico do armazém.

Para encontrar o lote ideal $Q^*$ que minimiza os custos, derivamos a função de custo em relação a $Q$ e igualamos o resultado a zero:

$$\frac{dC}{dQ} = -\frac{D \cdot S}{Q^2} + \frac{H}{2} + 2\alpha \cdot Q = 0$$

Utilizando a biblioteca **SymPy**, o Python resolve essa equação polinomial cubicamente de forma algébrica exata, encontrando a única raiz real positiva $Q^*$ que representa o ponto de ótimo global.

---

### C. Teoria dos Grafos e Roteamento Geodésico (Dijkstra)
A rede de tráfego urbano é modelada como um grafo direcionado ponderado $G = (V, E)$, onde os vértices $V$ são cruzamentos de ruas e as arestas $E$ representam os segmentos de via física com pesos associados.

1. **Dijkstra Clássico**: O menor caminho e a distância real entre os pontos de entrega (origem e destinos) são calculados no grafo de ruas real baixado do OpenStreetMap através do algoritmo de Dijkstra:
   $$d(v) = \min_{u} [ d(u) + \text{peso}(u, v) ]$$
2. **Caixeiro Viajante (TSP)**: O motor computa uma matriz de distâncias de menor caminho entre todos os pontos selecionados e resolve de forma exata o problema do Caixeiro-Viajante analisando todas as permutações viáveis de visitação (para até 4 pontos de parada totais, totalizando $3! = 6$ rotas possíveis) para garantir a ordem global mais curta e eficiente:
   $$\min \sum_{i=0}^N \sum_{j=0}^N d_{ij} \cdot x_{ij}$$

---

### D. Influência de Congestionamento de Trânsito e Clima
A velocidade real e o consumo de combustível são calculados de forma dinâmica para cada tipo de veículo sob condições de trânsito e meteorologia simuladas:

1. **Tempo de Percurso Ajustado**:
   $$T(v) = \frac{\text{Distância}}{S_b(v) \cdot M_t(v, \text{trânsito}) \cdot M_w(v, \text{clima})}$$
   * $S_b(v)$: Velocidade base do veículo $v$.
   * $M_t$: Multiplicador de velocidade decorrente de tráfego (ex: carros caem para $0.25$ em horário de pico, enquanto bicicletas mantêm $0.90$).
   * $M_w$: Multiplicador climático (ex: motocicletas reduzem sua velocidade para $0.40$ sob tempestades por motivos de segurança).

2. **Consumo Ajustado de Combustível**:
   $$C_{adj}(v) = C_{base}(v) \cdot [1.0 + \Delta_{\text{trânsito}} + \Delta_{\text{clima}}]$$
   Reflete o desgaste do motor e o tempo ocioso em marcha lenta durante congestionamentos (engrenagem de *stop-and-go*).

---

### E. Previsão de Demanda com Machine Learning
Utilizando dados históricos de 12 meses anteriores de transações de vendas, meteorologia diária e feriados, a biblioteca **Scikit-Learn** treina modelos supervisionados para prever a demanda futura:
* **Modelos**: Ridge Regression (regressão linear regularizada contra sobreajuste) e Random Forest Regressor (ensemble de árvores de decisão).
* **Entradas (Features)**: Dia da semana, mês, sinalizador de feriado, código de clima.
* **Métricas**: $R^2$, MAE (Erro Médio Absoluto) e RMSE (Raiz do Erro Quadrático Médio).

---

### F. Simulação Estocástica de Monte Carlo (Análise de Risco)
Para prever e mitigar a resiliência da cadeia de suprimentos sob extrema volatilidade de mercado, o motor estocástico realiza centenas de rodadas independentes de simulações amostrando variáveis a partir de distribuições de probabilidade:
* **Demanda e Custos de Rota**: Seguem distribuições normais e triangulares baseadas nas volatilidades configuradas no perfil de risco (Pessimista, Realista, Otimista).
* **Métricas Estocásticas de Saída**: Custo Médio Projetado, Nível de Serviço Médio (probabilidade de atendimento total da demanda), Taxa de Ruptura de Estoque (*Stockout Rate*) e taxa de utilização de capacidade dos armazéns.
* **Intervalo de Confiança**: É calculado um intervalo de confiança de 95% para os custos operacionais agregados sob a premissa do teorema do limite central:
   $$\text{IC}_{95\%} = \mu \pm 1.96 \cdot \frac{\sigma}{\sqrt{N}}$$

---

## 4. Estrutura de Pastas e Organização do Código

A modularidade segue boas práticas de engenharia de software e arquitetura limpa:

* `/config`: Centralização de variáveis de ambiente, caminhos de pastas e constantes financeiras.
* `/database`: Lógica de gerenciamento de conexões SQL e schemas de tabelas.
* `/models`: Classes de representação de entidades de domínio (Dataclasses e tipagem estática).
* `/repositories`: Abstrações de leitura/escrita no banco de dados SQLite (padrão repository).
* `/services`: Motores analíticos (cálculo EOQ, IA de recomendação, solvers PuLP).
* `/optimization`: Solvers matemáticos puros (como o Caixeiro-Viajante / TSP Permutation).
* `/routing`: Pathfinder Dijksta e integração com o OpenStreetMap (OSMnx).
* `/visualization`: Funções gráficas usando Plotly para as métricas da dashboard.
* `/maps`: Visualizador Leaflet/Folium focado na plotagem de rotas geográficas reais.
* `/simulation`: Lógica estocástica pura de Monte Carlo (Numpy).
* `/forecasting`: Modelos preditivos de demanda (Scikit-Learn).
* `/tests`: Testes automatizados robustos (`pytest`).
