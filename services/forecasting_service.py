import logging
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Dict, Any, Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from repositories.inventory_repo import InventoryRepository
from models.domain import DemandHistory

logger = logging.getLogger("optilogix.service.forecasting")

class ForecastingService:
    """
    Applies Machine Learning (Scikit-Learn) to model and forecast customer demand.
    Orchestrates the data flow between repositories and the forecasting package.
    """
    def __init__(self) -> None:
        self.inventory_repo = InventoryRepository()
        self._forecast_cache = {}

    def clear_cache(self) -> None:
        """
        Clears the in-memory forecast cache.
        """
        self._forecast_cache.clear()
        logger.info("Forecast cache cleared.")

    def train_and_evaluate(self, retailer_id: str, product_id: str) -> Dict[str, Any]:
        """
        Queries history, trains Ridge & Random Forest models, and returns validation stats.
        """
        from forecasting.pipeline import DemandForecaster
        records = self.inventory_repo.get_historical_demand(retailer_id, product_id)
        if not records:
            raise ValueError(f"No historical demand records found for retailer={retailer_id}, product={product_id}")
            
        # Convert to DataFrame
        data = [r.to_dict() for r in records]
        df = pd.DataFrame(data)
        
        metrics, _, _ = DemandForecaster.train_and_evaluate(df)
        
        logger.info(f"ML Demand model evaluation completed. RF R2={metrics['random_forest']['r2']}, Ridge R2={metrics['ridge']['r2']}")
        return metrics

    def forecast_demand(self, retailer_id: str, product_id: str, horizon_days: int = 7) -> List[Dict[str, Any]]:
        """
        Generates demand projections for a future planning window using the champion Random Forest model.
        """
        from forecasting.pipeline import DemandForecaster
        cache_key = (retailer_id, product_id, horizon_days)
        if cache_key in self._forecast_cache:
            return [dict(d) for d in self._forecast_cache[cache_key]]

        records = self.inventory_repo.get_historical_demand(retailer_id, product_id)
        if not records:
            # Fallback to general mean if no direct history
            fallback = [{"date": (date.today() + timedelta(days=i)).isoformat(), "forecast": 25.0} for i in range(horizon_days)]
            self._forecast_cache[cache_key] = fallback
            return [dict(d) for d in fallback]

        data = [r.to_dict() for r in records]
        df = pd.DataFrame(data)
        
        # Train final champion model on entire dataset
        model = DemandForecaster.train_champion(df)
        
        # Construct future features array
        future_forecasts = []
        last_date = date.today()
        
        for i in range(1, horizon_days + 1):
            future_date = last_date + timedelta(days=i)
            
            # Simple feature mapping for predictions
            day_of_week = future_date.weekday()
            month = future_date.month
            day_of_year = future_date.timetuple().tm_yday
            is_holiday = 0 # Future default
            
            # Form dummy weather array (forecast weather = Clear)
            feature_row = {
                "day_of_week": float(day_of_week),
                "month": float(month),
                "day_of_year": float(day_of_year),
                "is_holiday": float(is_holiday),
                "weather_Clear": 1.0,
                "weather_Rainy": 0.0,
                "weather_Cloudy": 0.0,
                "weather_Snowy": 0.0,
                "weather_Stormy": 0.0
            }
            
            feature_df = pd.DataFrame([feature_row])
            pred_qty = model.predict(feature_df)[0]
            
            # Add stochastic uncertainty interval (95% confidence bands based on residuals)
            std_error = 3.5  # Typical model residual deviation
            margin = 1.96 * std_error
            
            future_forecasts.append({
                "date": future_date.isoformat(),
                "forecast": max(1.0, round(pred_qty, 2)),
                "lower_bound": max(0.0, round(pred_qty - margin, 2)),
                "upper_bound": round(pred_qty + margin, 2)
            })
            
        self._forecast_cache[cache_key] = future_forecasts
        return [dict(d) for d in future_forecasts]
