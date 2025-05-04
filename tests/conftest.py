import pytest
import datetime
import os

from automation_framework.WeatherDiscrepancyAnalyzer import WeatherDiscrepancyAnalyzer
from automation_framework.config.manager import ConfigManager
from automation_framework.utilities.db_helpers import DatabaseHelper
from automation_framework.utilities.hf_logger import HuggingFaceLogger  # Import the logger
from automation_framework.utilities.test_reporting import TestErrorReporter, HuggingFaceTestLogger
from objects.objects_api.weather_page_api import WeatherPageApi
from objects.objects_ui.weather_page_ui import WeatherPageUi
from tests.fixtures.weather_fixtures import WeatherTestFixtures
from tests.test_suit_Base import TestSuitBase


# ✅ Register custom CLI option
def pytest_addoption(parser):
    parser.addoption(
        "--hf-logging",
        action="store_true",
        default=False,
        help="Enable Hugging Face logging"
    )


# Configure the HTML report
def pytest_configure(config):
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/screenshots", exist_ok=True)

    config._metadata = {
        "Project": "Pango Weather Automation",
        "Environment": "QA",
        "Python Version": f"{pytest.__version__}",
        "Execution Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def pytest_html_report_title(report):
    report.title = "Pango Weather API Test Report"


def extract_metrics_from_report(report):
    metrics = {"temperature_diff": 0, "humidity_diff": 0, "is_significant": False}

    if isinstance(report, dict):
        metrics["temperature_diff"] = report.get("temperature_diff", 0)
        metrics["humidity_diff"] = report.get("humidity_diff", 0)
        metrics["is_significant"] = report.get("is_significant", False)
    elif isinstance(report, str):
        if "Temperature difference:" in report:
            temp_line = [line for line in report.split("\n") if "Temperature difference:" in line]
            if temp_line:
                try:
                    metrics["temperature_diff"] = float(temp_line[0].split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
        if "Significant discrepancy detected" in report:
            metrics["is_significant"] = True

    return metrics


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    item.weather_test_data = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    report.description = str(item.function.__doc__)

    if report.when == "call":
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if report.failed:
            TestErrorReporter.process_failure_information(item, report, call, timestamp)

        if 'hf_logger' in item.funcargs and item.config.getoption("--hf-logging"):
            hf_logger = item.funcargs['hf_logger']
            if hf_logger:
                log_success = HuggingFaceTestLogger.log_basic_test_metrics(hf_logger, item, report, call)

                if log_success and hasattr(item, "weather_test_data"):
                    report.weather_test_data = item.weather_test_data
                    HuggingFaceTestLogger.log_weather_test_data(
                        hf_logger, item, report, extract_metrics_from_report
                    )
                    HuggingFaceTestLogger.log_test_errors(hf_logger, report)


@pytest.fixture
def analyze_discrepancies():
    async def _analyze(analyzer, db_response, ui_response, request, generate_text_report=False):
        return await WeatherTestFixtures.analyze_discrepancies(
            analyzer, db_response, ui_response, request, generate_text_report
        )
    return _analyze


@pytest.fixture(scope="session")
def config_manager():
    return ConfigManager()


@pytest.fixture(scope="session")
def hf_logger(config_manager):
    if not config_manager.use_hugging_face():
        yield None
        return

    project_name = config_manager.get_hugging_face_project()

    try:
        os.environ["HUGGING_FACE_TOKEN"] = config_manager.get_hugging_face_api_key()
        logger = HuggingFaceLogger(project_name=project_name)

        if hasattr(config_manager, 'wandb_api_key'):
            logger.setup_wandb(config_manager.wandb_api_key)

        logger.log_metrics({"event": "test_session_start", "timestamp": datetime.datetime.now().isoformat()})
        yield logger
        logger.log_metrics({"event": "test_session_end", "timestamp": datetime.datetime.now().isoformat()})
    except Exception as e:
        print(f"Failed to initialize Hugging Face logger: {e}")
        yield None


@pytest.fixture(scope="class")
def db_helper(config_manager):
    db_helper = DatabaseHelper(config_manager)
    yield db_helper
    db_helper.close_connection()


@pytest.fixture(scope="class")
def api_client():
    return WeatherPageApi()


@pytest.fixture(scope="class")
def driver():
    driver = TestSuitBase.get_driver()
    yield driver
    TestSuitBase.driver_dispose(driver)


@pytest.fixture(scope="class")
def ui_client(driver):
    return WeatherPageUi(driver)


@pytest.fixture(scope="class")
def weather_discrepancy_analyzer():
    return WeatherDiscrepancyAnalyzer()


def init_weather_test_data(request, city_name, city_id):
    WeatherTestFixtures.init_weather_test_data(request, city_name, city_id)


def store_weather_responses(request, ui_response, db_response):
    WeatherTestFixtures.store_weather_responses(request, ui_response, db_response)

def pytest_sessionfinish(session, exitstatus):
    WeatherDiscrepancyAnalyzer.export_discrepancies_as_json()
