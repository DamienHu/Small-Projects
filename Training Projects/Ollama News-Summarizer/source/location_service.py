import geocoder
from typing import Tuple, Dict,Optional
import json
import os

class LocationService:
    def __init__(self) -> None:
        self.cache_file = "config/location_cache.json"
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def _save_cache(self):
        os.makedirs("config", exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get_location(self, user_override:Optional[Dict]=None)->Dict:
        """Get location info using IP geolocation"""
        if user_override:
            return{
                "city": user_override.get("city",""),
                "state": user_override.get("state",""),
                "country": user_override.get("country",""),
                "lat": user_override.get("lat",None),
                "lng": user_override.get("lng",None)
            }
        #Existing IP geolocation logic or hardcoded fallback
        location = {
            "city": "Edmonton",
            "state": "AB",
            "country": "Canada",
            "lat": 53.55014,
            "lng": -113.46871,
        }
        return location
    
