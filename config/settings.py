import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    """
    Global settings and constants for the Smart Route Optimization System.
    """
    APP_ENV: str = os.getenv("APP_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "smart_routing_key_2026")
    
    # Project Paths
    BASE_DIR: Path = Path("c:/Users/jmpla/OneDrive/Desktop/Expotech")
    DB_PATH: Path = BASE_DIR / "data" / "smart_routes.db"
    LOG_FILE_PATH: Path = BASE_DIR / "logs" / "smart_routes.log"
    MAPS_CACHE_DIR: Path = BASE_DIR / "data" / "osm_cache"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    
    # Map Defaults (Center of São Paulo, Brazil)
    DEFAULT_LAT: float = -23.5505
    DEFAULT_LNG: float = -46.6333
    DEFAULT_ZOOM: int = 13
    
    # Fuel Price Settings (USD per liter)
    DEFAULT_FUEL_PRICE_GASOLINE: float = 1.50  # USD/L
    
    # Vehicle Parameter Presets
    # BICYCLE
    BIKE_SPEED: float = 15.0  # km/h
    BIKE_CALORIES_PER_KM: float = 35.0  # kcal/km
    
    # MOTORCYCLE
    MOTO_SPEED: float = 45.0  # km/h
    MOTO_FUEL_EFFICIENCY: float = 2.5  # L/100km (40 km/L)
    MOTO_CO2_EMISSIONS: float = 55.0  # g CO2/km
    
    # CAR
    CAR_SPEED: float = 50.0  # km/h
    CAR_FUEL_EFFICIENCY: float = 8.0  # L/100km (12.5 km/L)
    CAR_CO2_EMISSIONS: float = 120.0  # g CO2/km

    # Traffic Congestion Penalties (Speed multiplier factors during peak hour)
    # Cars are highly impacted, motorcycles medium impact, bicycles minimal impact.
    CAR_TRAFFIC_MULTIPLIER_HIGH: float = 0.4
    CAR_TRAFFIC_MULTIPLIER_PEAK: float = 0.25
    
    MOTO_TRAFFIC_MULTIPLIER_HIGH: float = 0.7
    MOTO_TRAFFIC_MULTIPLIER_PEAK: float = 0.55
    
    BIKE_TRAFFIC_MULTIPLIER_HIGH: float = 0.95
    BIKE_TRAFFIC_MULTIPLIER_PEAK: float = 0.90

    @classmethod
    def initialize_directories(cls) -> None:
        """
        Creates all required folder directories dynamically if they do not exist.
        """
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.MAPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Run initialization when module loads
Settings.initialize_directories()
