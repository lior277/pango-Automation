import json
from pathlib import Path
from typing import List, Dict, Any


class TestDataLoader:
    @staticmethod
    def load_test_data(file_path: str) -> List[Dict[str, Any]]:
        """
        Load test data from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            List of dictionaries containing test data
        """
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    @staticmethod
    def create_sample_data():
        """
        Create sample cities.json if it doesn't exist.
        """
        # Create test data directory if it doesn't exist
        test_data_dir = Path(__file__).parent / "test_data"
        test_data_dir.mkdir(exist_ok=True)

        # Create sample test data if it doesn't exist
        cities_json_path = test_data_dir / "cities.json"
        if not cities_json_path.exists():
            sample_cities = [
                {"name": "London", "country": "GB"},
                {"name": "New York", "country": "US"},
                {"name": "Tokyo", "country": "JP"},
                {"name": "Sydney", "country": "AU"},
                {"name": "Moscow", "country": "RU"},
                {"name": "Paris", "country": "FR"},
                {"name": "Berlin", "country": "DE"},
                {"name": "Rome", "country": "IT"},
                {"name": "Beijing", "country": "CN"},
                {"name": "Cairo", "country": "EG"},
                {"name": "Rio de Janeiro", "country": "BR"},
                {"name": "Mexico City", "country": "MX"},
                {"name": "Los Angeles", "country": "US"},
                {"name": "Toronto", "country": "CA"},
                {"name": "Mumbai", "country": "IN"},
                {"name": "Bangkok", "country": "TH"},
                {"name": "Singapore", "country": "SG"},
                {"name": "Dubai", "country": "AE"},
                {"name": "Cape Town", "country": "ZA"},
                {"name": "Istanbul", "country": "TR"}
            ]
            with open(cities_json_path, 'w') as file:
                json.dump(sample_cities, file, indent=2)
            print(f"Created sample cities.json at {cities_json_path}")

        return cities_json_path