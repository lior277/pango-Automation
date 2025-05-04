import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import logging

class TestSuitBase:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    @staticmethod
    def get_driver() -> webdriver.Chrome:
        try:
            chrome_options = TestSuitBase.get_web_driver_options()

            # Install ChromeDriver
            driver_path = ChromeDriverManager().install()

            # Use OS-safe driver path
            if platform.system() == "Windows":
                chromedriver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
            else:
                chromedriver_path = driver_path  # Linux uses just the binary

            service = ChromeService(chromedriver_path)

            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )

            driver.set_window_size(1920, 1080)
            return driver

        except Exception as e:
            TestSuitBase.logger.error(f"Failed to create WebDriver: {e}")
            raise

    @staticmethod
    def driver_dispose(driver: webdriver.Chrome = None):
        if driver is not None:
            try:
                driver.quit()
                TestSuitBase.logger.info("WebDriver disposed successfully.")
            except Exception as e:
                TestSuitBase.logger.error(f"Error disposing driver: {e}")

    @staticmethod
    def get_web_driver_options() -> ChromeOptions:
        options = ChromeOptions()

        options.add_argument('--headless')  # Required in CI
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--ignore-certificate-errors')

        TestSuitBase.logger.info(f"Chrome Options: {options.arguments}")
        return options
