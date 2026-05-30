from abc import ABC, abstractmethod
from typing import Dict, Any

class Vehicle(ABC):
    
    def __init__(self, name: str, base_speed: float, fuel_efficiency: float = 0.0, co2_rate: float = 0.0) -> None:
        self.name = name
        self.base_speed = base_speed
        self.fuel_efficiency = fuel_efficiency
        self.co2_rate = co2_rate

    @abstractmethod
    def get_metrics(self, distance_km: float, time_hours: float, fuel_price: float, speed_mult: float = 1.0) -> Dict[str, Any]:
        pass


class Bicycle(Vehicle):
    
    def __init__(self, base_speed: float = 15.0, calories_rate: float = 35.0) -> None:
        super().__init__("Bicicleta", base_speed, fuel_efficiency=0.0, co2_rate=0.0)
        self.calories_rate = calories_rate

    def get_metrics(self, distance_km: float, time_hours: float, fuel_price: float, speed_mult: float = 1.0) -> Dict[str, Any]:
        calories_burned = distance_km * self.calories_rate
        return {
            "vehicle": self.name,
            "distance_km": round(distance_km, 2),
            "time_hours": round(time_hours, 3),
            "fuel_liters": 0.0,
            "fuel_cost_usd": 0.0,
            "co2_emissions_g": 0.0,
            "calories_burned": round(calories_burned, 1),
            "sustainability_score": 100,
            "overall_ranking_score": 0.0
        }


class Motorcycle(Vehicle):
    
    def __init__(self, base_speed: float = 45.0, fuel_efficiency: float = 2.5, co2_rate: float = 55.0) -> None:
        super().__init__("Motocicleta", base_speed, fuel_efficiency, co2_rate)

    def get_metrics(self, distance_km: float, time_hours: float, fuel_price: float, speed_mult: float = 1.0) -> Dict[str, Any]:
        fuel_liters = (self.fuel_efficiency / 100.0) * distance_km
        fuel_cost = fuel_liters * fuel_price
        co2_emissions = distance_km * self.co2_rate
        
        average_speed = self.base_speed
        traffic_efficiency = speed_mult * 100.0
        
        return {
            "vehicle": self.name,
            "distance_km": round(distance_km, 2),
            "time_hours": round(time_hours, 3),
            "fuel_liters": round(fuel_liters, 2),
            "fuel_cost_usd": round(fuel_cost, 2),
            "co2_emissions_g": round(co2_emissions, 1),
            "calories_burned": 0.0,
            "sustainability_score": 60,
            "traffic_efficiency": round(traffic_efficiency, 1),
            "average_speed": round(average_speed, 1),
            "overall_ranking_score": 0.0
        }


class Car(Vehicle):
    
    def __init__(self, base_speed: float = 50.0, fuel_efficiency: float = 8.0, co2_rate: float = 120.0) -> None:
        super().__init__("Carro", base_speed, fuel_efficiency, co2_rate)

    def get_metrics(self, distance_km: float, time_hours: float, fuel_price: float, speed_mult: float = 1.0) -> Dict[str, Any]:
        fuel_liters = (self.fuel_efficiency / 100.0) * distance_km
        fuel_cost = fuel_liters * fuel_price
        co2_emissions = distance_km * self.co2_rate
        
        traffic_impact = (1.0 - speed_mult) * 100.0
        comfort_score = max(50.0, min(100.0, 95.0 - (1.0 - speed_mult) * 20.0))
        
        return {
            "vehicle": self.name,
            "distance_km": round(distance_km, 2),
            "time_hours": round(time_hours, 3),
            "fuel_liters": round(fuel_liters, 2),
            "fuel_cost_usd": round(fuel_cost, 2),
            "co2_emissions_g": round(co2_emissions, 1),
            "calories_burned": 0.0,
            "sustainability_score": 20,
            "traffic_impact": round(traffic_impact, 1),
            "comfort_score": round(comfort_score, 1),
            "overall_ranking_score": 0.0
        }
#A
