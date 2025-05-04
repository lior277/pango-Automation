import datetime
from pytest_html import extras


class TestErrorReporter:
    """Handles test error reporting and screenshots."""

    @staticmethod
    def process_failure_information(item, report, call, timestamp):
        try:
            extra_content = getattr(report, 'extra', [])

            # Screenshot on failure
            if 'driver' in item.funcargs:
                driver = item.funcargs['driver']
                screenshot_path = f"reports/screenshots/failure_{timestamp}.png"
                driver.save_screenshot(screenshot_path)
                extra_content.append(extras.image(screenshot_path, mime_type='image/png'))

            # Add exception trace
            if call.excinfo:
                extra_content.append(extras.text(str(call.excinfo), name="Exception"))

            report.extra = extra_content
        except Exception as e:
            print(f"[ERROR] Failed to attach extra info to HTML report: {e}")


class HuggingFaceTestLogger:
    """Logs intelligent test metrics and anomalies to Hugging Face."""

    @staticmethod
    def log_basic_test_metrics(hf_logger, item, report, call):
        try:
            metrics = {
                "event": "test_run",
                "test_name": item.nodeid,
                "result": report.outcome,
                "duration": report.duration,
                "timestamp": datetime.datetime.now().isoformat()
            }

            if report.failed and call.excinfo:
                metrics["error_message"] = str(call.excinfo.value)

            hf_logger.log_metrics(metrics)
            return True
        except Exception as e:
            print(f"[ERROR] Logging basic metrics failed: {e}")
            return False

    @staticmethod
    def log_weather_test_data(hf_logger, item, report, extract_metrics_fn):
        try:
            if not hasattr(report, "weather_test_data") or not report.weather_test_data:
                return

            log_data = {**report.weather_test_data}
            city_id = log_data.get("city_id", "unknown")

            # Extract analysis metrics
            analysis = report.weather_test_data.get("analysis_report", {})
            extracted = extract_metrics_fn(analysis)

            log_data.update({
                "event": "weather_test_analysis",
                "timestamp": datetime.datetime.now().isoformat(),
                "temperature_diff": extracted.get("temperature_diff", 0),
                "humidity_diff": extracted.get("humidity_diff", 0),
                "is_significant_diff": extracted.get("is_significant", False),
                "result": report.outcome,
            })

            log_data.pop("analysis_report", None)  # remove full text to reduce noise
            hf_logger.log_metrics(log_data, step=city_id)
        except Exception as e:
            print(f"[ERROR] Logging weather test data failed: {e}")

    @staticmethod
    def log_test_errors(hf_logger, report):
        try:
            if not hasattr(report, "weather_test_data") or not report.weather_test_data:
                return
            if not (report.failed and "error_message" in report.weather_test_data):
                return

            hf_logger.log_metrics({
                "event": "test_error",
                "timestamp": datetime.datetime.now().isoformat(),
                "city_name": report.weather_test_data.get("city_name", "unknown"),
                "city_id": report.weather_test_data.get("city_id", "unknown"),
                "error_message": report.weather_test_data.get("error_message", "Unknown error"),
                "result": "failed"
            }, step=report.weather_test_data.get("city_id", "unknown"))
        except Exception as e:
            print(f"[ERROR] Logging test error failed: {e}")
