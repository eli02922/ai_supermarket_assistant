from typing import List, Dict, Any, Optional
import random
from .base_generator import BaseDataGenerator
from src.core.logging import get_logger

logger = get_logger(__name__)


class StoreGenerator(BaseDataGenerator):
    """Store data generator"""

    def __init__(self, num_stores: int = 10, seed: Optional[int] = None):
        super().__init__(seed)
        self.num_stores = num_stores

        self.store_chains = {
            "Puregold": {"cities": ["Manila", "Quezon City", "Makati", "Pasig", "Taguig"]},
            "SM Markets": {"cities": ["Manila", "Pasay", "Muntinlupa", "Paranaque", "Las Pinas"]},
            "Robinsons": {"cities": ["Manila", "Mandaluyong", "Pasig", "Cainta", "Antipolo"]},
            "Walmart": {"cities": ["Taguig", "Makati", "BGC", "Manila", "Pasig"]}
        }

    def generate_batch(
        self, batch_size: int = 100, **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate store records"""
        stores = []
        chains = list(self.store_chains.keys())

        for i in range(min(batch_size, self.num_stores - len(stores))):
            chain = random.choice(chains)
            city = random.choice(self.store_chains[chain]["cities"])

            store = {
                "id": self._generate_id(),
                "code": f"{chain[:2].upper()}{random.randint(100, 999)}",
                "name": f"{chain} {city} {self._generate_suffix()}",
                "address": fake.street_address(),
                "city": city,
                "province": self._get_province(city),
                "region": self._get_region(city),
                "store_type": random.choice(["Supermarket", "Hypermarket", "Express", "Neighborhood"]),
                "floor_area_sqm": random.randint(500, 5000),
                "parking_capacity": random.randint(10, 200),
                "opening_hours": "8:00 AM - 9:00 PM",
                "latitude": self._generate_lat_lon(city)[0],
                "longitude": self._generate_lat_lon(city)[1],
            }
            stores.append(store)

        logger.info(f"Generated {len(stores)} stores")
        return stores

    def _generate_suffix(self) -> str:
        """Generate store suffix"""
        suffixes = ["Branch", "Store", "Market", "Mall", "Plaza", "Center", "Hub"]
        return random.choice(suffixes)

    def _get_province(self, city: str) -> str:
        """Get province from city"""
        provinces = {
            "Manila": "Metro Manila",
            "Quezon City": "Metro Manila",
            "Makati": "Metro Manila",
            "Pasig": "Metro Manila",
            "Taguig": "Metro Manila",
            "Pasay": "Metro Manila",
            "Muntinlupa": "Metro Manila",
            "Paranaque": "Metro Manila",
            "Las Pinas": "Metro Manila",
            "Mandaluyong": "Metro Manila",
            "Cainta": "Rizal",
            "Antipolo": "Rizal",
            "BGC": "Metro Manila",
        }
        return provinces.get(city, "Metro Manila")

    def _get_region(self, city: str) -> str:
        """Get region from city"""
        regions = {
            "Manila": "NCR",
            "Quezon City": "NCR",
            "Makati": "NCR",
            "Pasig": "NCR",
            "Taguig": "NCR",
            "Pasay": "NCR",
            "Muntinlupa": "NCR",
            "Paranaque": "NCR",
            "Las Pinas": "NCR",
            "Mandaluyong": "NCR",
            "Cainta": "Region IV-A",
            "Antipolo": "Region IV-A",
            "BGC": "NCR",
        }
        return regions.get(city, "NCR")

    def _generate_lat_lon(self, city: str) -> tuple:
        """Generate latitude and longitude for a city"""
        city_coords = {
            "Manila": (14.5995, 120.9842),
            "Quezon City": (14.6760, 121.0437),
            "Makati": (14.5547, 121.0244),
            "Pasig": (14.5764, 121.0851),
            "Taguig": (14.5243, 121.0792),
            "Pasay": (14.5378, 121.0014),
            "Muntinlupa": (14.4070, 121.0514),
            "Paranaque": (14.4973, 121.0168),
            "Las Pinas": (14.4504, 121.0168),
            "Mandaluyong": (14.5794, 121.0359),
            "Cainta": (14.5804, 121.1194),
            "Antipolo": (14.5867, 121.1756),
            "BGC": (14.5510, 121.0550),
        }
        lat, lon = city_coords.get(city, (14.5995, 120.9842))
        # Add small random offset
        lat += random.uniform(-0.01, 0.01)
        lon += random.uniform(-0.01, 0.01)
        return (round(lat, 6), round(lon, 6))