import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from config.settings import Settings

logger = logging.getLogger("smart_routing.database.manager")

sqlite3.register_converter("date", lambda b: datetime.strptime(b.decode(), "%Y-%m-%d").date())
sqlite3.register_converter("timestamp", lambda b: datetime.strptime(b.decode(), "%Y-%m-%d %H:%M:%S.%f") if b"." in b else datetime.strptime(b.decode(), "%Y-%m-%d %H:%M:%S"))

class DatabaseManager:
    
    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(Settings.DB_PATH),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def initialize_database(cls) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS route_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            start_lat REAL NOT NULL,
            start_lng REAL NOT NULL,
            dest_count INTEGER NOT NULL,
            traffic_intensity TEXT NOT NULL,
            weather TEXT NOT NULL,
            metrics_json TEXT NOT NULL
        );
        """
        try:
            with cls.get_connection() as conn:
                conn.execute(query)
                conn.commit()
            logger.info("SQLite Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite Database: {e}", exc_info=True)

    @classmethod
    def save_route_run(
        cls,
        start_lat: float,
        start_lng: float,
        dest_count: int,
        traffic_intensity: str,
        weather: str,
        metrics: List[Dict[str, Any]]
    ) -> None:
        query = """
        INSERT INTO route_runs (start_lat, start_lng, dest_count, traffic_intensity, weather, metrics_json)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            with cls.get_connection() as conn:
                conn.execute(query, (
                    start_lat, start_lng, dest_count,
                    traffic_intensity, weather, json.dumps(metrics)
                ))
                conn.commit()
            logger.info("Successfully logged route optimization run in database.")
        except Exception as e:
            logger.error(f"Failed to save route run to database: {e}", exc_info=True)

    @classmethod
    def get_historical_runs(cls, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT id, timestamp, start_lat, start_lng, dest_count, traffic_intensity, weather, metrics_json FROM route_runs ORDER BY timestamp DESC LIMIT ?;"
        runs = []
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (limit,))
                for row in cursor.fetchall():
                    runs.append({
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "start_lat": row["start_lat"],
                        "start_lng": row["start_lng"],
                        "dest_count": row["dest_count"],
                        "traffic_intensity": row["traffic_intensity"],
                        "weather": row["weather"],
                        "metrics": json.loads(row["metrics_json"])
                    })
        except Exception as e:
            logger.error(f"Failed to fetch historical runs: {e}", exc_info=True)
        return runs

    @classmethod
    def clear_history(cls) -> None:
        query = "DELETE FROM route_runs;"
        try:
            with cls.get_connection() as conn:
                conn.execute(query)
                conn.commit()
            logger.info("Cleared SQLite database history logs.")
        except Exception as e:
            logger.error(f"Failed to clear database logs: {e}", exc_info=True)

DatabaseManager.initialize_database()
#A
