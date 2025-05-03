import configparser
import os


class ConfigManager:
    def __init__(self, config_path='config.ini'):
        # Direct path to config.ini in automation_framework/config
        framework_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        actual_config_path = os.path.join(framework_dir, 'config', config_path)

        if not os.path.exists(actual_config_path):
            raise FileNotFoundError(f"Configuration file not found at {actual_config_path}")

        self.config = configparser.ConfigParser()
        self.config.read(actual_config_path)

    def get_api_base_url(self) -> str:
        return self.config.get('API', 'BASE_URL')

    def get_api_key(self) -> str:
        return self.config.get('API', 'API_KEY')

    def get_db_name(self) -> str:
        return self.config.get('DB', 'DB_NAME')

    def get_ui_weather_url(self) -> str:
        return self.config.get('UI', 'WEATHER_URL')

    def get_selenium_timeout(self) -> int:
        return int(self.config.get('UI', 'TIME_TO_WAIT_IN_SECONDS'))