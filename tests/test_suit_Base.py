import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import logging

class TestSuitBase:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Adjust the logging level as per your needs

    @staticmethod
    def get_driver() -> webdriver:
        try:
            chrome_options = TestSuitBase.get_web_driver_options()
            chrome_install = ChromeDriverManager().install()
            folder = os.path.dirname(chrome_install)
            chromedriver_path = os.path.join(folder, "chromedriver.exe")
            service = ChromeService(chromedriver_path)

            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )

            driver.maximize_window()
            return driver
        except Exception as e:
            TestSuitBase.logger.error(f"Failed to create WebDriver: {e}")
            raise

    @staticmethod
    def driver_dispose(driver: webdriver.Chrome = None):
        if driver is not None:
            try:
                driver.close()
                driver.quit()
                TestSuitBase.logger.info("WebDriver disposed successfully.")
            except Exception as e:
                TestSuitBase.logger.error(f"Error disposing driver: {e}")

    @staticmethod
    def get_web_driver_options() -> ChromeOptions:
        options = ChromeOptions()

        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')

        TestSuitBase.logger.info(f"Chrome Options: {options.arguments}")

        return options
