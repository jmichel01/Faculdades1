import math
from typing import Tuple

class GeoHelpers:
    """
    Geographical calculation and time-distance format conversions.
    """
    
    @staticmethod
    def format_time_hours(hours: float) -> str:
        """
        Formats decimal hours into a readable string like '2h 15m' or '45m 12s'.
        """
        total_seconds = int(hours * 3600.0)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        
        if h > 0:
            return f"{h}h {m}m"
        elif m > 0:
            return f"{m}m {s}s"
        else:
            return f"{s}s"

    @staticmethod
    def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates the bearing angle from point 1 to point 2.
        Returns bearing in degrees (0 = North, 90 = East, etc).
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        diff_long = math.radians(lon2 - lon1)
        
        x = math.sin(diff_long) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - (math.sin(lat1_rad) *
                math.cos(lat2_rad) * math.cos(diff_long))
                
        initial_bearing = math.atan2(x, y)
        
        # Normalize to 0-360 degrees
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        
        return round(compass_bearing, 1)
