import numpy as np
from typing import Dict, Any, List
from config.settings import Settings
from traffic.simulator import TrafficSimulator

class MonteCarloSimulator:
    """
    Core Monte Carlo simulation engine.
    Calculates stochastic distributions for supply chain networks under stress conditions.
    """
    @staticmethod
    def run_simulation(
        scenario_type: str, 
        trials: int, 
        base_capacities: np.ndarray,
        base_holding_costs: np.ndarray,
        base_route_costs: np.ndarray,
        base_demands: np.ndarray,
        hubs_fixed_costs: List[float]
    ) -> Dict[str, Any]:
        # Scenario configuration mapping
        if scenario_type == "Optimistic":
            demand_mult, demand_std = 0.85, 0.04
            cost_mult, cost_std = 0.90, 0.03
            cap_mult = 1.0
            weather_probs = [0.85, 0.12, 0.02, 0.01]  # Sunny, Rainy, Snowy, Stormy
            traffic_probs = [0.50, 0.40, 0.08, 0.02]  # Low, Medium, High, Peak Hour
        elif scenario_type == "Pessimistic":
            demand_mult, demand_std = 1.25, 0.18
            cost_mult, cost_std = 1.35, 0.10
            cap_mult = 0.85
            weather_probs = [0.40, 0.40, 0.15, 0.05]
            traffic_probs = [0.05, 0.25, 0.50, 0.20]
        elif scenario_type == "Crisis":
            demand_mult, demand_std = 1.50, 0.35
            cost_mult, cost_std = 1.80, 0.25
            cap_mult = 0.60
            weather_probs = [0.20, 0.40, 0.30, 0.10]
            traffic_probs = [0.02, 0.13, 0.45, 0.40]
        else: # "Realistic"
            demand_mult, demand_std = 1.00, 0.08
            cost_mult, cost_std = 1.00, 0.05
            cap_mult = 1.00
            weather_probs = [0.65, 0.25, 0.07, 0.03]
            traffic_probs = [0.20, 0.50, 0.20, 0.10]

        rng = np.random.default_rng()

        costs_out = []
        service_levels_out = []
        stockouts_out = []
        utilizations_out = []

        sim_fuel_prices = []
        sim_weathers = []
        sim_traffics = []
        sim_traffic_delays = []
        
        sim_vehicle_times = {"Carro": [], "Motocicleta": [], "Bicicleta": []}
        sim_vehicle_costs = {"Carro": [], "Motocicleta": [], "Bicicleta": []}
        sim_vehicle_co2 = {"Carro": [], "Motocicleta": [], "Bicicleta": []}
        
        weathers = ["Sunny", "Rainy", "Snowy", "Stormy"]
        traffics = ["Low", "Medium", "High", "Peak Hour"]

        # Run stochastic iterations
        for _ in range(trials):
            # Apply normal noise and scenario multiplier for supply chain costs
            stochastic_demands = base_demands * rng.normal(demand_mult, demand_std, size=len(base_demands))
            stochastic_demands = np.clip(stochastic_demands, 1.0, None)
            
            stochastic_costs = base_route_costs * rng.normal(cost_mult, cost_std, size=len(base_route_costs))
            stochastic_costs = np.clip(stochastic_costs, 0.1, None)

            active_capacities = base_capacities * cap_mult

            total_demands_qty = np.sum(stochastic_demands)
            total_avail_capacity = np.sum(active_capacities)

            if total_avail_capacity >= total_demands_qty:
                service_level = rng.uniform(0.96, 1.0) if scenario_type in ["Optimistic", "Realistic"] else rng.uniform(0.85, 0.95)
                stockout_rate = rng.uniform(0.0, 0.03) if scenario_type in ["Optimistic", "Realistic"] else rng.uniform(0.04, 0.12)
            else:
                capacity_ratio = total_avail_capacity / total_demands_qty
                service_level = float(np.clip(capacity_ratio * rng.uniform(0.85, 0.95), 0.4, 0.95))
                stockout_rate = float(np.clip((1.0 - capacity_ratio) * rng.uniform(1.0, 1.25), 0.05, 0.6))

            # Operational cost estimation
            raw_transport_expense = np.sum(stochastic_demands) * np.mean(stochastic_costs) * 0.4
            raw_holding_expense = np.sum(active_capacities) * np.mean(base_holding_costs) * 0.15
            raw_fixed_expense = np.sum(hubs_fixed_costs) * (1.1 if scenario_type == "Crisis" else 1.0)
            
            trial_total_cost = raw_transport_expense + raw_holding_expense + raw_fixed_expense
            utilization = float(np.clip((total_demands_qty / total_avail_capacity) * rng.uniform(0.85, 0.95), 0.1, 0.98))

            costs_out.append(trial_total_cost)
            service_levels_out.append(service_level)
            stockouts_out.append(stockout_rate)
            utilizations_out.append(utilization)

            # Weather & Traffic sampling
            w_state = rng.choice(weathers, p=weather_probs)
            t_intensity = rng.choice(traffics, p=traffic_probs)
            f_price = max(0.50, rng.normal(Settings.DEFAULT_FUEL_PRICE_GASOLINE * cost_mult, 0.15 * cost_mult))
            
            sim_fuel_prices.append(f_price)
            sim_weathers.append(w_state)
            sim_traffics.append(t_intensity)
            
            trip_dist = 15.0
            car_speed_mult = TrafficSimulator.get_speed_multiplier("Carro", t_intensity, w_state)
            sim_traffic_delays.append((1.0 - car_speed_mult) * 100.0)
            
            for v_name, base_spd, base_eff, co2_rt in [
                ("Carro", Settings.CAR_SPEED, Settings.CAR_FUEL_EFFICIENCY, Settings.CAR_CO2_EMISSIONS),
                ("Motocicleta", Settings.MOTO_SPEED, Settings.MOTO_FUEL_EFFICIENCY, Settings.MOTO_CO2_EMISSIONS),
                ("Bicicleta", Settings.BIKE_SPEED, 0.0, 0.0)
            ]:
                speed_mult = TrafficSimulator.get_speed_multiplier(v_name, t_intensity, w_state)
                trial_speed_mult = max(0.1, rng.normal(speed_mult, 0.05))
                adjusted_speed = base_spd * trial_speed_mult
                time_hours = trip_dist / adjusted_speed
                
                fuel_mult = TrafficSimulator.get_fuel_consumption_multiplier(t_intensity, w_state)
                trial_fuel_mult = max(0.5, rng.normal(fuel_mult, 0.08))
                adjusted_efficiency = base_eff * trial_fuel_mult
                
                fuel_liters = (adjusted_efficiency / 100.0) * trip_dist if base_eff > 0.0 else 0.0
                fuel_cost = fuel_liters * f_price
                co2_emissions = trip_dist * co2_rt
                
                sim_vehicle_times[v_name].append(time_hours * 60.0)
                sim_vehicle_costs[v_name].append(fuel_cost)
                sim_vehicle_co2[v_name].append(co2_emissions)

        mean_cost = float(np.mean(costs_out))
        std_cost = float(np.std(costs_out))
        mean_service = float(np.mean(service_levels_out))
        mean_stockout = float(np.mean(stockouts_out))
        mean_utilization = float(np.mean(utilizations_out))

        ci_lower = mean_cost - (1.96 * std_cost / np.sqrt(trials))
        ci_upper = mean_cost + (1.96 * std_cost / np.sqrt(trials))

        weather_freqs = {w: round((sim_weathers.count(w) / trials) * 100, 1) for w in weathers}
        traffic_freqs = {t: round((sim_traffics.count(t) / trials) * 100, 1) for t in traffics}

        return {
            "mean_cost": mean_cost,
            "std_cost": std_cost,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "costs_out": costs_out,
            "mean_service": mean_service,
            "mean_stockout": mean_stockout,
            "mean_utilization": mean_utilization,
            "avg_fuel_price": float(np.mean(sim_fuel_prices)),
            "weather_freqs": weather_freqs,
            "traffic_freqs": traffic_freqs,
            "avg_traffic_delay_pct": float(np.mean(sim_traffic_delays)),
            "sim_fuel_prices": sim_fuel_prices,
            "sim_vehicle_times": sim_vehicle_times,
            "sim_vehicle_costs": sim_vehicle_costs,
            "sim_vehicle_co2": sim_vehicle_co2,
            "demand_multiplier": demand_mult,
            "cost_multiplier": cost_mult
        }
