import math
import random
from datetime import date, timedelta
from typing import List
from database.connection import DatabaseConnectionManager
from models.domain import Hub, Retailer, Route, DemandHistory
from repositories.inventory_repo import InventoryRepository
from repositories.route_repo import RouteRepository

class MockDataGenerator:
    """
    Constructs highly realistic supply chain mock structures.
    Includes seasonal oscillations, weather effects, and holiday demand spikes.
    """
    
    # Hub locations
    HUBS_DATA = [
        ("HUB_ATL", "Atlanta Distribution Center", 33.7490, -84.3880, 50000.0, 5000.0, 1.5),
        ("HUB_CHI", "Chicago Distribution Center", 41.8781, -87.6298, 65000.0, 7500.0, 2.0),
        ("HUB_DAL", "Dallas Logistics Hub", 32.7767, -96.7970, 45000.0, 4800.0, 1.2),
        ("HUB_LAX", "Los Angeles Gateway", 34.0522, -118.2437, 70000.0, 9500.0, 2.5),
    ]

    # Retailer locations
    RETAILERS_DATA = [
        ("RET_NYC", "New York Store", 40.7128, -74.0060),
        ("RET_MIA", "Miami Mega Retail", 25.7617, -80.1918),
        ("RET_HOU", "Houston Direct", 29.7604, -95.3698),
        ("RET_DEN", "Denver Mountain Outlet", 39.7392, -104.9903),
        ("RET_SEA", "Seattle Tech Depot", 47.6062, -122.3321),
        ("RET_SFO", "San Francisco Express", 37.7749, -122.4194),
        ("RET_BOS", "Boston Market", 42.3601, -71.0589),
        ("RET_PHX", "Phoenix Retail", 33.4484, -112.0740),
        ("RET_MSP", "Minneapolis Outlet", 44.9778, -93.2650),
        ("RET_STL", "St. Louis Hub Store", 38.6270, -90.1994),
    ]

    PRODUCTS = ["PROD001", "PROD002"]

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Great circle distance approximation.
        """
        R = 6371.0  # Earth's radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def generate_and_seed(cls) -> None:
        """
        Seeds the SQLite database with high quality data.
        """
        inventory_repo = InventoryRepository()
        route_repo = RouteRepository()

        # 1. Seed Warehouses
        for h in cls.HUBS_DATA:
            inventory_repo.save_hub(Hub(
                id=h[0], name=h[1], latitude=h[2], longitude=h[3],
                capacity=h[4], fixed_cost=h[5], holding_cost=h[6]
            ))

        # 2. Seed Retailers
        for r in cls.RETAILERS_DATA:
            inventory_repo.save_retailer(Retailer(
                id=r[0], name=r[1], latitude=r[2], longitude=r[3]
            ))

        # 3. Seed Routes
        hubs = inventory_repo.list_hubs()
        retailers = inventory_repo.list_retailers()
        
        for hub in hubs:
            for ret in retailers:
                distance = cls.calculate_distance(hub.latitude, hub.longitude, ret.latitude, ret.longitude)
                # Base shipping cost scales with distance (0.12 USD/km)
                base_cost = distance * 0.12
                congestion = round(random.uniform(0.95, 1.45), 2)
                route_repo.save_route(Route(
                    id=None, origin_id=hub.id, destination_id=ret.id,
                    distance=round(distance, 2), base_cost=round(base_cost, 2),
                    congestion_factor=congestion
                ))

        # 4. Seed Historical Demand (12 Months, i.e., 365 Days)
        start_date = date.today() - timedelta(days=365)
        demand_list: List[DemandHistory] = []
        weathers = ["Clear", "Rainy", "Cloudy", "Snowy", "Stormy"]

        # Generate seed demand sequence
        for day in range(365):
            current_date = start_date + timedelta(days=day)
            
            # Holiday markers (e.g., Thanksgiving, Christmas, Independence Day, etc.)
            is_holiday = 0
            if (current_date.month == 11 and current_date.day in [24, 25, 26, 27]) or \
               (current_date.month == 12 and current_date.day in [20, 21, 22, 23, 24, 25]) or \
               (current_date.month == 7 and current_date.day in [3, 4, 5]):
                is_holiday = 1

            # Dynamic weather
            weather = random.choices(weathers, weights=[0.6, 0.2, 0.1, 0.07, 0.03])[0]

            for ret in retailers:
                for prod in cls.PRODUCTS:
                    # Mathematical seasonality model
                    # base demand varies per retailer and product
                    ret_hash = sum(ord(c) for c in ret.id)
                    prod_hash = sum(ord(c) for c in prod)
                    base_demand = 30 + (ret_hash % 20) + (prod_hash % 10)

                    # Seasonal sinusoidal oscillations
                    # Yearly wave (highest in winter/summer depending on phase)
                    yearly_phase = 2 * math.pi * day / 365
                    yearly_seasonality = 15 * math.sin(yearly_phase)

                    # Weekly wave (highest on Thursday/Friday/Saturday)
                    weekly_phase = 2 * math.pi * current_date.weekday() / 7
                    weekly_seasonality = 8 * math.sin(weekly_phase)

                    # Weather shocks (storms and snow lower demand slightly)
                    weather_multiplier = 1.0
                    if weather in ["Snowy", "Stormy"]:
                        weather_multiplier = 0.8
                    elif weather == "Rainy":
                        weather_multiplier = 0.95

                    # Holiday spikes
                    holiday_surge = 0
                    if is_holiday:
                        holiday_surge = random.uniform(25, 55)

                    # Compose components and add Gaussian noise
                    noise = random.normalvariate(0, 4)
                    qty = max(2.0, (base_demand + yearly_seasonality + weekly_seasonality + holiday_surge) * weather_multiplier + noise)

                    price = 150.0 if prod == "PROD001" else 280.0
                    
                    demand_list.append(DemandHistory(
                        id=None, retailer_id=ret.id, product_id=prod,
                        date=current_date, quantity=round(qty, 2), price=price,
                        weather=weather, is_holiday=is_holiday
                    ))

        # Save to database in optimized batch
        inventory_repo.save_demand_history_batch(demand_list)
