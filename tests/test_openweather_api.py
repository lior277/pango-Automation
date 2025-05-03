import pytest

from tests.test_data.popular_cities import city_data


class TestWeatherApiWithCityIds:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("city_info", city_data)
    async def test_get_weather_by_city_id(self, city_info, api_client, db_helper):

        city_name = city_info["city"]
        city_id = str(city_info["id"])

        print(f"\nTesting weather data for {city_name} (ID: {city_id})")

        try:
            # Call the API to get weather data by city ID
            weather_response = await api_client.get_weather_data_by_city_id(city_id)
            highest_average = db_helper.get_city_with_highest_average_temperature()

            print(f"the highest average temperature is "
                  f"{highest_average.city_name} with {highest_average.average_temperature}°C")

            # ADDED: Verify data inserted into the database matches the API response
            stored_data = db_helper.get_all_weather_data()
            matching_record = next(
                (record for record in stored_data if record.city_name == city_name),
                None
            )

            # Assert that database data matches API response
            assert abs(matching_record.temperature - weather_response.temperature) < 0.001, \
                f"Temperature mismatch for {city_name}: DB={matching_record.temperature}, API={weather_response.temperature}"

            assert abs(matching_record.feels_like - weather_response.feels_like) < 0.001, \
                f"Feels like temperature mismatch for {city_name}: DB={matching_record.feels_like}, API={weather_response.feels_like}"

            print(f"Database validation successful for {city_name} - Data matches API response")

        except Exception as e:
            pytest.fail(f"Test failed for {city_name}: {str(e)}")
