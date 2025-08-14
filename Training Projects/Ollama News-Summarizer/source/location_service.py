import geocoder
from typing import Tuple, Dict, Optional
import json
import os

class LocationService:
    """
    This class provides functionality to get location information using IP geolocation
    or by utilizing a provided address dictionary. The class also supports caching 
    the location information to avoid repeated geolocation lookups.
    """

    def __init__(self) -> None:
        """
        Initializes the LocationService object. Sets up the cache file path for storing
        previously fetched location data.
        """
        self.cache_file = "config/location_cache.json"

    def _load_cache(self):
        """
        Loads the location cache from a file if it exists. This cache stores previously
        fetched location data to avoid unnecessary repeated geolocation lookups.

        Returns:
            None: Updates the `self.cache` attribute with the loaded cache data.
        """
        if os.path.exists(self.cache_file):
            # Load the cached location data from the file
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            # Initialize an empty cache if the cache file doesn't exist
            self.cache = {}

    def _save_cache(self):
        """
        Saves the current cache to the cache file. This ensures that cached location data
        persists between application restarts.

        Returns:
            None: Writes the current `self.cache` data to the cache file.
        """
        # Ensure the config directory exists before saving the cache
        os.makedirs("config", exist_ok=True)
        
        # Save the cache data to the JSON file
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get_location(self, address: Optional[Dict] = None) -> Dict:
        """
        Retrieves location information based on a given address dictionary or falls back
        to IP-based geolocation if no address is provided. It can also return a cached
        location if available.

        Args:
            address (Optional[Dict]): A dictionary containing address components like 
            city, state, and country.

        Returns:
            Dict: A dictionary containing location information including city, state,
            country, and optionally latitude and longitude.
        """
        # If an address is provided, extract relevant location details
        if address:
            city = (
                address.get("city") or
                address.get("town") or
                address.get("village") or
                address.get("municipality") or
                address.get("hamlet") or
                address.get("locality") or
                ""
            )
            state = address.get("state") or address.get("province") or ""
            country = address.get("country") or ""
            
            # Return the extracted location information as a dictionary
            return {
                "city": city,
                "state": state,
                "country": country,
                # "lat": user_override.get("lat", None),  # Latitude is not currently used
                # "lng": user_override.get("lng", None),  # Longitude is not currently used
            }
        
        # Fallback: Return a hardcoded location if no address is provided or geolocation fails
        location = {
            "city": "Edmonton",  # Default city
            "state": "AB",       # Default state/province
            "country": "Canada", # Default country
            "lat": 53.55014,     # Default latitude
            "lng": -113.46871,   # Default longitude
        }

        # Return the fallback location
        return location
