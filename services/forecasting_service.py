import logging
import pandas as pd
from datetime import date, timedelta
from typing import Dict, Any, List
from repositories.inventory_repo import InventoryRepository

logger = logging.getLogger("optilogix.service.forecasting")

class ForecastingService:
    def __init__(self) -> None:
        self.inventory_repo = InventoryRepository()
        self._forecast_cache = {}

    def clear_cache(self) -> None:
        self._forecast_cache.clear()
        logger.info("Forecast cache cleared.")

    def train_and_evaluate(self, retailer_id: str, product_id: str) -> Dict[str, Any]:
        from forecasting.pipeline import DemandForecaster
        records = self.inventory_repo.get_historical_demand(retailer_id, product_id)
        if not records:
            raise ValueError(f"No historical demand records found for retailer={retailer_id}, product={product_id}")
            
        data = [r.to_dict() for r in records]
        df = pd.DataFrame(data)
        
        metrics, _, _ = DemandForecaster.train_and_evaluate(df)
        
        logger.info(f"ML Demand model evaluation completed. RF R2={metrics['random_forest']['r2']}, Ridge R2={metrics['ridge']['r2']}")
        return metrics

    def forecast_demand(self, retailer_id: str, product_id: str, horizon_days: int = 7) -> List[Dict[str, Any]]:
        from forecasting.pipeline import DemandForecaster
        cache_key = (retailer_id, product_id, horizon_days)
        if cache_key in self._forecast_cache:
            return [dict(d) for d in self._forecast_cache[cache_key]]

        records = self.inventory_repo.get_historical_demand(retailer_id, product_id)
        if not records:
            fallback = [{"date": (date.today() + timedelta(days=i)).isoformat(), "forecast": 25.0} for i in range(horizon_days)]
            self._forecast_cache[cache_key] = fallback
            return [dict(d) for d in fallback]

        data = [r.to_dict() for r in records]
        df = pd.DataFrame(data)
        
        model = DemandForecaster.train_champion(df)
        
        future_forecasts = []
        last_date = date.today()
        
        for i in range(1, horizon_days + 1):
            future_date = last_date + timedelta(days=i)
            
            day_of_week = future_date.weekday()
            month = future_date.month
            day_of_year = future_date.timetuple().tm_yday
            is_holiday = 0
            
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
            
            std_error = 3.5
            margin = 1.96 * std_error
            
            future_forecasts.append({
                "date": future_date.isoformat(),
                "forecast": max(1.0, round(pred_qty, 2)),
                "lower_bound": max(0.0, round(pred_qty - margin, 2)),
                "upper_bound": round(pred_qty + margin, 2)
            })
            
        self._forecast_cache[cache_key] = future_forecasts
        return [dict(d) for d in future_forecasts]
#A
