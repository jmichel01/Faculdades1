import logging
import sqlite3
from database.connection import DatabaseConnectionManager

logger = logging.getLogger("optilogix.database.schema")

class DatabaseSchemaManager:
    
    @classmethod
    def init_database(cls) -> None:
        logger.info("Initializing SQLite database schemas...")
        
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT CHECK(role IN ('admin', 'analyst', 'viewer')) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS hubs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                capacity REAL NOT NULL,
                fixed_cost REAL NOT NULL,
                holding_cost REAL NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS retailers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin_id TEXT NOT NULL,
                destination_id TEXT NOT NULL,
                distance REAL NOT NULL,
                base_cost REAL NOT NULL,
                congestion_factor REAL DEFAULT 1.0,
                FOREIGN KEY (origin_id) REFERENCES hubs(id) ON DELETE CASCADE,
                FOREIGN KEY (destination_id) REFERENCES retailers(id) ON DELETE CASCADE,
                UNIQUE(origin_id, destination_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS demand_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                retailer_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                date DATE NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                weather TEXT DEFAULT 'Clear',
                is_holiday INTEGER DEFAULT 0,
                FOREIGN KEY (retailer_id) REFERENCES retailers(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS simulation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scenario_type TEXT CHECK(scenario_type IN ('Optimistic', 'Realistic', 'Pessimistic', 'Crisis')) NOT NULL,
                demand_multiplier REAL NOT NULL,
                cost_multiplier REAL NOT NULL,
                total_cost REAL NOT NULL,
                service_level REAL NOT NULL,
                stockout_rate REAL NOT NULL,
                avg_utilization REAL NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS optimization_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                solver_status TEXT NOT NULL,
                total_cost REAL NOT NULL,
                transport_cost REAL NOT NULL,
                holding_cost REAL NOT NULL,
                procurement_cost REAL NOT NULL,
                run_details TEXT NOT NULL
            );
            """
        ]
        
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_demand_history_lookup ON demand_history (retailer_id, product_id, date);",
            "CREATE INDEX IF NOT EXISTS idx_routes_nodes ON routes (origin_id, destination_id);"
        ]
        
        with DatabaseConnectionManager.get_connection() as conn:
            for query in queries:
                conn.execute(query)
            
            for idx_query in index_queries:
                conn.execute(idx_query)
                
        logger.info("SQLite database schema initialized successfully.")

    @classmethod
    def reset_database(cls) -> None:
        logger.warning("Dropping all SQLite database tables...")
        tables = ["routes", "demand_history", "hubs", "retailers", "users", "simulation_runs", "optimization_runs"]
        
        with DatabaseConnectionManager.get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = OFF;")
            for table in tables:
                conn.execute(f"DROP TABLE IF EXISTS {table};")
            conn.execute("PRAGMA foreign_keys = ON;")
            
        logger.info("All SQLite tables dropped. Reinitializing...")
        cls.init_database()
#A
