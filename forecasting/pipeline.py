import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

class DemandForecaster:
    @staticmethod
    def prepare_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        df["date"] = pd.to_datetime(df["date"])
        
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month
        df["day_of_year"] = df["date"].dt.dayofyear
        
        weather_dummies = pd.get_dummies(df["weather"], prefix="weather", drop_first=False)
        
        standard_weathers = ["weather_Clear", "weather_Rainy", "weather_Cloudy", "weather_Snowy", "weather_Stormy"]
        for col in standard_weathers:
            if col not in weather_dummies.columns:
                weather_dummies[col] = 0
                
        X = pd.concat([
            df[["day_of_week", "month", "day_of_year", "is_holiday"]],
            weather_dummies[standard_weathers]
        ], axis=1)
        
        y = df["quantity"]
        
        return X.astype(float), y

    @classmethod
    def train_and_evaluate(cls, df: pd.DataFrame) -> Tuple[Dict[str, Any], RandomForestRegressor, Ridge]:
        X, y = cls.prepare_features(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        ridge = Ridge(alpha=1.0)
        ridge.fit(X_train, y_train)
        y_pred_ridge = ridge.predict(X_test)
        
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        y_pred_rf = rf.predict(X_test)
        
        metrics = {
            "ridge": {
                "mae": round(mean_absolute_error(y_test, y_pred_ridge), 3),
                "rmse": round(root_mean_squared_error(y_test, y_pred_ridge), 3),
                "r2": round(r2_score(y_test, y_pred_ridge), 3)
            },
            "random_forest": {
                "mae": round(mean_absolute_error(y_test, y_pred_rf), 3),
                "rmse": round(root_mean_squared_error(y_test, y_pred_rf), 3),
                "r2": round(r2_score(y_test, y_pred_rf), 3)
            }
        }
        return metrics, rf, ridge

    @classmethod
    def train_champion(cls, df: pd.DataFrame) -> RandomForestRegressor:
        X, y = cls.prepare_features(df)
        model = RandomForestRegressor(n_estimators=120, random_state=42)
        model.fit(X, y)
        return model
#A
