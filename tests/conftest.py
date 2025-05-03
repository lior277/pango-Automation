import pytest

from automation_framework.WeatherDiscrepancyAnalyzer import WeatherDiscrepancyAnalyzer
from automation_framework.config.manager import ConfigManager
from automation_framework.utilities.db_helpers import DatabaseHelper
from objects.objects_api.weather_page_api import WeatherPageApi
from objects.objects_ui.weather_page_ui import WeatherPageUi
from tests.test_suit_Base import TestSuitBase


@pytest.fixture(scope="class")
def config_manager():
    return ConfigManager()


@pytest.fixture(scope="class")
def db_helper(config_manager):
    # Create and return the database helper
    db_helper = DatabaseHelper(config_manager)

    yield db_helper

    db_helper.close_connection()


@pytest.fixture(scope="class")
def api_client():

    return WeatherPageApi()


@pytest.fixture(scope="class")
def driver():
    # Create the driver using TestSuitBase
    driver = TestSuitBase.get_driver()

    # Yield the driver for use in tests
    yield driver

    # Clean up after tests complete
    TestSuitBase.driver_dispose(driver)


@pytest.fixture(scope="class")
def ui_client(driver):
    # Create and return UI client with the driver
    return WeatherPageUi(driver)

@pytest.fixture(scope="class")
def weather_discrepancy_analyzer():

    return WeatherDiscrepancyAnalyzer()