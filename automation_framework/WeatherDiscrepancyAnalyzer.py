import datetime
from typing import List, Tuple

from objects.data_classes.get_weather_response import WeatherResponse


class WeatherDiscrepancyAnalyzer:
    # Static list to store discrepancies across multiple calls
    _discrepancies = []

    # City-specific thresholds
    _city_thresholds = {
        "California": 10.0,
        "Johannesburg": 10.0,
        "Minnesota": 10.0,
        "default": 5.0  # Default threshold for other cities
    }

    @staticmethod
    async def analyze_temperature_discrepancies(db_response: WeatherResponse,
                                                ui_response: WeatherResponse) -> str:
        city_name = db_response.city_name

        # Extract temperatures
        db_temp = float(db_response.temperature)
        ui_temp = float(ui_response.temperature)

        # Extract feels like temperatures
        db_feels_like = float(db_response.feels_like)
        ui_feels_like = float(ui_response.feels_like)

        # Calculate discrepancies
        temp_discrepancy = abs(db_temp - ui_temp)
        feels_like_discrepancy = abs(db_feels_like - ui_feels_like)

        # Get city-specific thresholds
        threshold = WeatherDiscrepancyAnalyzer._city_thresholds.get(
            city_name, WeatherDiscrepancyAnalyzer._city_thresholds["default"])

        # Add this city's discrepancy to the running list
        # Include both temperature and feels_like discrepancies
        WeatherDiscrepancyAnalyzer._discrepancies.append(
            (city_name, db_temp, ui_temp, temp_discrepancy,
             db_feels_like, ui_feels_like, feels_like_discrepancy, threshold)
        )

        # Generate and return report with all discrepancies collected so far
        return WeatherDiscrepancyAnalyzer._generate_discrepancy_report()

    @staticmethod
    def _generate_discrepancy_report() -> str:
        # Use the stored discrepancies list
        discrepancies = WeatherDiscrepancyAnalyzer._discrepancies

        # Generate report header
        report = WeatherDiscrepancyAnalyzer._generate_report_header(discrepancies)

        # Generate city details section
        report += WeatherDiscrepancyAnalyzer._generate_city_details(discrepancies)

        # Generate summary statistics if there are discrepancies
        if discrepancies:
            report += WeatherDiscrepancyAnalyzer._generate_summary_statistics(discrepancies)

        # Generate report footer
        report += "=" * 75 + "\n"
        report += f"Analysis completed for {len(discrepancies)} cities."

        return report

    @staticmethod
    def _generate_report_header(discrepancies: List[Tuple]) -> str:
        report = "\n" + "=" * 75 + "\n"
        report += "TEMPERATURE DISCREPANCY ANALYSIS REPORT\n"
        report += "=" * 75 + "\n\n"

        report += f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total Cities Analyzed: {len(discrepancies)}\n\n"

        # Add severity level explanation section
        report += "SEVERITY LEVELS:\n"
        report += "-" * 50 + "\n"
        report += "  CRITICAL: Discrepancy > 5.0°C\n"
        report += "  HIGH:     Discrepancy > 3.0°C to 5.0°C\n"
        report += "  MEDIUM:   Discrepancy > 1.0°C to 3.0°C\n"
        report += "  LOW:      Discrepancy ≤ 1.0°C\n\n"

        # Counts for each severity level
        critical_temp = [d for d in discrepancies
                         if WeatherDiscrepancyAnalyzer._determine_severity(d[3]) == "CRITICAL"]

        high_temp = [d for d in discrepancies
                     if WeatherDiscrepancyAnalyzer._determine_severity(d[3]) == "HIGH"]

        medium_temp = [d for d in discrepancies
                       if WeatherDiscrepancyAnalyzer._determine_severity(d[3]) == "MEDIUM"]

        low_temp = [d for d in discrepancies
                    if WeatherDiscrepancyAnalyzer._determine_severity(d[3]) == "LOW"]

        report += "TEMPERATURE SEVERITY DISTRIBUTION:\n"
        report += f"  CRITICAL: {len(critical_temp)} cities\n"
        report += f"  HIGH:     {len(high_temp)} cities\n"
        report += f"  MEDIUM:   {len(medium_temp)} cities\n"
        report += f"  LOW:      {len(low_temp)} cities\n\n"

        # Count test outcomes
        failed_tests = [d for d in discrepancies if d[3] > d[7]]  # discrepancy > threshold
        passed_tests = [d for d in discrepancies if d[3] <= d[7]]  # discrepancy <= threshold

        report += "TEST OUTCOMES:\n"
        report += f"  PASSED: {len(passed_tests)} cities\n"
        report += f"  FAILED: {len(failed_tests)} cities\n\n"

        if failed_tests:
            report += "FAILED CITIES:\n"
            for d in failed_tests:
                severity = WeatherDiscrepancyAnalyzer._determine_severity(d[3])
                report += f"  - {d[0]}: {d[3]:.1f}°C ({severity}) vs threshold {d[7]:.1f}°C\n"
            report += "\n"

        return report

    @staticmethod
    def _determine_severity(discrepancy: float) -> str:
        if discrepancy > 5.0:
            return "CRITICAL"
        elif discrepancy > 3.0:
            return "HIGH"
        elif discrepancy > 1.0:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def _calculate_percentage(value: float, reference: float) -> float:
        return (value / abs(reference) * 100) if reference != 0 else 0

    @staticmethod
    def _generate_city_details(discrepancies: List[Tuple]) -> str:
        report = "DETAILED CITY RESULTS:\n"
        report += "-" * 75 + "\n\n"

        for city, db_temp, ui_temp, temp_discrepancy, db_feels_like, ui_feels_like, feels_like_discrepancy, threshold in discrepancies:
            # Get severity ratings with visual emphasis
            temp_severity = WeatherDiscrepancyAnalyzer._determine_severity(temp_discrepancy)
            feels_like_severity = (WeatherDiscrepancyAnalyzer
                                   ._determine_severity(feels_like_discrepancy))

            # Determine test status
            temp_status = "PASSED" if temp_discrepancy <= threshold else "FAILED"
            feels_like_status = "PASSED" if feels_like_discrepancy <= threshold else "FAILED"

            # Calculate percentage differences
            temp_percentage = WeatherDiscrepancyAnalyzer._calculate_percentage(temp_discrepancy, db_temp)
            feels_like_percentage = WeatherDiscrepancyAnalyzer._calculate_percentage(feels_like_discrepancy,
                                                                                     db_feels_like)

            # Calculate absolute differences
            temp_diff = db_temp - ui_temp
            feels_like_diff = db_feels_like - ui_feels_like

            # Format city details with more detailed severity information
            report += f"City: {city}\n"
            report += "  Temperature Analysis:\n"
            report += f"    Database Temperature: {db_temp:.2f}°C\n"
            report += f"    UI Temperature: {ui_temp:.2f}°C\n"
            report += f"    Absolute Difference: {temp_diff:.2f}°C\n"
            report += f"    Discrepancy: {temp_discrepancy:.2f}°C\n"
            report += f"    SEVERITY: {temp_severity}\n"
            report += f"    Threshold: {threshold:.2f}°C\n"
            report += f"    Test Status: {temp_status}\n"
            report += f"    Percentage Difference: {temp_percentage:.2f}%\n\n"

            report += "  Feels Like Analysis:\n"
            report += f"    Database Feels Like: {db_feels_like:.2f}°C\n"
            report += f"    UI Feels Like: {ui_feels_like:.2f}°C\n"
            report += f"    Absolute Difference: {feels_like_diff:.2f}°C\n"
            report += f"    Discrepancy: {feels_like_discrepancy:.2f}°C\n"
            report += f"    SEVERITY: {feels_like_severity}\n"
            report += f"    Threshold: {threshold:.2f}°C\n"
            report += f"    Test Status: {feels_like_status}\n"
            report += f"    Percentage Difference: {feels_like_percentage:.2f}%\n\n"

            report += "-" * 50 + "\n\n"

        return report

    @staticmethod
    def _generate_summary_statistics(discrepancies: List[Tuple]) -> str:
        # Extract temperature discrepancies
        temp_discrepancies = [d[3] for d in discrepancies]
        feels_like_discrepancies = [d[6] for d in discrepancies]

        # Calculate statistics
        avg_temp_discrepancy = sum(temp_discrepancies) / len(temp_discrepancies)
        max_temp_discrepancy = max(temp_discrepancies)
        min_temp_discrepancy = min(temp_discrepancies)

        avg_feels_like_discrepancy = sum(feels_like_discrepancies) / len(feels_like_discrepancies)
        max_feels_like_discrepancy = max(feels_like_discrepancies)
        min_feels_like_discrepancy = min(feels_like_discrepancies)

        # Count severity levels
        critical_count = sum(1 for d in temp_discrepancies if d > 5.0)
        high_count = sum(1 for d in temp_discrepancies if 3.0 < d <= 5.0)
        medium_count = sum(1 for d in temp_discrepancies if 1.0 < d <= 3.0)
        low_count = sum(1 for d in temp_discrepancies if d <= 1.0)

        # Format statistics section
        report = "SUMMARY STATISTICS:\n"
        report += "-" * 75 + "\n\n"

        report += "Temperature Discrepancies:\n"
        report += f"  Average: {avg_temp_discrepancy:.2f}°C\n"
        report += f"  Maximum: {max_temp_discrepancy:.2f}°C\n"
        report += f"  Minimum: {min_temp_discrepancy:.2f}°C\n"
        report += f"  Severity Distribution: {critical_count} CRITICAL, {high_count} HIGH, {medium_count} MEDIUM, {low_count} LOW\n\n"

        report += "Feels Like Discrepancies:\n"
        report += f"  Average: {avg_feels_like_discrepancy:.2f}°C\n"
        report += f"  Maximum: {max_feels_like_discrepancy:.2f}°C\n"
        report += f"  Minimum: {min_feels_like_discrepancy:.2f}°C\n\n"

        # Find cities with max discrepancies
        city_max_temp_idx = temp_discrepancies.index(max_temp_discrepancy)
        city_max_feels_like_idx = feels_like_discrepancies.index(max_feels_like_discrepancy)

        report += f"City with Highest Temperature Discrepancy: {discrepancies[city_max_temp_idx][0]} "
        report += f"({max_temp_discrepancy:.2f}°C - {WeatherDiscrepancyAnalyzer._determine_severity(max_temp_discrepancy)})\n"

        report += (f"City with Highest Feels Like Discrepancy:"
                   f" {discrepancies[city_max_feels_like_idx][0]} ")

        report += (f"({max_feels_like_discrepancy:.2f}°C -"
                   f" {WeatherDiscrepancyAnalyzer._determine_severity
                   (max_feels_like_discrepancy)})\n\n")

        return report

    @staticmethod
    def reset_discrepancies():
        """Reset the discrepancies list to start fresh"""
        WeatherDiscrepancyAnalyzer._discrepancies = []