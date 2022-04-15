from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


class WebDriver:
    driver_path = os.path.abspath('app/parser/drivers/chromedriver')

    def __init__(self):
        self._driver = self._create_driver()

    def _create_driver(self) -> webdriver:
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            'geolocation': True
        })
        return webdriver.Chrome(self.driver_path, options=chrome_options)

    def set_location(self, latitude: float, longitude: float, accuracy: int = 500) -> None:
        location_params = {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy
        }
        self._driver.execute_cdp_cmd("Emulation.setGeolocationOverride", location_params)

    def get_page_content(self, url: str) -> str:
        self._driver.get(url)
        return self._driver.page_source

    def close_driver(self):
        self._driver.close()

    def __enter__(self):
        if self._driver is None:
            self._driver = self._create_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()
