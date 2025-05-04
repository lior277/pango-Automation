import datetime
from typing import Dict, Any


class WeatherTestFixtures:
    @staticmethod
    def init_weather_test_data(request, city_name, city_id):
        request.node.weather_test_data = {
            "city_name": city_name,
            "city_id": city_id,
            "test_start_time": datetime.datetime.now().isoformat()
        }

    @staticmethod
    def store_weather_responses(request, ui_response, db_response):
        request.node.weather_test_data.update({
            "ui_temperature": getattr(ui_response, "temperature", None),
            "db_temperature": getattr(db_response, "temperature", None),
            "ui_humidity": getattr(ui_response, "humidity", None),
            "db_humidity": getattr(db_response, "humidity", None)
        })

    @staticmethod
    async def analyze_discrepancies(analyzer, db_response, ui_response, request, generate_text_report=False) -> Dict[
        str, Any]:
        # Run the analysis with the option to skip text report generation
        analysis_data = await analyzer.analyze_temperature_discrepancies(
            db_response=db_response,
            ui_response=ui_response,
            generate_text_report=generate_text_report
        )

        # Store analysis data for Hugging Face logging
        request.node.weather_test_data.update({
            "temperature_diff": analysis_data.get("temperature_diff", 0),
            "temperature_discrepancy": analysis_data.get("temperature_discrepancy", 0),
            "temperature_severity": analysis_data.get("temperature_severity", "LOW"),
            "temperature_status": analysis_data.get("temperature_status", "PASSED"),
            "is_significant": analysis_data.get("is_significant", False)
        })

        # Store the text report if it was generated
        if "text_report" in analysis_data:
            request.node.weather_test_data["analysis_report"] = analysis_data["text_report"]

        return analysis_data