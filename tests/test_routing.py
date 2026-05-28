import pytest
from vehicles.models import Bicycle, Motorcycle, Car
from traffic.simulator import TrafficSimulator
from routing.engine import RoutingEngine
from optimization.tsp_solver import TspSolver

def test_vehicle_metrics() -> None:
    """
    Validates calculations inside vehicle models (Car, Moto, Bike).
    """
    car = Car(base_speed=50.0, fuel_efficiency=8.0, co2_rate=120.0)
    metrics = car.get_metrics(distance_km=10.0, time_hours=0.2, fuel_price=1.50)
    
    assert metrics["vehicle"] == "Carro"
    assert metrics["distance_km"] == 10.0
    assert metrics["time_hours"] == 0.2
    assert metrics["fuel_liters"] == 0.8  # (8.0/100) * 10
    assert metrics["fuel_cost_usd"] == 1.20  # 0.8 * 1.5
    assert metrics["co2_emissions_g"] == 1200.0  # 10 * 120
    assert metrics["calories_burned"] == 0.0
    assert metrics["traffic_impact"] == 0.0
    assert metrics["comfort_score"] == 95.0
    
    # Test congested Car metrics
    metrics_congested = car.get_metrics(distance_km=10.0, time_hours=0.4, fuel_price=1.50, speed_mult=0.5)
    assert metrics_congested["traffic_impact"] == 50.0
    assert metrics_congested["comfort_score"] == 85.0
    
    # Test Motorcycle metrics
    moto = Motorcycle(base_speed=45.0, fuel_efficiency=2.5, co2_rate=55.0)
    m_metrics = moto.get_metrics(distance_km=10.0, time_hours=0.25, fuel_price=1.50, speed_mult=0.8)
    assert m_metrics["vehicle"] == "Motocicleta"
    assert m_metrics["traffic_efficiency"] == 80.0
    assert m_metrics["average_speed"] == 45.0

def test_traffic_multiplier() -> None:
    """
    Verifies that traffic simulator returns expected multipliers.
    """
    # Car speed multiplier during peak hour must be lower than low traffic
    car_peak = TrafficSimulator.get_speed_multiplier("Carro", "Peak Hour", "Sunny")
    car_low = TrafficSimulator.get_speed_multiplier("Carro", "Low", "Sunny")
    
    assert car_peak < car_low
    assert car_peak > 0.0
    
    # Bicycle should be highly affected by Snowy weather but unaffected by Peak Hour traffic
    bike_peak = TrafficSimulator.get_speed_multiplier("Bicicleta", "Peak Hour", "Sunny")
    bike_snow = TrafficSimulator.get_speed_multiplier("Bicicleta", "Low", "Snowy")
    
    assert bike_snow < bike_peak

def test_grid_routing_fallback() -> None:
    """
    Validates the staircase grid route generator behavior.
    """
    coords, dist = RoutingEngine.generate_grid_path(47.6062, -122.3321, 47.6101, -122.3421, num_blocks=3)
    
    assert len(coords) > 2
    assert coords[0] == (47.6062, -122.3321)
    assert coords[-1] == (47.6101, -122.3421)
    assert dist > 0.0

def test_tsp_solver() -> None:
    """
    Validates exact TSP permutation optimal solutions.
    """
    start = {"lat": 47.6062, "lng": -122.3321}
    destinations = [
        {"lat": 47.6080, "lng": -122.3350},  # Close
        {"lat": 47.6150, "lng": -122.3500},  # Far
        {"lat": 47.6100, "lng": -122.3400}   # Medium
    ]
    
    order, dist, legs = TspSolver.optimize_route(start, destinations, G=None, return_to_start=True)
    
    assert len(order) == 3
    assert set(order) == {0, 1, 2}
    assert dist > 0.0
    assert len(legs) == 4  # 3 delivery points + return to start
