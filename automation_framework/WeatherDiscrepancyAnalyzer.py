# automation_framework/utilities/WeatherDiscrepancyAnalyzer.py
import datetime
from typing import List, Tuple, Dict, Any

from objects.data_classes.get_weather_response import WeatherResponse


class WeatherDiscrepancyAnalyzer:
    _discrepancies = []

    _city_thresholds = {
        "California": 10.0,
        "Johannesburg": 10.0,
        "Minnesota": 10.0,
        "default": 5.0
    }

    @staticmethod
    async def analyze_temperature_discrepancies(db_response: WeatherResponse,
                                                ui_response: WeatherResponse,
                                                generate_text_report: bool = False) -> Dict[str, Any]:
        city_name = db_response.city_name
        db_temp = float(db_response.temperature)
        ui_temp = float(ui_response.temperature)
        db_feels_like = float(db_response.feels_like)
        ui_feels_like = float(ui_response.feels_like)

        temp_discrepancy = abs(db_temp - ui_temp)
        feels_like_discrepancy = abs(db_feels_like - ui_feels_like)

        threshold = WeatherDiscrepancyAnalyzer._city_thresholds.get(
            city_name, WeatherDiscrepancyAnalyzer._city_thresholds["default"])

        temp_percentage = WeatherDiscrepancyAnalyzer._calculate_percentage(temp_discrepancy, db_temp)
        feels_like_percentage = WeatherDiscrepancyAnalyzer._calculate_percentage(feels_like_discrepancy, db_feels_like)

        temp_severity = WeatherDiscrepancyAnalyzer._determine_severity(temp_discrepancy)
        temp_status = "PASSED" if temp_discrepancy <= threshold else "FAILED"
        feels_like_status = "PASSED" if feels_like_discrepancy <= threshold else "FAILED"

        analysis_data = {
            "city_name": city_name,
            "db_temperature": db_temp,
            "ui_temperature": ui_temp,
            "temperature_diff": db_temp - ui_temp,
            "temperature_discrepancy": temp_discrepancy,
            "temperature_percentage": temp_percentage,
            "temperature_severity": temp_severity,
            "temperature_status": temp_status,
            "db_feels_like": db_feels_like,
            "ui_feels_like": ui_feels_like,
            "feels_like_diff": db_feels_like - ui_feels_like,
            "feels_like_discrepancy": feels_like_discrepancy,
            "feels_like_percentage": feels_like_percentage,
            "feels_like_severity": WeatherDiscrepancyAnalyzer._determine_severity(feels_like_discrepancy),
            "feels_like_status": feels_like_status,
            "threshold": threshold,
            "is_significant": temp_discrepancy > threshold or feels_like_discrepancy > threshold,
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }

        WeatherDiscrepancyAnalyzer._discrepancies.append(
            (city_name, db_temp, ui_temp, temp_discrepancy,
             db_feels_like, ui_feels_like, feels_like_discrepancy, threshold)
        )

        if generate_text_report:
            report = WeatherDiscrepancyAnalyzer._generate_discrepancy_report()
            analysis_data["text_report"] = report
            print("\n---- Temperature Discrepancy Report ----\n" + report)
        else:
            print(f"\n---- Temp Analysis {city_name} ----")
            print(f"Temp: DB={db_temp} UI={ui_temp} Diff={temp_discrepancy} ({temp_severity})")

        return analysis_data

    @staticmethod
    def _determine_severity(discrepancy: float) -> str:
        if discrepancy > 5.0:
            return "CRITICAL"
        elif discrepancy > 3.0:
            return "HIGH"
        elif discrepancy > 1.0:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _calculate_percentage(value: float, reference: float) -> float:
        return (value / abs(reference) * 100) if reference != 0 else 0

    @staticmethod
    def _generate_discrepancy_report() -> str:
        return "\n".join([f"City: {d[0]}, Temp diff: {d[3]}" for d in WeatherDiscrepancyAnalyzer._discrepancies])

    @staticmethod
    def get_discrepancies_summary() -> Dict[str, Any]:
        if not WeatherDiscrepancyAnalyzer._discrepancies:
            return {"total_cities": 0, "has_data": False}

        temp_discrepancies = [d[3] for d in WeatherDiscrepancyAnalyzer._discrepancies]
        avg_temp = sum(temp_discrepancies) / len(temp_discrepancies)
        max_temp = max(temp_discrepancies)
        min_temp = min(temp_discrepancies)

        return {
            "has_data": True,
            "total_cities": len(temp_discrepancies),
            "avg_temp_discrepancy": avg_temp,
            "max_temp_discrepancy": max_temp,
            "min_temp_discrepancy": min_temp,
            "timestamp": datetime.datetime.now().isoformat()
        }

    @staticmethod
    def export_discrepancies_as_json(filepath="logs/discrepancies.json"):
        import json
        keys = ["city_name", "db_temp", "ui_temp", "temp_discrepancy",
                "db_feels_like", "ui_feels_like", "feels_like_discrepancy", "threshold"]
        data = [dict(zip(keys, d)) for d in WeatherDiscrepancyAnalyzer._discrepancies]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def reset_discrepancies():
        WeatherDiscrepancyAnalyzer._discrepancies = []
