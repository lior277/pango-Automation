import os
import sqlite3
from typing import List, Optional

from automation_framework.config.manager import ConfigManager
from objects.data_classes.get_weather_response import WeatherResponse


class DatabaseHelper:
    def __init__(self, config_manager: ConfigManager = None):
        self.config_manager = config_manager or ConfigManager()

        # Get shared DB path from env or config
        db_name = DatabaseHelper.get_shared_db_path(self.config_manager)
        self.db_path = os.path.abspath(db_name)

        # Ensure directory exists (handles relative or subdir paths)
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)

        print(f"[DatabaseHelper] Using DB: {self.db_path} | Exists: {os.path.exists(self.db_path)}")

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    @staticmethod
    def get_shared_db_path(config_manager: Optional[ConfigManager] = None) -> str:
        """Return the consistent DB path used across all test layers"""
        config_manager = config_manager or ConfigManager()
        return os.environ.get("WEATHER_DB_PATH", config_manager.get_db_name())

    def create_tables(self):
        """Create the weather_data table if it doesn't exist"""
        with self.conn:
            # Use the existing schema: city_name, temperature, feels_like, average_temperature
            self.conn.execute('''CREATE TABLE IF NOT EXISTS weather_data (
              city_name TEXT PRIMARY KEY,
              temperature REAL,
              feels_like REAL,
              average_temperature REAL
          )''')

    def _city_exists(self, city_name: str) -> bool:
        """Check if a city exists in the database"""
        try:
            self.cursor.execute('''
               SELECT COUNT(*) 
               FROM weather_data 
               WHERE city_name = ?
           ''', (city_name,))

            return self.cursor.fetchone()[0] > 0

        except sqlite3.Error as e:
            print(f"Error checking city existence: {e}")
            return False

    def insert_weather_data(self, weather_responses: List[WeatherResponse]):
        """Insert or update weather data for multiple cities"""
        try:
            for weather_response in weather_responses:
                # Check if city exists
                exists = self._city_exists(weather_response.city_name)

                # Calculate average temperature directly
                avg_temp = (weather_response.temp_min + weather_response.temp_max) / 2

                if exists:
                    # Update existing record - using existing schema
                    with self.conn:
                        self.conn.execute('''
                           UPDATE weather_data 
                           SET temperature = ?, 
                               feels_like = ?, 
                               average_temperature = ?
                           WHERE city_name = ?
                       ''', (
                            weather_response.temperature,
                            weather_response.feels_like,
                            avg_temp,
                            weather_response.city_name
                        ))
                else:
                    # Insert new record - using existing schema
                    with self.conn:
                        self.conn.execute('''
                           INSERT INTO weather_data 
                           (city_name, temperature, feels_like, average_temperature)
                           VALUES (?, ?, ?, ?)
                       ''', (
                            weather_response.city_name,
                            weather_response.temperature,
                            weather_response.feels_like,
                            avg_temp
                        ))

                print(f"Successfully inserted/updated data for {weather_response.city_name}")

        except sqlite3.Error as e:
            print(f"Error inserting weather data: {e}")
            self.conn.rollback()

    def get_all_weather_data(self) -> List[WeatherResponse]:
        """Get all weather data from the database"""
        try:
            self.cursor.execute('''
              SELECT city_name, temperature, feels_like, average_temperature 
              FROM weather_data
          ''')

            results = self.cursor.fetchall()

            if not results:
                print("No weather data found in database")
                return []

            # Create WeatherResponse objects from database records
            return [
                WeatherResponse(
                    city_name=result[0],
                    temperature=result[1],
                    feels_like=result[2],
                    temp_min=0.0,  # Not stored in DB, use default
                    temp_max=0.0,  # Not stored in DB, use default
                    average_temperature=result[3]
                )
                for result in results
            ]

        except sqlite3.Error as e:
            print(f"Error retrieving all weather data: {e}")
            return []  # Return empty list instead of raising exception


    def get_weather_data_by_city_name(self, city_name: str) -> WeatherResponse:
        try:
            self.cursor.execute('''
                SELECT city_name, temperature, feels_like, average_temperature 
                FROM weather_data 
                WHERE city_name = ?
            ''', (city_name,))

            result = self.cursor.fetchone()

            if result:
                return WeatherResponse(
                    city_name=result[0],
                    temperature=result[1],
                    feels_like=result[2],
                    temp_min=0.0,  # Not stored in DB, use default
                    temp_max=0.0,  # Not stored in DB, use default
                    average_temperature=result[3]
                )

            # City not found
            print(f"No weather data found for city: {city_name}")
            return None

        except sqlite3.Error as e:
            print(f"Error retrieving weather data for city {city_name}: {e}")
            return None

    def get_city_with_highest_average_temperature(self) -> Optional[WeatherResponse]:
        """Get the city with the highest average temperature"""
        try:
            self.cursor.execute('''
                SELECT city_name, temperature, feels_like, average_temperature 
                FROM weather_data 
                ORDER BY average_temperature DESC 
                LIMIT 1
            ''')

            result = self.cursor.fetchone()

            if result:
                return WeatherResponse(
                    city_name=result[0],
                    temperature=result[1],
                    feels_like=result[2],
                    temp_min=0.0,  # Not stored in DB, use default
                    temp_max=0.0,  # Not stored in DB, use default
                    average_temperature=result[3]
                )

            # No data found, return None instead of raising exception
            print("No weather data available")
            return None

        except sqlite3.Error as e:
            print(f"Error retrieving highest average temperature city: {e}")
            return None

    def close_connection(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()