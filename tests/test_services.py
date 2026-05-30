import pytest
from database.schema import DatabaseSchemaManager
from utils.mock_data_generator import MockDataGenerator
from services.calculus_service import CalculusService
from services.forecasting_service import ForecastingService
from services.simulation_service import SimulationService
from services.optimization_service import OptimizationService
from services.network_service import NetworkService

@pytest.fixture(scope="module", autouse=True)
def seed_test_database() -> None:
    DatabaseSchemaManager.init_database()
    MockDataGenerator.generate_and_seed()


def test_calculus_service() -> None:
    service = CalculusService()
    res = service.solve_optimal_order_quantity(
        demand=5000.0,
        setup_cost=200.0,
        holding_cost=10.0,
        congestion_coef=0.005
    )
    
    assert res["optimal_q"] > 0
    assert res["min_cost"] > 0
    assert "latex_cost_function" in res
    assert "latex_derivative" in res
    
    assert res["optimal_q"] < 447.21


def test_forecasting_service() -> None:
    service = ForecastingService()
    retailer_id = "RET_NYC"
    product_id = "PROD001"
    
    metrics = service.train_and_evaluate(retailer_id, product_id)
    assert "ridge" in metrics
    assert "random_forest" in metrics
    assert "r2" in metrics["random_forest"]
    assert "mae" in metrics["random_forest"]
    
    forecasts = service.forecast_demand(retailer_id, product_id, horizon_days=5)
    assert len(forecasts) == 5
    for f in forecasts:
        assert "date" in f
        assert f["forecast"] > 0.0
        assert f["lower_bound"] <= f["forecast"]
        assert f["upper_bound"] >= f["forecast"]


def test_optimization_service() -> None:
    service = OptimizationService()
    
    res_lp = service.run_network_optimization(planning_days=2)
    assert res_lp["solver_status"] == "Optimal"
    assert res_lp["total_cost"] > 0
    assert len(res_lp["shipments"]) >= 0
    assert len(res_lp["hub_states"]) > 0
    
    res_heur = service.run_heuristic_nearest_allocation(planning_days=2)
    assert res_heur["total_cost"] > 0
    assert len(res_heur["shipments"]) > 0


def test_simulation_service() -> None:
    service = SimulationService()
    
    res = service.run_monte_carlo_simulation(scenario_type="Pessimistic", trials=10)
    assert res["scenario"] == "Pessimistic"
    assert res["trials_run"] == 10
    assert "costs" in res
    assert res["service_level"] > 0.0
    assert res["stockout_rate"] >= 0.0
    assert len(res["costs"]["raw_series"]) == 10
    
    assert "avg_fuel_price" in res
    assert "weather_frequencies" in res
    assert "traffic_frequencies" in res
    assert "avg_traffic_delay_pct" in res
    assert "sim_fuel_prices" in res
    assert "sim_vehicle_times" in res
    assert "sim_vehicle_costs" in res
    assert "sim_vehicle_co2" in res
    assert len(res["sim_fuel_prices"]) == 10
    assert "Carro" in res["sim_vehicle_times"]
    assert len(res["sim_vehicle_times"]["Carro"]) == 10


def test_network_service() -> None:
    service = NetworkService()
    
    kpis = service.calculate_network_kpis()
    assert kpis["node_count"] == 14
    assert kpis["edge_count"] == 40
    assert kpis["density"] > 0.0
    assert kpis["is_weakly_connected"] is True
    
    path, cost = service.get_shortest_path("HUB_ATL", "RET_MIA")
    assert path[0] == "HUB_ATL"
    assert path[-1] == "RET_MIA"
    assert cost > 0.0
#A
