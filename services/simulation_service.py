import logging
import numpy as np
from typing import Dict, Any, List
from models.domain import SimulationRun
from repositories.inventory_repo import InventoryRepository
from repositories.route_repo import RouteRepository
from repositories.simulation_repo import SimulationRepository
from services.forecasting_service import ForecastingService
from simulation.monte_carlo import MonteCarloSimulator

logger = logging.getLogger("optilogix.service.simulation")

class SimulationService:
    def __init__(self) -> None:
        self.inventory_repo = InventoryRepository()
        self.route_repo = RouteRepository()
        self.simulation_repo = SimulationRepository()
        self.forecasting_service = ForecastingService()

    def run_monte_carlo_simulation(self, scenario_type: str, trials: int = 50) -> Dict[str, Any]:
        logger.info(f"Running Monte Carlo Simulation under scenario: {scenario_type} ({trials} trials)...")
        
        hubs = self.inventory_repo.list_hubs()
        retailers = self.inventory_repo.list_retailers()
        routes = self.route_repo.list_routes()
        products = ["PROD001", "PROD002"]
        
        if not hubs or not retailers:
            raise ValueError("Incomplete database. Ensure hubs and retailers are seeded.")

        base_capacities = np.array([h.capacity for h in hubs])
        base_holding_costs = np.array([h.holding_cost for h in hubs])
        base_route_costs = np.array([r.base_cost * r.congestion_factor for r in routes])
        hubs_fixed_costs = [h.fixed_cost for h in hubs]

        base_demands_list = []
        for r in retailers:
            for p in products:
                forecast = self.forecasting_service.forecast_demand(r.id, p, 1)[0]["forecast"]
                base_demands_list.append(forecast)
                
        base_demands = np.array(base_demands_list)

        res = MonteCarloSimulator.run_simulation(
            scenario_type=scenario_type,
            trials=trials,
            base_capacities=base_capacities,
            base_holding_costs=base_holding_costs,
            base_route_costs=base_route_costs,
            base_demands=base_demands,
            hubs_fixed_costs=hubs_fixed_costs
        )

        db_run = SimulationRun(
            id=None,
            timestamp=None,
            scenario_type=scenario_type,
            demand_multiplier=res["demand_multiplier"],
            cost_multiplier=res["cost_multiplier"],
            total_cost=round(res["mean_cost"], 2),
            service_level=round(res["mean_service"], 4),
            stockout_rate=round(res["mean_stockout"], 4),
            avg_utilization=round(res["mean_utilization"], 4)
        )
        self.simulation_repo.save_simulation_run(db_run)

        return {
            "scenario": scenario_type,
            "trials_run": trials,
            "costs": {
                "mean": round(res["mean_cost"], 2),
                "std": round(res["std_cost"], 2),
                "ci_95_lower": round(res["ci_lower"], 2),
                "ci_95_upper": round(res["ci_upper"], 2),
                "raw_series": [round(float(c), 2) for c in res["costs_out"]]
            },
            "service_level": round(res["mean_service"] * 100, 2),
            "stockout_rate": round(res["mean_stockout"] * 100, 2),
            "avg_utilization": round(res["mean_utilization"] * 100, 2),
            "avg_fuel_price": round(res["avg_fuel_price"], 2),
            "weather_frequencies": res["weather_freqs"],
            "traffic_frequencies": res["traffic_freqs"],
            "avg_traffic_delay_pct": round(res["avg_traffic_delay_pct"], 1),
            "sim_fuel_prices": [round(float(p), 2) for p in res["sim_fuel_prices"]],
            "sim_vehicle_times": res["sim_vehicle_times"],
            "sim_vehicle_costs": res["sim_vehicle_costs"],
            "sim_vehicle_co2": res["sim_vehicle_co2"]
        }
#A
