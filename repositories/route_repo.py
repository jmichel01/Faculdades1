import sqlite3
from typing import List, Optional
from database.connection import DatabaseConnectionManager
from models.domain import Route
from repositories.base_repository import BaseRepository

class RouteRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("optilogix.repository.route")

    def save_route(self, route: Route) -> Route:
        query = """
            INSERT INTO routes (origin_id, destination_id, distance, base_cost, congestion_factor)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(origin_id, destination_id) DO UPDATE SET
                distance = excluded.distance,
                base_cost = excluded.base_cost,
                congestion_factor = excluded.congestion_factor
            RETURNING id;
        """
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                route.origin_id, route.destination_id,
                route.distance, route.base_cost, route.congestion_factor
            ))
            row = cursor.fetchone()
            if row:
                route.id = row["id"]
        return route

    def list_routes(self) -> List[Route]:
        query = "SELECT id, origin_id, destination_id, distance, base_cost, congestion_factor FROM routes"
        routes = []
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                routes.append(Route(
                    id=row["id"], origin_id=row["origin_id"],
                    destination_id=row["destination_id"], distance=row["distance"],
                    base_cost=row["base_cost"], congestion_factor=row["congestion_factor"]
                ))
        return routes

    def get_route_by_nodes(self, origin_id: str, destination_id: str) -> Optional[Route]:
        query = """
            SELECT id, origin_id, destination_id, distance, base_cost, congestion_factor 
            FROM routes 
            WHERE origin_id = ? AND destination_id = ?
        """
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (origin_id, destination_id))
            row = cursor.fetchone()
            if row:
                return Route(
                    id=row["id"], origin_id=row["origin_id"],
                    destination_id=row["destination_id"], distance=row["distance"],
                    base_cost=row["base_cost"], congestion_factor=row["congestion_factor"]
                )
        return None

    def delete_all_routes(self) -> None:
        query = "DELETE FROM routes"
        with DatabaseConnectionManager.get_connection() as conn:
            conn.execute(query)
        self.logger.info("Cleared all route instances from SQLite database.")
#A
