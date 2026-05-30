import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from database.connection import DatabaseConnectionManager
from models.domain import SimulationRun, OptimizationRun
from repositories.base_repository import BaseRepository

class SimulationRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__("optilogix.repository.simulation")

    def save_simulation_run(self, run: SimulationRun) -> SimulationRun:
        query = """
            INSERT INTO simulation_runs (
                scenario_type, demand_multiplier, cost_multiplier, 
                total_cost, service_level, stockout_rate, avg_utilization
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING id, timestamp;
        """
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                run.scenario_type, run.demand_multiplier, run.cost_multiplier,
                run.total_cost, run.service_level, run.stockout_rate, run.avg_utilization
            ))
            row = cursor.fetchone()
            if row:
                run.id = row["id"]
                run.timestamp = datetime.fromisoformat(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"]
        return run

    def list_simulation_runs(self) -> List[SimulationRun]:
        query = """
            SELECT id, timestamp, scenario_type, demand_multiplier, cost_multiplier, 
                   total_cost, service_level, stockout_rate, avg_utilization 
            FROM simulation_runs ORDER BY timestamp DESC
        """
        runs = []
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                ts_str = row["timestamp"]
                ts = datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else ts_str
                runs.append(SimulationRun(
                    id=row["id"], timestamp=ts,
                    scenario_type=row["scenario_type"],
                    demand_multiplier=row["demand_multiplier"],
                    cost_multiplier=row["cost_multiplier"],
                    total_cost=row["total_cost"],
                    service_level=row["service_level"],
                    stockout_rate=row["stockout_rate"],
                    avg_utilization=row["avg_utilization"]
                ))
        return runs

    def save_optimization_run(self, run: OptimizationRun) -> OptimizationRun:
        query = """
            INSERT INTO optimization_runs (
                solver_status, total_cost, transport_cost, 
                holding_cost, procurement_cost, run_details
            ) VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id, timestamp;
        """
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                run.solver_status, run.total_cost, run.transport_cost,
                run.holding_cost, run.procurement_cost, run.run_details
            ))
            row = cursor.fetchone()
            if row:
                run.id = run["id"]
                run.timestamp = datetime.fromisoformat(row["timestamp"]) if isinstance(row["timestamp"], str) else row["timestamp"]
        return run

    def list_optimization_runs(self) -> List[OptimizationRun]:
        query = """
            SELECT id, timestamp, solver_status, total_cost, transport_cost, 
                   holding_cost, procurement_cost, run_details 
            FROM optimization_runs ORDER BY timestamp DESC
        """
        runs = []
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                ts_str = row["timestamp"]
                ts = datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else ts_str
                runs.append(OptimizationRun(
                    id=row["id"], timestamp=ts,
                    solver_status=row["solver_status"],
                    total_cost=row["total_cost"],
                    transport_cost=row["transport_cost"],
                    holding_cost=row["holding_cost"],
                    procurement_cost=row["procurement_cost"],
                    run_details=row["run_details"]
                ))
        return runs
#A
