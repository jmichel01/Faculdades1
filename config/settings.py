import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "smart_routing_key_2026")
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DB_PATH: Path = Path(os.getenv("DB_PATH", str(BASE_DIR / "data" / "smart_routes.db")))
    LOG_FILE_PATH: Path = Path(os.getenv("LOG_FILE_PATH", str(BASE_DIR / "logs" / "smart_routes.log")))
    MAPS_CACHE_DIR: Path = BASE_DIR / "data" / "osm_cache"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    
    DEFAULT_LAT: float = -23.5505
    DEFAULT_LNG: float = -46.6333
    DEFAULT_ZOOM: int = 13
    
    DEFAULT_FUEL_PRICE_GASOLINE: float = 1.50
    
    BIKE_SPEED: float = 15.0
    BIKE_CALORIES_PER_KM: float = 35.0
    
    MOTO_SPEED: float = 45.0
    MOTO_FUEL_EFFICIENCY: float = 2.5
    MOTO_CO2_EMISSIONS: float = 55.0
    
    CAR_SPEED: float = 50.0
    CAR_FUEL_EFFICIENCY: float = 8.0
    CAR_CO2_EMISSIONS: float = 120.0

    CAR_TRAFFIC_MULTIPLIER_HIGH: float = 0.4
    CAR_TRAFFIC_MULTIPLIER_PEAK: float = 0.25
    
    MOTO_TRAFFIC_MULTIPLIER_HIGH: float = 0.7
    MOTO_TRAFFIC_MULTIPLIER_PEAK: float = 0.55
    
    BIKE_TRAFFIC_MULTIPLIER_HIGH: float = 0.95
    BIKE_TRAFFIC_MULTIPLIER_PEAK: float = 0.90

    @classmethod
    def initialize_directories(cls) -> None:
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.MAPS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

Settings.initialize_directories()
#A
