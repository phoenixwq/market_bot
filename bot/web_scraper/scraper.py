import csv
import re
from datetime import datetime
from bs4 import BeautifulSoup
from bot.settings import CSV_DELIMITER, csv_path
from .driver import WebDriver


class Page:
    def __init__(self, **kwargs):
        self._driver = WebDriver()
        self._url_pattern = "https://2gis.ru/search/{product_name}" \
                            "/tab/market/page/{page}?m={longitude}%2C{latitude}%2F17.65"
        self.query_param = kwargs

    def __iter__(self):
        if "page" in self.query_param:
            self.query_param.pop("page")

        self._number = 0
        self._start_page = self.get_page(1)
        soup = BeautifulSoup(self._start_page, "html.parser")
        self.count_page = len(soup.find_all("span", {"class": "_19xy60y"})) or 1
        return self

    def __next__(self):
        if self._number >= self.count_page:
            raise StopIteration
        self._number += 1
        if self._number == 1:
            return self._start_page
        page = self.get_page(self._number)
        return page

    def get_page(self, page_number):
        page_url = self._url_pattern.format(**self.query_param, page=page_number)
        return self._driver.get_page_content(page_url)


class Scraper:
    def __init__(self):
        self._driver = WebDriver()
        self.base_url = "https://2gis.ru"

    def parse(self, page: Page, only_first: bool = False):
        for page_number, html in enumerate(page):
            if only_first and page_number > 0:
                break
            products_soup = BeautifulSoup(html, "html.parser")
            for product in products_soup.find_all("div", {"class": "_1k2x33mp"}):
                product_url = product.find("a", class_="_1rehek").get('href')
                product_id = re.search(r"\d+", product_url).group(0)
                product_name = product.find("span", class_="_hc69qa").text
                product_detail_hrml = self._driver.get_page_content(self.base_url + product_url)
                product_detail_soup = BeautifulSoup(product_detail_hrml, "html.parser")
                try:
                    image_url = product_detail_soup.find("div", class_="_1l59x1q").find('img')['src']
                except AttributeError:
                    image_url = None
                for j, local_info in enumerate(product_detail_soup.find_all("div", {"class": "_1xqczd6"})):
                    if only_first and j > 0:
                        break
                    shop = local_info.find("div", class_="_b8wvvmq").text
                    address = local_info.find("div", class_="_9vba8w").text
                    price = local_info.find("span", class_="_f9pg1j5").text
                    yield [product_id, product_name, image_url, price, shop, address]

    def parse_and_load(self, page: Page):
        filename = str(datetime.now().timestamp()) + ".csv"
        path_file = csv_path + f"{filename}"
        with open(path_file, "w", encoding='UTF8', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=CSV_DELIMITER)
            header = ["id", "name", "image", "price", "shop", "address"]
            writer.writerow(header)
            for row in self.parse(page):
                writer.writerow(row)
            return path_file
