import logging
import pandas as pd
from typing import Dict, Any, List

logger = logging.getLogger("smart_routing.analytics.processor")

class AnalyticsProcessor:
    """
    Processes historical route runs logs to generate statistics, trends, and rankings.
    """
    
    @staticmethod
    def get_summary_stats(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes general summaries over historical sessions.
        """
        if not runs:
            return {
                "total_runs": 0,
                "avg_distance": 0.0,
                "most_frequent_weather": "N/A",
                "most_frequent_traffic": "N/A"
            }
            
        df = pd.DataFrame(runs)
        
        # Calculate average distance from metrics
        all_distances = []
        for run in runs:
            for metric in run["metrics"]:
                all_distances.append(metric["distance_km"])
                
        avg_dist = sum(all_distances) / len(all_distances) if all_distances else 0.0
        
        return {
            "total_runs": len(runs),
            "avg_distance": round(avg_dist, 2),
            "most_frequent_weather": df["weather"].mode()[0] if not df["weather"].empty else "N/A",
            "most_frequent_traffic": df["traffic_intensity"].mode()[0] if not df["traffic_intensity"].empty else "N/A"
        }

    @staticmethod
    def get_vehicle_performance_rankings(runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregates average performance values per vehicle mode.
        """
        if not runs:
            return []
            
        records = []
        for run in runs:
            for m in run["metrics"]:
                records.append({
                    "vehicle": m["vehicle"],
                    "time_hours": m["time_hours"],
                    "fuel_cost_usd": m["fuel_cost_usd"],
                    "co2_emissions_g": m["co2_emissions_g"],
                    "sustainability_score": m["sustainability_score"]
                })
                
        df = pd.DataFrame(records)
        if df.empty:
            return []
            
        # Group by vehicle type and calculate averages
        grouped = df.groupby("vehicle").mean().reset_index()
        
        rankings = []
        for _, row in grouped.iterrows():
            rankings.append({
                "vehicle": row["vehicle"],
                "avg_time_mins": round(row["time_hours"] * 60.0, 1),
                "avg_cost_usd": round(row["fuel_cost_usd"], 2),
                "avg_co2_g": round(row["co2_emissions_g"], 1),
                "sustainability_score": int(row["sustainability_score"])
            })
            
        # Sort by speed/time by default
        return sorted(rankings, key=lambda x: x["avg_time_mins"])

    @staticmethod
    def get_peak_hour_comparison(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compares average travel times and fuel costs between peak and non-peak configurations.
        """
        if not runs:
            return {"peak_avg_time_mins": 0.0, "offpeak_avg_time_mins": 0.0, "time_inflation_pct": 0.0}
            
        peak_times = []
        offpeak_times = []
        
        for run in runs:
            is_peak = run["traffic_intensity"] in ["High", "Peak Hour"]
            for m in run["metrics"]:
                if m["vehicle"] == "Carro":  # Use Carro as the benchmark
                    if is_peak:
                        peak_times.append(m["time_hours"] * 60.0)
                    else:
                        offpeak_times.append(m["time_hours"] * 60.0)
                        
        avg_peak = sum(peak_times) / len(peak_times) if peak_times else 0.0
        avg_offpeak = sum(offpeak_times) / len(offpeak_times) if offpeak_times else 0.0
        
        inflation = 0.0
        if avg_offpeak > 0:
            inflation = ((avg_peak - avg_offpeak) / avg_offpeak) * 100.0
            
        return {
            "peak_avg_time_mins": round(avg_peak, 1),
            "offpeak_avg_time_mins": round(avg_offpeak, 1),
            "time_inflation_pct": round(inflation, 1)
        }
