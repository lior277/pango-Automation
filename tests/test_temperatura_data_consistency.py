import pytest

from tests.test_data.popular_cities import city_data
from tests.test_suit_Base import TestSuitBase


class TestWeatherApiWithCityIds(TestSuitBase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("city_info", city_data)
    async def test_get_weather_by_city_id(self, city_info,
                                          db_helper, ui_client,
                                          weather_discrepancy_analyzer, config_manager, driver):

        driver.get(config_manager.get_ui_weather_url())
        city_name = city_info["city"]
        city_id = str(city_info["id"])

        print(f"\nTesting weather data for {city_name} (ID: {city_id})")

        try:
            # Call the API to get weather data by city ID
            weather_response_ui = await ui_client.get_temperatura_data_by_city_name(city_name)
            weather_response_db = db_helper.get_weather_data_by_city_name(city_name)

            report = await weather_discrepancy_analyzer.analyze_temperature_discrepancies(
                db_response=weather_response_db,
                ui_response=weather_response_ui
            )

            print("\n---- Temperature Discrepancy Report ----")
            print(report)

        except Exception as e:
            pytest.fail(f"Test failed for {city_name}: {str(e)}")
