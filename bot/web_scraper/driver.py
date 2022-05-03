from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent


class WebDriver:
    driver_path = os.path.join(BASE_DIR, "chromedriver")

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebDriver, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._driver = self._create_driver()

    def _create_driver(self) -> webdriver:
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            'geolocation': True,
        })
        return webdriver.Chrome(self.driver_path, options=chrome_options)

    def get_page_content(self, url: str) -> str:
        self._driver.get(url)
        content = self._driver.page_source
        return content

    def quit_driver(self):
        self._driver.quit()
