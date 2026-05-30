import sqlite3
from typing import List, Optional
from datetime import date
from database.connection import DatabaseConnectionManager
from models.domain import Hub, Retailer, DemandHistory
from repositories.base_repository import BaseRepository

class InventoryRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("optilogix.repository.inventory")

    def save_hub(self, hub: Hub) -> Hub:
        query = """
            INSERT INTO hubs (id, name, latitude, longitude, capacity, fixed_cost, holding_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                capacity = excluded.capacity,
                fixed_cost = excluded.fixed_cost,
                holding_cost = excluded.holding_cost;
        """
        with DatabaseConnectionManager.get_connection() as conn:
            conn.execute(query, (
                hub.id, hub.name, hub.latitude, hub.longitude,
                hub.capacity, hub.fixed_cost, hub.holding_cost
            ))
        return hub

    def get_hub(self, hub_id: str) -> Optional[Hub]:
        query = "SELECT id, name, latitude, longitude, capacity, fixed_cost, holding_cost FROM hubs WHERE id = ?"
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (hub_id,))
            row = cursor.fetchone()
            if row:
                return Hub(
                    id=row["id"], name=row["name"],
                    latitude=row["latitude"], longitude=row["longitude"],
                    capacity=row["capacity"], fixed_cost=row["fixed_cost"],
                    holding_cost=row["holding_cost"]
                )
        return None

    def list_hubs(self) -> List[Hub]:
        query = "SELECT id, name, latitude, longitude, capacity, fixed_cost, holding_cost FROM hubs ORDER BY id ASC"
        hubs = []
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                hubs.append(Hub(
                    id=row["id"], name=row["name"],
                    latitude=row["latitude"], longitude=row["longitude"],
                    capacity=row["capacity"], fixed_cost=row["fixed_cost"],
                    holding_cost=row["holding_cost"]
                ))
        return hubs

    def save_retailer(self, retailer: Retailer) -> Retailer:
        query = """
            INSERT INTO retailers (id, name, latitude, longitude)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                latitude = excluded.latitude,
                longitude = excluded.longitude;
        """
        with DatabaseConnectionManager.get_connection() as conn:
            conn.execute(query, (
                retailer.id, retailer.name, retailer.latitude, retailer.longitude
            ))
        return retailer

    def get_retailer(self, retailer_id: str) -> Optional[Retailer]:
        query = "SELECT id, name, latitude, longitude FROM retailers WHERE id = ?"
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (retailer_id,))
            row = cursor.fetchone()
            if row:
                return Retailer(
                    id=row["id"], name=row["name"],
                    latitude=row["latitude"], longitude=row["longitude"]
                )
        return None

    def list_retailers(self) -> List[Retailer]:
        query = "SELECT id, name, latitude, longitude FROM retailers ORDER BY id ASC"
        retailers = []
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                retailers.append(Retailer(
                    id=row["id"], name=row["name"],
                    latitude=row["latitude"], longitude=row["longitude"]
                ))
        return retailers

    def save_demand_history_batch(self, demand_list: List[DemandHistory]) -> None:
        query = """
            INSERT INTO demand_history (retailer_id, product_id, date, quantity, price, weather, is_holiday)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        data = [
            (
                d.retailer_id, d.product_id,
                d.date.isoformat() if isinstance(d.date, date) else d.date,
                d.quantity, d.price, d.weather, d.is_holiday
            )
            for d in demand_list
        ]
        with DatabaseConnectionManager.get_connection() as conn:
            conn.executemany(query, data)
        self.logger.info(f"Batched insertion of {len(demand_list)} demand records succeeded.")

    def get_historical_demand(self, retailer_id: Optional[str] = None, product_id: Optional[str] = None) -> List[DemandHistory]:
        query = "SELECT id, retailer_id, product_id, date, quantity, price, weather, is_holiday FROM demand_history WHERE 1=1"
        params = []
        if retailer_id:
            query += " AND retailer_id = ?"
            params.append(retailer_id)
        if product_id:
            query += " AND product_id = ?"
            params.append(product_id)
        query += " ORDER BY date ASC"
        
        history = []
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                dt_str = row["date"]
                dt = date.fromisoformat(dt_str) if isinstance(dt_str, str) else dt_str
                history.append(DemandHistory(
                    id=row["id"], retailer_id=row["retailer_id"],
                    product_id=row["product_id"], date=dt,
                    quantity=row["quantity"], price=row["price"],
                    weather=row["weather"], is_holiday=row["is_holiday"]
                ))
        return history
#A
