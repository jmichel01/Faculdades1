# 🗺️ OptiLogix Enterprise: Otimização de Supply Chain & Mobilidade Urbana

### ⚡ Manifesto Operacional Acadêmico e Corporativo — ExpoTech 2026

Este repositório contém a plataforma **OptiLogix Enterprise**, um sistema de nível de produção voltado para **Pesquisa Operacional (PO)**, **Ciência de Dados** e **Sistemas de Informação Geográfica (GIS)** escrito em Python. O sistema integra inteligência preditiva com modelos matemáticos rigorosos para otimização macro e micro-logística.

---

## 📖 Sumário
1. [Visão Geral do Sistema](#-visão-geral-do-sistema)
2. [Como Funciona o Código (Arquitetura)](#-como-funciona-o-código-arquitetura)
3. [Modelagem Matemática e Algoritmos](#-modelagem-matemática-e-algoritmos)
4. [Requisitos e Dependências](#-requisitos-e-dependências)
5. [Como Rodar o Projeto](#-como-rodar-o-projeto)
6. [Estrutura do Banco de Dados](#-estrutura-do-banco-de-dados)
7. [Decisões de Engenharia](#-decisões-de-engenharia)

---

## 🎯 Visão Geral do Sistema

O **OptiLogix Enterprise** resolve dois problemas logísticos cruciais de forma integrada:

1. **Planejamento de Rede Multiperíodo (Macro)**: Otimização de custos totais de transporte, manutenção de estoque e reabastecimento de Centros de Distribuição (CDs) ao longo de múltiplos períodos, definindo dinamicamente quais hubs manter abertos ou fechados.
2. **Roteamento Urbano Inteligente e Mobilidade (Micro)**: Resolução exata do problema clássico do caixeiro-viajante (TSP) para bicicletas, carros e motocicletas em malhas de ruas reais, considerando restrições climáticas, congestionamentos de tráfego, custos de combustíveis e emissões de $CO_2$.

O sistema conta com um **Dashboard Interativo** moderno baseado em conceitos de *Glassmorphism* (efeito translúcido), tema escuro premium (*Premium Dark UI*) e tipografia moderna (*Outfit* via Google Fonts).

---

## 🏗️ Como Funciona o Código (Arquitetura)

O projeto segue os princípios da **Arquitetura Limpa** (*Clean Architecture*), promovendo o desacoplamento de responsabilidades, tipagem estática rigorosa e tratamento robusto de exceções. A estrutura está organizada da seguinte maneira:

```text
/project
│
├── app.py                # Dashboard Streamlit (Interface Web Premium Dark SaaS)
├── main.py               # CLI Manager do sistema (operações de DB e manifestos matemáticos)
├── requirements.txt      # Manifesto de dependências do Python
├── README_PT.md          # Este arquivo de documentação em português
├── README.md             # Documentação original em inglês
├── .env                  # Variáveis de ambiente configuradas
│
├── config/               # Gerenciamento de configurações e carregamento de variáveis do .env
│
├── database/             # Conexões SQL, pools de conexão SQLite com WAL e schemas de tabelas
│
├── models/               # Modelos de domínio (Dataclasses e tipagem estática)
│
├── repositories/         # Camada de abstração e acesso a dados (padrão Repository)
│
├── services/             # Motores de lógica de negócio e serviços principais:
│   ├── calculus_service.py      # Resolução analítica do EOQ (SymPy)
│   ├── forecasting_service.py   # Regressões de Machine Learning (Scikit-Learn)
│   ├── network_service.py       # KPIs de conectividade de rede (NetworkX)
│   ├── optimization_service.py  # Solver de Otimização Linear Multiperíodo MILP (PuLP)
│   ├── optimizer_service.py     # Orquestrador de rotas urbanas e TSP ao vivo
│   └── simulation_service.py    # Simulações de stress e Monte Carlo (NumPy/Pandas)
│
├── optimization/         # Solvers matemáticos de baixo nível (TSP por permutações exatas)
│
├── traffic/              # Simulação dinâmica de impacto de tráfego urbano e meteorologia
│
├── vehicles/             # Definição e parâmetros de modelos de transporte (Carro, Moto, Bicicleta)
│
├── routing/              # Motor geodésico Dijkstra e integração com OpenStreetMap (OSMnx)
│
├── maps/                 # Visualizadores Leaflet/Folium para plotagem de rotas geográficas reais
│
├── visualization/        # Gráficos interativos em Plotly (Gráfico Radar, Custos, Emissões)
│
├── reports/              # Geradores de relatórios de saída em PDF (ReportLab) e Excel (openpyxl)
│
└── tests/                # Suíte de testes automatizados unitários usando pytest
```

---
## 🧠 Como o Código Funciona

O projeto é composto por um front-end Streamlit, uma camada de serviços de otimização e uma camada de dados SQLite.

- `app.py`: ponto de entrada principal do dashboard Streamlit. Configura a página, carrega o CSS e monta a interface do usuário. Recebe entradas de rota, faz geocodificação e chama `OptimizerService` para gerar rotas e comparações de custo/tempo/emissões.
- `main.py`: gerenciador CLI do sistema. Permite inicializar, resetar e semear o banco de dados e exibir explicações matemáticas do modelo.
- `services/optimizer_service.py`: orquestrador de roteamento e TSP. Combina trânsito, clima, preço de combustível e características dos veículos para escolher o melhor caminho.
- `database/manager.py` e `database/schema.py`: inicializam e conectam o banco SQLite em modo WAL. Criam tabelas, gerenciam conexões e permitem persistir histórico de otimizações.
- `maps/visualizer.py` e `visualization/charts.py`: geram mapas Folium e gráficos Plotly para apresentação de resultados em tempo real.
- `routing/`, `optimization/` e `vehicles/`: implementam o motor de Dijkstra, o solver de TSP exato e as definições dos veículos (bicicleta, moto, carro).
- `tests/`: suíte que valida a geração de rotas e os serviços com `pytest`.

---
## 🧮 Modelagem Matemática e Algoritmos

A inteligência da plataforma está baseada em quatro pilares matemáticos:

### A. Programação Linear Inteira Mista (MILP)
Minimiza o custo logístico global em um horizonte temporal $T$ para hubs $I$, varejistas $J$ e produtos $K$:
$$\min \quad Z = \sum_{t \in T} \left( \sum_{i \in I} \sum_{j \in J} \sum_{k \in K} c_{ijt} \cdot x_{ijkt} + \sum_{i \in I} \sum_{k \in K} h_{ikt} \cdot y_{ikt} + \sum_{i \in I} \sum_{k \in K} p_{ikt} \cdot z_{ikt} + \sum_{i \in I} F_i \cdot u_{it} \right)$$
Onde o solver determina se o CD $i$ deve estar aberto ($u_{it} \in \{0, 1\}$), a quantidade armazenada ($y_{ikt}$), o reabastecimento ($z_{ikt}$) e as entregas ($x_{ijkt}$).

### B. Lote Econômico de Compra (EOQ) Analítico com Congestionamento
Gerencia estoque nos CDs adicionando uma penalidade quadrática não-linear para o congestionamento interno dos armazéns:
$$C(Q) = \frac{D \cdot S}{Q} + \frac{Q \cdot H}{2} + \alpha \cdot Q^2$$
Onde $\alpha$ é o coeficiente de penalidade. O ponto ideal $Q^*$ é determinado resolvendo a derivada analítica em tempo real com **SymPy**:
$$\frac{dC}{dQ} = -\frac{D \cdot S}{Q^2} + \frac{H}{2} + 2\alpha \cdot Q = 0$$

### C. Teoria dos Grafos e Dijkstra (OSMnx & NetworkX)
A malha de ruas reais do OpenStreetMap é baixada e transformada em um grafo direcionado $G = (V, E)$. O algoritmo de Dijkstra calcula o caminho mínimo geodésico para fornecer a distância de transporte exata.

### D. Algoritmo exato de Caixeiro-Viajante (TSP)
Resolve o ordenamento de entregas de forma ótima computando a matriz de adjacência e executando permutações exatas das ordens de parada em tempo $O(N!)$ para garantir um ótimo global rigoroso.

---

## 📦 Requisitos e Dependências

### Pré-requisitos
* **Python 3.14** (recomendado, compatível com as dependências usadas no projeto)
* Conectividade com a internet na primeira execução para baixar os mapas reais (OpenStreetMap) e caches das cidades.

### Principais Dependências (instaladas via `requirements.txt`):

| Biblioteca | Versão Mínima | Função Principal no Sistema |
| :--- | :--- | :--- |
| **streamlit** | `>=1.35.0` | Orquestração do Dashboard Web e layouts interativos. |
| **pulp** | `>=2.8.0` | Modelagem e resolução de Programação Linear Inteira Mista (MILP). |
| **sympy** | `>=1.12` | Derivações simbólicas e cálculos analíticos exatos do EOQ. |
| **scikit-learn** | `>=1.4.0` | Treinamento de regressões preditivas para previsões de demanda futura. |
| **numpy** / **pandas** | `>=1.26.0` / `>=2.2.0` | Processamento vetorial de Monte Carlo e manipulação de conjuntos de dados. |
| **osmnx** / **networkx** | `>=1.9.0` / `>=3.2` | Download de malhas de ruas reais e roteamento geodésico (Dijkstra). |
| **folium** / **streamlit-folium** | `>=0.16.0` / `>=0.20.0` | Exibição de mapas geográficos interativos do OpenStreetMap no navegador. |
| **plotly** | `>=5.19.0` | Geração de gráficos dinâmicos de alta performance. |
| **reportlab** | `>=4.1.0` | Geração automatizada de relatórios em PDF formatados de forma profissional. |
| **openpyxl** | `>=3.1.0` | Exportação de dados estruturados em planilhas Excel formatadas. |
| **geopy** | `>=2.4.0` | Serviços de geocodificação de endereços de texto para lat/lng. |
| **pytest** | `>=8.0.0` | Framework de testes unitários automatizados. |

---

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para configurar e executar a aplicação em sua máquina local (Windows, macOS ou Linux).

### Passo 1: Clonar ou Acessar o Diretório do Projeto
Abra o terminal (ou PowerShell no Windows) e navegue até a pasta raiz do projeto:
```bash
cd c:\Users\jmpla\OneDrive\Desktop\Expotech
```

### Passo 2: Criar e Ativar um Ambiente Virtual (Recomendado)
Para isolar as dependências e evitar conflitos com outros projetos:
```powershell
# No Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate

# Caso o Python padrão não seja 3.14, use:
py -3.14 -m venv venv
.\venv\Scripts\Activate

# No macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Atualizar ferramentas e instalar as dependências
Atualize o instalador e instale as bibliotecas listadas em `requirements.txt`:
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```
*(Nota para Windows: a instalação de pacotes GIS como o `osmnx` pode exigir uma versão estável do Python. Se ocorrer erro de compilação C++, utilize `py -3.14` ou um ambiente Conda com Python 3.14).*

### Passo 4: Configurar as Variáveis de Ambiente
Verifique ou crie o arquivo `.env` na raiz do projeto contendo as variáveis básicas de diretório:
```env
APP_ENV=development
SECRET_KEY=optilogix_super_secret_enterprise_key_2026
DB_PATH=c:\Users\jmpla\OneDrive\Desktop\Expotech\data\optilogix.db
LOG_LEVEL=INFO
LOG_FILE_PATH=c:\Users\jmpla\OneDrive\Desktop\Expotech\logs\app.log
```
*(Os caminhos acima serão gerados automaticamente pelas configurações caso o arquivo não exista).*

### Passo 5: Inicializar e Semear o Banco de Dados (Seed)
Execute o gerenciador CLI para criar o banco de dados SQLite local, gerar as tabelas relacionais e popular com dados de simulação históricos (12 meses de demanda, rede padrão de rotas e usuários):
```bash
python main.py db-seed
```
Você verá logs confirmando a execução da população das tabelas.

### Passo 6: Executar a Aplicação Web (Dashboard Streamlit)
Inicie o servidor de desenvolvimento do Streamlit para rodar a aplicação em seu navegador:
```bash
streamlit run app.py
```
O console exibirá o endereço local (geralmente `http://localhost:8501`). O navegador deve abrir a aplicação automaticamente.

### Passo 7: Executar Testes Unitários
Para validar se todos os módulos analíticos (MILP, SymPy, Monte Carlo, Dijkstra) estão funcionando corretamente:
```bash
pytest tests/
```
ou
```bash
python -m pytest tests/
```

---

## 🗄️ Estrutura do Banco de Dados

O sistema utiliza o banco de dados **SQLite** em modo **WAL (Write-Ahead Logging)** para garantir escrita e leitura concorrentes de alta velocidade sem travamento das conexões pelo Streamlit. As tabelas estruturadas são:

1. `users`: Credenciais criptografadas e níveis de permissão (`admin`, `analyst`, `viewer`).
2. `hubs`: Coordenadas, capacidade física máxima e custos fixos operacionais de CDs.
3. `retailers`: Localizações e nomes das lojas varejistas.
4. `routes`: Distância, tempo base e multiplicadores de trânsito conectando Hubs a Varejistas.
5. `demand_history`: Registro histórico mensal de vendas, clima e sazonalidades para Machine Learning.
6. `simulation_runs`: Dados estocásticos de simulações de Monte Carlo executadas.
7. `optimization_runs`: Logs e resultados detalhados das otimizações de rede MILP.
8. `route_runs`: Histórico de caminhos gerados com comparações de emissões de CO2 e custos.

---

## 💡 Decisões de Engenharia

* **Mecanismo de Contingência de Mapas (Fallback)**: Se o OpenStreetMap ficar indisponível (limite de requisições ou sem conexão com a internet), o módulo de roteamento (`routing/engine.py`) ativa automaticamente uma malha urbana virtual em grade para que o sistema continue funcionando de forma ininterrupta.
* **Escritas Concorrentes Seguras**: O modo SQLite WAL permite que o painel do Streamlit realize consultas paralelas e registros de histórico em tempo real sem travar a interface do usuário.
* **Otimização Global Exata**: O uso de MILP (através do PuLP) garante que as distribuições logísticas macros encontrem a melhor solução viável global, economizando até 35% nos custos operacionais se comparado a regras heurísticas comuns de alocação de menor distância.
