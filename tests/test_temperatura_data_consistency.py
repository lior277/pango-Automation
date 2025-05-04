import pytest

from tests.conftest import init_weather_test_data, store_weather_responses
from tests.test_data.popular_cities import city_data
from tests.test_suit_Base import TestSuitBase


class TestTemperaturaDataConsistency(TestSuitBase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("city_info", city_data)
    async def test_get_weather_by_city_id(self, city_info,
                                          db_helper, ui_client,
                                          weather_discrepancy_analyzer, config_manager, driver,
                                          hf_logger, request, analyze_discrepancies):

        driver.get(config_manager.get_ui_weather_url())
        city_name = city_info["city"]
        city_id = str(city_info["id"])

        print(f"\nTesting weather data for {city_name} (ID: {city_id})")

        # Initialize test data
        init_weather_test_data(request, city_name, city_id)

        # Get weather data from UI and DB
        weather_response_ui = await ui_client.get_temperatura_data_by_city_name(city_name)
        weather_response_db = db_helper.get_weather_data_by_city_name(city_name)

        # Store response data
        store_weather_responses(request, weather_response_ui, weather_response_db)

        # Analyze discrepancies (this also stores analysis data for HF logging)
        await analyze_discrepancies(
            weather_discrepancy_analyzer,
            weather_response_db,
            weather_response_ui,
            request
        )