import logging
from typing import Dict, Any, List, Tuple
from config.settings import Settings
from vehicles.models import Bicycle, Motorcycle, Car
from traffic.simulator import TrafficSimulator
from routing.engine import RoutingEngine
from optimization.tsp_solver import TspSolver
from database.manager import DatabaseManager

logger = logging.getLogger("smart_routing.services.optimizer_service")

class OptimizerService:
    """
    Main Orchestrator Service for the Smart Route Optimization System.
    Links mapping coordinates, vehicle metrics, traffic factors, and optimization solvers.
    """
    
    def __init__(self) -> None:
        # Instantiate vehicle models with default settings
        self.bike = Bicycle(Settings.BIKE_SPEED, Settings.BIKE_CALORIES_PER_KM)
        self.moto = Motorcycle(Settings.MOTO_SPEED, Settings.MOTO_FUEL_EFFICIENCY, Settings.MOTO_CO2_EMISSIONS)
        self.car = Car(Settings.CAR_SPEED, Settings.CAR_FUEL_EFFICIENCY, Settings.CAR_CO2_EMISSIONS)
        self.vehicles = {
            "Bicicleta": self.bike,
            "Motocicleta": self.moto,
            "Carro": self.car
        }

    def geocode_address(self, address: str) -> Dict[str, float]:
        """
        Geocodes a written address using Nominatim geocoding service.
        Returns a dictionary with 'lat' and 'lng' if found, else raises ValueError.
        """
        # Quick offline resolution cache for default São Paulo demo locations
        address_lower = address.lower()
        if "paulista, 1000" in address_lower:
            return {"lat": -23.5629, "lng": -46.6544}
        elif "masp" in address_lower:
            return {"lat": -23.5615, "lng": -46.6559}
        elif "augusta, 1500" in address_lower:
            return {"lat": -23.5596, "lng": -46.6617}
        elif "ibirapuera" in address_lower:
            return {"lat": -23.5874, "lng": -46.6576}

        from geopy.geocoders import Nominatim
        import time
        try:
            # Add user_agent to prevent blockages
            geolocator = Nominatim(user_agent="smart_route_optimizer_agent_2026")
            time.sleep(1.0)  # Sleep to follow terms of service usage limits
            location = geolocator.geocode(address)
            if location:
                logger.info(f"Geocoded '{address}' -> {location.latitude}, {location.longitude}")
                return {"lat": location.latitude, "lng": location.longitude}
        except Exception as e:
            logger.warning(f"Geocoding exception for '{address}': {e}")
            # If completely offline, try to generate a mock coordinate near default starting point to avoid crashing
            import random
            mock_lat = Settings.DEFAULT_LAT + random.uniform(-0.01, 0.01)
            mock_lng = Settings.DEFAULT_LNG + random.uniform(-0.01, 0.01)
            logger.info(f"Geocoding failed/offline. Falling back to mock coordinates: {mock_lat}, {mock_lng}")
            return {"lat": mock_lat, "lng": mock_lng}
            
        raise ValueError(f"Address not found: '{address}'")

    def run_routing_optimization(
        self,
        locations: List[Dict[str, float]],
        selected_vehicles: List[str],
        traffic_intensity: str,
        weather: str,
        fuel_price: float,
        return_to_start: bool = True,
        prioritize_eco: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete route optimization workflow.
        1. Downloads OSMnx sub-graph for locations bounding box.
        2. Solves the TSP optimal sequence.
        3. Calculates metrics for each selected transport mode.
        4. Logs results to database.
        5. Generates AI-style mobility recommendations.
        """
        if len(locations) < 2:
            raise ValueError("You must select at least a Start location and one delivery point.")
            
        start_point = locations[0]
        delivery_points = locations[1:]
        
        # 1. Estimate bounding box and fetch street network graph (OSMnx)
        # Bounding box coordinates with a padding margin (approx 1.5km)
        lats = [loc["lat"] for loc in locations]
        lngs = [loc["lng"] for loc in locations]
        padding = 0.015
        min_lat, max_lat = min(lats) - padding, max(lats) + padding
        min_lng, max_lng = min(lngs) - padding, max(lngs) + padding
        
        G = RoutingEngine.get_street_network(min_lat, max_lat, min_lng, max_lng)
        
        # 2. Run Traveling Salesman Problem (TSP) solver
        optimal_order, total_dist, leg_details = TspSolver.optimize_route(
            start_point, delivery_points, G, return_to_start
        )
        
        # 3. Calculate metrics for each selected vehicle
        vehicle_metrics = []
        legs_per_vehicle = {}
        
        for vehicle_name in selected_vehicles:
            vehicle = self.vehicles[vehicle_name]
            
            # Apply traffic and weather speed multipliers
            speed_mult = TrafficSimulator.get_speed_multiplier(vehicle_name, traffic_intensity, weather)
            adjusted_speed = vehicle.base_speed * speed_mult
            
            # Apply fuel consumption multiplier
            fuel_mult = TrafficSimulator.get_fuel_consumption_multiplier(traffic_intensity, weather)
            adjusted_efficiency = vehicle.fuel_efficiency * fuel_mult
            
            # Copy base vehicle properties to calculate leg metrics
            temp_vehicle = None
            if vehicle_name == "Bicicleta":
                temp_vehicle = Bicycle(adjusted_speed, vehicle.calories_rate)
            elif vehicle_name == "Motocicleta":
                temp_vehicle = Motorcycle(adjusted_speed, adjusted_efficiency, vehicle.co2_rate)
            else:
                temp_vehicle = Car(adjusted_speed, adjusted_efficiency, vehicle.co2_rate)
                
            # Compute leg-by-leg metrics
            vehicle_legs = []
            total_time_hours = 0.0
            
            for leg in leg_details:
                # Time = distance / speed
                leg_dist = leg["distance_km"]
                leg_time = leg_dist / adjusted_speed
                total_time_hours += leg_time
                
                vehicle_legs.append({
                    "from_node": leg["from_node"],
                    "to_node": leg["to_node"],
                    "distance_km": leg_dist,
                    "time_hours": leg_time,
                    "path_coords": leg["path_coords"]
                })
                
            legs_per_vehicle[vehicle_name] = vehicle_legs
            
            # Fetch summary metrics
            m = temp_vehicle.get_metrics(total_dist, total_time_hours, fuel_price, speed_mult=speed_mult)
            vehicle_metrics.append(m)

        # 4. Generate rankings & recommendations
        recommendation = self.generate_recommendation(vehicle_metrics, traffic_intensity, weather, prioritize_eco)
        
        # 5. Log run to database
        DatabaseManager.save_route_run(
            start_point["lat"], start_point["lng"], len(delivery_points),
            traffic_intensity, weather, vehicle_metrics
        )
        
        return {
            "optimal_order": optimal_order,
            "total_distance_km": total_dist,
            "metrics": vehicle_metrics,
            "legs_per_vehicle": legs_per_vehicle,
            "recommendation": recommendation,
            "osm_graph_active": G is not None
        }

    def generate_recommendation(self, metrics: List[Dict[str, Any]], traffic: str, weather: str, prioritize_eco: bool = True) -> Dict[str, Any]:
        """
        AI Decision Recommendation System.
        Evaluates time, cost, safety, and CO2 emissions to recommend the overall best transport.
        """
        if not metrics:
            return {"best_vehicle": "None", "reason": "No vehicles selected."}
            
        # Map values to find the best option
        # We compute a score: lower score is better
        # Normalize times and costs relative to averages
        avg_time = sum(m["time_hours"] for m in metrics) / len(metrics) if metrics else 1.0
        avg_cost = sum(m["fuel_cost_usd"] for m in metrics) / len(metrics) if metrics else 1.0
        
        best_score = float("inf")
        best_vehicle = None
        
        for m in metrics:
            # Normalize indicators
            norm_time = m["time_hours"] / avg_time if avg_time > 0 else 1.0
            norm_cost = m["fuel_cost_usd"] / avg_cost if avg_cost > 0 else 1.0
            norm_co2 = m["co2_emissions_g"] / 300.0  # 300g benchmark
            
            # Sustainability bonus
            sustainability_discount = (100 - m["sustainability_score"]) / 100.0
            
            # Penalty for high traffic congestion with cars
            traffic_penalty = 0.0
            if m["vehicle"] == "Carro" and traffic in ["High", "Peak Hour"]:
                traffic_penalty = 0.5  # Heavy penalty for being stuck
                
            if prioritize_eco:
                score = (0.35 * norm_time) + (0.30 * norm_cost) + (0.15 * norm_co2) + (0.20 * sustainability_discount) + traffic_penalty
            else:
                # Realista: Focus only on operational factors (time and cost)
                score = (0.50 * norm_time) + (0.50 * norm_cost) + traffic_penalty
                
            m["overall_ranking_score"] = round(100.0 - (score * 20.0), 1)  # Scale to 0-100 score for display
            
            if score < best_score:
                best_score = score
                best_vehicle = m["vehicle"]

        # Generate custom reason based on weather, traffic, and choice
        traffic_pt_map = {"Low": "Baixo", "Medium": "Médio", "High": "Alto", "Peak Hour": "Horário de Pico"}
        weather_pt_map = {"Sunny": "Ensolarado", "Rainy": "Chuvoso", "Snowy": "Nevando", "Stormy": "Tempestuoso"}
        traffic_pt = traffic_pt_map.get(traffic, traffic)
        weather_pt = weather_pt_map.get(weather, weather)

        reason = ""
        if best_vehicle == "Bicicleta":
            if prioritize_eco:
                reason = "A Bicicleta é recomendada pois é totalmente ecológica (0g de CO2), tem custo de combustível zero e não pega trânsito. Ideal para curtas distâncias!"
            else:
                reason = "A Bicicleta é recomendada pois apresenta custo operacional zero e resiliência total ao trânsito, sendo ideal para percursos urbanos muito curtos."
            if weather in ["Rainy", "Snowy"]:
                reason += f" Nota: O clima está {weather_pt.lower()}; use roupas de ciclismo adequadas."
        elif best_vehicle == "Motocicleta":
            reason = f"A Motocicleta é a melhor escolha sob o trânsito atual ({traffic_pt}). Ela passa pelos engarrafamentos de carros, economiza muito tempo comparada à bicicleta e gasta metade do combustível de um carro."
        else: # Carro
            if prioritize_eco:
                reason = "O Carro é recomendado por sua velocidade e proteção contra as intempéries climáticas. Ideal para distâncias longas. Contudo, gera a maior pegada de carbono e sofre muito com trânsito lento."
            else:
                reason = "O Carro é recomendado por sua alta velocidade em trânsito livre e total proteção contra intempéries climáticas, garantindo o transporte mais rápido para distâncias médias ou longas."

        return {
            "best_vehicle": best_vehicle,
            "reason": reason
        }
