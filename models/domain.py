from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional, Dict, Any

@dataclass
class User:
    id: Optional[int]
    username: str
    role: str
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Hub:
    id: str
    name: str
    latitude: float
    longitude: float
    capacity: float
    fixed_cost: float
    holding_cost: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Retailer:
    id: str
    name: str
    latitude: float
    longitude: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Route:
    id: Optional[int]
    origin_id: str
    destination_id: str
    distance: float
    base_cost: float
    congestion_factor: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DemandHistory:
    id: Optional[int]
    retailer_id: str
    product_id: str
    date: date
    quantity: float
    price: float
    weather: str = "Clear"
    is_holiday: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if isinstance(d["date"], date):
            d["date"] = d["date"].isoformat()
        return d

@dataclass
class SimulationRun:
    id: Optional[int]
    timestamp: Optional[datetime]
    scenario_type: str
    demand_multiplier: float
    cost_multiplier: float
    total_cost: float
    service_level: float
    stockout_rate: float
    avg_utilization: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class OptimizationRun:
    id: Optional[int]
    timestamp: Optional[datetime]
    solver_status: str
    total_cost: float
    transport_cost: float
    holding_cost: float
    procurement_cost: float
    run_details: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
#A
