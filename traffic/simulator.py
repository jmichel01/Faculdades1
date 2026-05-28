import logging
from config.settings import Settings

logger = logging.getLogger("smart_routing.traffic.simulator")

class TrafficSimulator:
    """
    Simulates dynamic urban traffic behaviors and weather conditions.
    Applies penalties to vehicle travel speed and fuel consumption rates.
    """
    
    @staticmethod
    def get_speed_multiplier(vehicle_name: str, traffic_intensity: str, weather: str) -> float:
        """
        Determines the overall speed multiplier based on the transport mode, traffic congestion, and weather.
        """
        # 1. Base traffic intensity factors
        traffic_mult = 1.0
        
        if traffic_intensity == "Medium":
            if vehicle_name == "Carro":
                traffic_mult = 0.75
            elif vehicle_name == "Motocicleta":
                traffic_mult = 0.85
            else:  # Bicicleta
                traffic_mult = 0.98
        elif traffic_intensity == "High":
            if vehicle_name == "Carro":
                traffic_mult = Settings.CAR_TRAFFIC_MULTIPLIER_HIGH
            elif vehicle_name == "Motocicleta":
                traffic_mult = Settings.MOTO_TRAFFIC_MULTIPLIER_HIGH
            else:
                traffic_mult = Settings.BIKE_TRAFFIC_MULTIPLIER_HIGH
        elif traffic_intensity == "Peak Hour":
            if vehicle_name == "Carro":
                traffic_mult = Settings.CAR_TRAFFIC_MULTIPLIER_PEAK
            elif vehicle_name == "Motocicleta":
                traffic_mult = Settings.MOTO_TRAFFIC_MULTIPLIER_PEAK
            else:
                traffic_mult = Settings.BIKE_TRAFFIC_MULTIPLIER_PEAK
                
        # 2. Weather factors
        weather_mult = 1.0
        if weather == "Rainy":
            if vehicle_name == "Carro":
                weather_mult = 0.90
            elif vehicle_name == "Motocicleta":
                weather_mult = 0.75  # Slippery roads increase hazard
            else:  # Bicicleta
                weather_mult = 0.70  # Rain makes pedaling hard
        elif weather == "Snowy":
            if vehicle_name == "Carro":
                weather_mult = 0.70
            elif vehicle_name == "Motocicleta":
                weather_mult = 0.40  # Motorcycles have extreme safety concerns in snow
            else:  # Bicicleta
                weather_mult = 0.35  # Biking in snow is very hard
        elif weather == "Stormy":
            if vehicle_name == "Carro":
                weather_mult = 0.60
            elif vehicle_name == "Motocicleta":
                weather_mult = 0.30  # High winds make it extremely risky
            else:  # Bicicleta
                weather_mult = 0.25
                
        total_multiplier = traffic_mult * weather_mult
        logger.debug(f"Computed speed multiplier for {vehicle_name} (Traffic: {traffic_intensity}, Weather: {weather}): {total_multiplier:.3f}")
        
        # Guard rail to prevent zero speed
        return max(0.10, total_multiplier)

    @staticmethod
    def get_fuel_consumption_multiplier(traffic_intensity: str, weather: str) -> float:
        """
        Estimates the surge in fuel consumption rate under heavy traffic (stop-and-go) or severe weather.
        """
        fuel_mult = 1.0
        
        # Stop-and-go traffic increases fuel consumption rate (L/100km)
        if traffic_intensity == "Medium":
            fuel_mult += 0.10
        elif traffic_intensity == "High":
            fuel_mult += 0.25
        elif traffic_intensity == "Peak Hour":
            fuel_mult += 0.45
            
        # Severe weather (use of heaters/wipers, resistance)
        if weather == "Rainy":
            fuel_mult += 0.05
        elif weather in ["Snowy", "Stormy"]:
            fuel_mult += 0.15
            
        return fuel_mult
