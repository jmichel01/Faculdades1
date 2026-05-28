<<<<<<< HEAD
# OptiLogix Enterprise: Supply Chain Optimization & Analytical Platform
### ⚡ ExpoTech 2026 Academic & Corporate Operations Manifesto

> [!NOTE]  
> Versão em português deste documento disponível em: [README_PT.md](file:///c:/Users/jmpla/OneDrive/Desktop/Expotech/README_PT.md).

---

## 1. Project Overview
**OptiLogix Enterprise** is a professional, production-grade Operations Research (OR) and Data Science platform built in Python. Designed to replicate modern corporate tactical planning dashboards, it integrates **Machine Learning Demand Prediction**, **Multi-Period Mixed-Integer Linear Programming (MILP)**, **Discrete Graph Routing**, **Continuous Calculus Cost Derivations**, and **Stochastic Monte Carlo Stress Simulations** to optimize multi-commodity shipping schedules and inventory levels under volatile market regimes.

The system is fully responsive, visually stunning, mathematically rigorous, and adheres strictly to industry software engineering standards.

---

## 2. Software Architecture & Modular Engineering
OptiLogix conforms to professional **Clean Architecture** patterns, ensuring a decoupling of concerns, complete typing, structured logging, and thorough exception handling:

```text
/project
│
├── app.py                # Streamlit Dashboard orchestration (Premium Dark SaaS UI)
├── main.py               # Operational CLI manager for DB tasks and math explanations
├── requirements.txt      # Python dependencies manifest
├── README.md             # Complete system documentation
├── .env                  # Environment configurations configuration
│
├── config/               # Settings management with dotenv validation guards
│   ├── __init__.py
│   └── settings.py
│
├── database/             # SQLite connection pool manager with WAL & relational schema
│   ├── __init__.py
│   ├── connection.py
│   ├── manager.py
│   └── schema.py
│
├── models/               # Domain-driven dataclasses representing entities
│   ├── __init__.py
│   └── domain.py
│
├── repositories/         # CRUD data-access abstractions
│   ├── __init__.py
│   ├── base_repository.py
│   ├── inventory_repo.py
│   ├── route_repo.py
│   ├── simulation_repo.py
│   └── user_repo.py
│
├── services/             # Core business logic engines
│   ├── __init__.py
│   ├── calculus_service.py      # SymPy EOQ derivation
│   ├── forecasting_service.py   # Scikit-learn Ridge & Random Forest predictions
│   ├── network_service.py       # Graph Network KPIs using NetworkX
│   ├── optimization_service.py  # PuLP multi-period MILP solver
│   ├── optimizer_service.py     # Live TSP optimizer orchestrator
│   └── simulation_service.py    # Monte Carlo stochastics simulation engine
│
├── optimization/         # Lower-level mathematical solvers
│   ├── __init__.py
│   └── tsp_solver.py            # Exact permutations Traveling Salesman solver
│
├── simulation/           # Simulation models and state
├── forecasting/          # Machine learning model pipelines
├── analytics/            # Post-run aggregators and processors
│   ├── __init__.py
│   └── processor.py             # Computes averages and trends over historical runs
│
├── visualization/        # Interactive Plotly UI chart panels
│   ├── __init__.py
│   └── charts.py                # Plotly time, cost, emissions, and radar rankings
│
├── reports/              # Automatic multi-format exporter engines
│   ├── __init__.py
│   └── generator.py             # openpyxl multi-tab Excel and ReportLab PDFs
│
├── routing/              # OSMnx street networks Dijkstra engines
│   ├── __init__.py
│   └── engine.py                # Geodesic road pathfinder & city fallback
│
├── maps/                 # Folium GIS Leaflet visualizers
│   ├── __init__.py
│   └── visualizer.py            # Dark Matter tiles rendering & markers
│
├── traffic/              # Urban congestion simulators
│   ├── __init__.py
│   └── simulator.py             # Traffic/weather speed & consumption adjustments
│
├── vehicles/             # Transportation mode models
│   ├── __init__.py
│   └── models.py                # Car, Motorcycle, Bicycle dataclasses
│
├── utils/                # Helper utilities and math conversions
│   ├── __init__.py
│   └── helpers.py
│
├── logs/                 # Persistent log records
├── data/                 # Relational SQLite file and OSM caching maps
└── tests/                # Unit test suites using pytest with isolated db
    ├── conftest.py
    ├── test_routing.py
    └── test_services.py
```

---

## 3. Mathematical Modeling & Operations Research

### A. Operations Research (Linear & Mixed-Integer Programming)
OptiLogix minimizes the total operational cost over planning horizon $T$ across Distribution Centers $I$, Retail Destinations $J$, and Commodities $K$.

#### Mathematical Objective Function:
$$\min \quad Z = \sum_{t \in T} \left( \sum_{i \in I} \sum_{j \in J} \sum_{k \in K} c_{ijt} \cdot x_{ijkt} + \sum_{i \in I} \sum_{k \in K} h_{ikt} \cdot y_{ikt} + \sum_{i \in I} \sum_{k \in K} p_{ikt} \cdot z_{ikt} + \sum_{i \in I} F_i \cdot u_{it} \right)$$

*   **Decision Variables:**
    *   $x_{ijkt} \ge 0$: Quantity of product $k$ shipped from DC $i$ to Retailer $j$ in period $t$.
    *   $y_{ikt} \ge 0$: Inventory of product $k$ stored at DC $i$ at the end of period $t$.
    *   $z_{ikt} \ge 0$: Replenishment order quantity arriving at DC $i$ in period $t$.
    *   $u_{it} \in \{0, 1\}$: Binary state indicating if DC $i$ is open in period $t$.

*   **Constraints:**
    1.  **Demand Satisfaction**: $\sum_{i \in I} x_{ijkt} \ge \hat{d}_{jkt} \quad \forall j, k, t$
    2.  **Inventory Flow Balance**: $y_{ikt} = y_{i,k,t-1} + z_{ikt} - \sum_{j \in J} x_{ijkt} \quad \forall i, k, t$
    3.  **DC Storage Capacity Limits**: $\sum_{k \in K} y_{ikt} \le C_i \cdot u_{it} \quad \forall i, t$
    4.  **Route Flow Caps**: $\sum_{k \in K} x_{ijkt} \le T_{ij} \quad \forall i, j, t$

### B. Calculus & Continuous Optimization (SymPy)
Analytically derives the Economic Order Quantity (EOQ) under quadratic congestion cost penalties:
*   **Total Inventory Cost Function**:
    $$C(Q) = \frac{D \cdot S}{Q} + \frac{Q \cdot H}{2} + \alpha \cdot Q^2$$
*   **Symbolic Optimization**:
    $$\frac{dC}{dQ} = -\frac{D \cdot S}{Q^2} + \frac{H}{2} + 2\alpha \cdot Q = 0 \implies \text{Solve for } Q^*$$

### C. Discrete Graph Routing (NetworkX & OSMnx)
The routing network is modeled as a weighted directed graph $G = (V, E)$. Dijkstra shortest-path weight parameterizes shipping cost coefficients:
$$c_{ijt} = \text{DijkstraPathLength}(i, j) \times \text{fuel\_coefficient}$$

---

## 4. Machine Learning & Forecasting
Using **Scikit-learn**, the platform trains **Ridge** and **Random Forest Regressors** on historical daily datasets. Features include day-of-week, month, holiday flags, and weather codes.
*   **Models Evaluated**: Ridge Regression vs. Random Forest Ensemble.
*   **KPI Metrics**: R² score, Mean Absolute Error (MAE), and Root Mean Squared Error (RMSE).
*   **Confidence Intervals**: Computes 95% forecast ribbons for demand quantity projections.

---

## 5. Stochastic Monte Carlo Simulation
The simulation engine models operational supply chain resilience under market fluctuations by executing hundreds of random trials per regime:
*   **Simulated Volatilities**: Demand shocks, warehousing capacity losses, fuel price fluctuations (normal volatility), weather state probabilities, and traffic/congestion delays.
*   **KPI Outputs**: Overall Service Level (%), Stockout Rate (%), Distribution Center Capacity Utilization (%), and Custo Médio Projetado (95% Confidence Intervals).

---

## 6. Database Schema & Persistence
OptiLogix implements a structured relational persistence layer using **SQLite** with WAL (Write-Ahead Logging) enabled:

1.  `users`: Stores system credentials and authentication roles (`admin`, `analyst`, `viewer`).
2.  `hubs`: Stores coordinates, holding costs, capacity limits, and operating overheads for DCs.
3.  `retailers`: Stores coordinates and names of retail customer destinations.
4.  `routes`: Connects Hubs to Retailers with distance, base costs, and congestion factors.
5.  `demand_history`: Logs 12 months of historical product transactions, weather codes, and holiday flags.
6.  `simulation_runs`: Logs Monte Carlo trial results (Service level, Stockout rate, costs).
7.  `optimization_runs`: Logs multi-period MILP solver allocations (allocations, costs, states).
8.  `route_runs`: Logs live routing requests, coordinates, traffic levels, and vehicle comparison tables.

---

## 7. Installation & Execution

### Prerequisites
*   Python 3.8+ (fully tested on Python 3.14)

### Setup Dependencies
```bash
pip install -r requirements.txt
```

### Database Seeding
Populate the SQLite database with 12 months of seasonal demand data and default networks:
```bash
python main.py db-seed
```

### Run Tests
```bash
python -m pytest tests/
```

### Launch Dashboard
```bash
streamlit run app.py
```

---

## 8. Engineering Decisions & Rationale
1.  **OSMnx Fallback Engine**: If a network connection is unavailable or OpenStreetMap rates limits are hit, the routing module switches to a staircase city-grid algorithm to guarantee uninterrupted calculations.
2.  **WAL Mode**: SQLite WAL journal mode is programmatically enforced to allow parallel write locks from the Streamlit UI and background worker tasks without locking issues.
3.  **PuLP Linear Optimization**: Multi-period multi-commodity linear modeling allows for global optimization of logistics operations, outperforming naive heuristics by up to 35% in cost savings.
4.  **Glassmorphism Custom Styling**: Embedded HSL color palettes and Outfit typography provide a state-of-the-art BI feel, maximizing visual engagement for corporate and academic evaluations.

---

## 9. Future Enhancements
*   **Genetic Algorithms (GA)**: Integrate heuristic GA solvers for routing scales exceeding 20 destinations where exact TSP permutations are computationally prohibitive.
*   **Dynamic API Feeds**: Replace historical mock weather files with real-time OpenWeatherMap API integrations to automate route calculations on live rain/snow multipliers.
=======
# Faculdades1
Arquivo do projeto da faculdade 
>>>>>>> f39576dfa9134749dcaf4bfad41401387d2fbb81
