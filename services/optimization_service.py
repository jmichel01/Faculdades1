import logging
import json
from datetime import datetime, date
from typing import Dict, Any, List, Tuple
import pulp
from repositories.inventory_repo import InventoryRepository
from repositories.route_repo import RouteRepository
from repositories.simulation_repo import SimulationRepository
from services.forecasting_service import ForecastingService
from services.network_service import NetworkService
from models.domain import OptimizationRun

logger = logging.getLogger("optilogix.service.optimization")

class OptimizationService:
    """
    Applies Operations Research techniques (Linear and Mixed-Integer Programming).
    Orchestrates supply chain network optimization using the PuLP framework.
    """
    def __init__(self) -> None:
        self.inventory_repo = InventoryRepository()
        self.route_repo = RouteRepository()
        self.simulation_repo = SimulationRepository()
        self.forecasting_service = ForecastingService()
        self.network_service = NetworkService()

    def run_network_optimization(self, planning_days: int = 3) -> Dict[str, Any]:
        """
        Executes a multi-period, multi-commodity cost minimization optimization problem.
        Uses mixed integer programming to optimize routing, holding, and fixed-DC costs.
        """
        logger.info("Initializing PuLP logistics optimization problem...")
        
        # 1. Load network components
        hubs = self.inventory_repo.list_hubs()
        retailers = self.inventory_repo.list_retailers()
        routes = self.route_repo.list_routes()
        products = ["PROD001", "PROD002"]
        periods = list(range(1, planning_days + 1))
        
        if not hubs or not retailers or not routes:
            raise ValueError("Incomplete logistics database. Ensure hubs, retailers, and routes are seeded.")

        # Re-build route lookup maps
        route_costs = {}
        route_caps = {}
        for r in routes:
            route_costs[(r.origin_id, r.destination_id)] = r.base_cost * r.congestion_factor
            route_caps[(r.origin_id, r.destination_id)] = 250.0  # Dynamic route shipping limit

        # 2. Query demand forecasts for all retailers and products across periods
        forecasts = {}
        for r in retailers:
            for p in products:
                # Get forecasts for the planning horizon
                f_list = self.forecasting_service.forecast_demand(r.id, p, planning_days)
                for t_idx, f in enumerate(f_list):
                    t = t_idx + 1
                    forecasts[(r.id, p, t)] = f["forecast"]

        # Starting inventory levels (t=0)
        init_inventory = {}
        for h in hubs:
            for p in products:
                init_inventory[(h.id, p)] = 10.0  # Start with safety stock level to guarantee holding costs

        # 3. Instantiate PuLP Model
        prob = pulp.LpProblem("OptiLogix_SupplyChain_MinCost", pulp.LpMinimize)

        # 4. Decision Variables
        # Shipments: x[i, j, k, t] (continuous)
        x = pulp.LpVariable.dicts(
            "Ship",
            ((h.id, r.id, p, t) for h in hubs for r in retailers for p in products for t in periods),
            lowBound=0,
            cat=pulp.LpContinuous
        )
        
        # End-of-period Inventory: y[i, k, t] (continuous)
        y = pulp.LpVariable.dicts(
            "Inv",
            ((h.id, p, t) for h in hubs for p in products for t in list(range(0, planning_days + 1))),
            lowBound=0,
            cat=pulp.LpContinuous
        )
        
        # Procurement: z[i, k, t] (continuous)
        z = pulp.LpVariable.dicts(
            "Proc",
            ((h.id, p, t) for h in hubs for p in products for t in periods),
            lowBound=0,
            cat=pulp.LpContinuous
        )
        
        # DC Operating state: u[i, t] (binary)
        u = pulp.LpVariable.dicts(
            "DCActive",
            ((h.id, t) for h in hubs for t in periods),
            cat=pulp.LpBinary
        )

        # Set initial inventory variables to constants
        for h in hubs:
            for p in products:
                prob += y[(h.id, p, 0)] == init_inventory[(h.id, p)]

        # 5. Objective Function Components
        # Cost parameters
        procurement_cost_rates = {"PROD001": 100.0, "PROD002": 200.0}
        
        transport_cost_term = pulp.lpSum(
            route_costs.get((h.id, r.id), 999.0) * x[(h.id, r.id, p, t)]
            for h in hubs for r in retailers for p in products for t in periods
        )
        
        holding_cost_term = pulp.lpSum(
            h.holding_cost * y[(h.id, p, t)]
            for h in hubs for p in products for t in periods
        )
        
        procurement_cost_term = pulp.lpSum(
            procurement_cost_rates[p] * z[(h.id, p, t)]
            for h in hubs for p in products for t in periods
        )
        
        dc_fixed_cost_term = pulp.lpSum(
            h.fixed_cost * u[(h.id, t)]
            for h in hubs for t in periods
        )

        # Total Cost Objective
        prob += transport_cost_term + holding_cost_term + procurement_cost_term + dc_fixed_cost_term

        # 6. Constraints
        # a. Demand Satisfaction
        for r in retailers:
            for p in products:
                for t in periods:
                    prob += pulp.lpSum(x[(h.id, r.id, p, t)] for h in hubs) >= forecasts[(r.id, p, t)]

        # b. Inventory Balance
        for h in hubs:
            for p in products:
                for t in periods:
                    prob += y[(h.id, p, t)] == y[(h.id, p, t-1)] + z[(h.id, p, t)] - pulp.lpSum(x[(h.id, r.id, p, t)] for r in retailers)

        # c. Warehouse Storage Capacity
        for h in hubs:
            for t in periods:
                prob += pulp.lpSum(y[(h.id, p, t)] for p in products) <= h.capacity * u[(h.id, t)]

        # d. Route Shipments Limit
        for h in hubs:
            for r in retailers:
                for t in periods:
                    prob += pulp.lpSum(x[(h.id, r.id, p, t)] for p in products) <= route_caps.get((h.id, r.id), 250.0)

        # e. Safety Stock Constraint (forces positive holding cost and immediate procurement replenishment)
        for h in hubs:
            for p in products:
                for t in periods:
                    prob += y[(h.id, p, t)] >= 10.0

        # 7. Solve
        # We use PuLP's default solver (CBC or Highs if configured)
        solver = pulp.PULP_CBC_CMD(msg=False)
        status = prob.solve(solver)
        
        solver_status = pulp.LpStatus[status]
        logger.info(f"PuLP Solver completed with status: {solver_status}")

        if solver_status != "Optimal":
            raise RuntimeError(f"Operations Research solver failed to find optimal allocation: {solver_status}")

        # 8. Extract optimization metrics
        total_cost_val = pulp.value(prob.objective)
        transport_cost_val = pulp.value(transport_cost_term)
        holding_cost_val = pulp.value(holding_cost_term)
        procurement_cost_val = pulp.value(procurement_cost_term)
        fixed_cost_val = pulp.value(dc_fixed_cost_term)

        # Prepare details JSON
        active_shipments = []
        for h in hubs:
            for r in retailers:
                for p in products:
                    for t in periods:
                        val = x[(h.id, r.id, p, t)].varValue
                        if val and val > 0.01:
                            active_shipments.append({
                                "origin": h.id,
                                "destination": r.id,
                                "product": p,
                                "period": t,
                                "quantity": round(val, 2)
                            })
                            
        hub_states = []
        for h in hubs:
            for t in periods:
                hub_states.append({
                    "hub_id": h.id,
                    "period": t,
                    "is_active": int(u[(h.id, t)].varValue or 0),
                    "inventory": round(sum(y[(h.id, p, t)].varValue or 0 for p in products), 2)
                })

        details = {
            "shipments": active_shipments,
            "hub_states": hub_states,
            "planning_days": planning_days,
            "fixed_cost": round(fixed_cost_val, 2)
        }

        # 9. Save to Database
        opt_run = OptimizationRun(
            id=None,
            timestamp=None,
            solver_status=solver_status,
            total_cost=round(total_cost_val, 2),
            transport_cost=round(transport_cost_val, 2),
            holding_cost=round(holding_cost_val, 2),
            procurement_cost=round(procurement_cost_val, 2),
            run_details=json.dumps(details)
        )
        self.simulation_repo.save_optimization_run(opt_run)

        return {
            "solver_status": solver_status,
            "total_cost": round(total_cost_val, 2),
            "transport_cost": round(transport_cost_val, 2),
            "holding_cost": round(holding_cost_val, 2),
            "procurement_cost": round(procurement_cost_val, 2),
            "fixed_cost": round(fixed_cost_val, 2),
            "shipments": active_shipments,
            "hub_states": hub_states
        }

    def run_heuristic_nearest_allocation(self, planning_days: int = 3) -> Dict[str, Any]:
        """
        Executes a naive heuristic allocation (Nearest Warehouse) for comparative efficiency evaluation.
        Satisfies demand by routing directly from the geographically closest DC, neglecting capacities or holding optimization.
        """
        hubs = self.inventory_repo.list_hubs()
        retailers = self.inventory_repo.list_retailers()
        routes = self.route_repo.list_routes()
        products = ["PROD001", "PROD002"]
        periods = list(range(1, planning_days + 1))
        
        # Build distance / cost lookup
        route_costs = {}
        for r in routes:
            route_costs[(r.origin_id, r.destination_id)] = r.base_cost * r.congestion_factor

        # Find closest hub for each retailer
        nearest_hubs = {}
        for r in retailers:
            best_hub = None
            min_dist = float("inf")
            for h in hubs:
                dist = self.network_service.calculate_distance(h.latitude, h.longitude, r.latitude, r.longitude)
                if dist < min_dist:
                    min_dist = dist
                    best_hub = h.id
            nearest_hubs[r.id] = best_hub

        # Generate forecasts
        forecasts = {}
        for r in retailers:
            for p in products:
                f_list = self.forecasting_service.forecast_demand(r.id, p, planning_days)
                for t_idx, f in enumerate(f_list):
                    t = t_idx + 1
                    forecasts[(r.id, p, t)] = f["forecast"]

        # Calculate naive heuristic costs
        heur_transport_cost = 0.0
        heur_procurement_cost = 0.0
        heur_holding_cost = 0.0
        heur_fixed_cost = len(hubs) * 5000.0 * planning_days  # assume all hubs active
        
        procurement_cost_rates = {"PROD001": 100.0, "PROD002": 200.0}
        shipments = []

        for r in retailers:
            closest_h = nearest_hubs[r.id]
            for p in products:
                for t in periods:
                    qty = forecasts[(r.id, p, t)]
                    shipping_rate = route_costs.get((closest_h, r.id), 999.0)
                    
                    # Naive shipment cost
                    heur_transport_cost += shipping_rate * qty
                    heur_procurement_cost += procurement_cost_rates[p] * qty
                    # Assume simple holding cost for static stocks buffer (30 units per DC)
                    heur_holding_cost += 1.8 * 30 * len(hubs)

                    shipments.append({
                        "origin": closest_h,
                        "destination": r.id,
                        "product": p,
                        "period": t,
                        "quantity": round(qty, 2)
                    })

        total_heur_cost = heur_transport_cost + heur_procurement_cost + heur_holding_cost + heur_fixed_cost
        
        return {
            "total_cost": round(total_heur_cost, 2),
            "transport_cost": round(heur_transport_cost, 2),
            "holding_cost": round(heur_holding_cost, 2),
            "procurement_cost": round(heur_procurement_cost, 2),
            "fixed_cost": round(heur_fixed_cost, 2),
            "shipments": shipments
        }
