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

        # Set default reporting preferences if not in config
        if not self.config.has_section('REPORTING'):
            self.config.add_section('REPORTING')
            self.config.set('REPORTING', 'TYPE', 'html')
            self.config.set('REPORTING', 'HUGGING_FACE_PROJECT', 'pango-weather-automation')
            self.config.set('REPORTING', 'GENERATE_TEXT_REPORTS', 'False')

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

    def get_hugging_face_api_key(self) -> str:
        return self.config.get('LOGGER', 'HUGGING_FACE_API_KEY')

    def get_reporting_type(self) -> str:
        return self.config.get('REPORTING', 'TYPE', fallback='html')

    def use_hugging_face(self) -> bool:
        report_type = self.get_reporting_type().lower()
        return report_type in ['huggingface', 'both']

    def use_html_report(self) -> bool:
        report_type = self.get_reporting_type().lower()
        return report_type in ['html', 'both']

    def get_hugging_face_project(self) -> str:
        return self.config.get('REPORTING', 'HUGGING_FACE_PROJECT',
                               fallback='pango-weather-automation')

    def generate_text_reports(self) -> bool:
        return self.config.getboolean('REPORTING', 'GENERATE_TEXT_REPORTS', fallback=False)