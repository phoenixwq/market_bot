import csv
import os
from driver import WebDriver
from bs4 import BeautifulSoup
from config import BASE_DIR
from datetime import datetime


class ScraperData:
    def __init__(self, file: str, size: int):
        self.file = file
        self.size = size


class GoogleShoppingScraper:
    url = "https://www.google.ru/search?tbm=shop&hl=ru&q=%s"

    def __init__(self, location=None):
        self._web_driver = WebDriver()
        self.location = location

    def parse(self, product_name: str) -> ScraperData:
        if self.location is not None:
            self._web_driver.set_location(**self.location)
        html = self._web_driver.get_page_content(self.url % product_name)
        soup = BeautifulSoup(html, 'html.parser')
        soup.find_all("div", {"class": "i0X6df"})

        filename = str(datetime.now().timestamp()) + ".csv"
        path_file = os.path.join(BASE_DIR, f"data/{filename}")
        size = 0
        with open(path_file, "w", encoding='UTF8', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            header = ["name", "price", "shop", "url", "image"]
            writer.writerow(header)

            for product in soup.find_all("div", {"class": "i0X6df"}):
                size += 1
                name = product.find('h4', class_='Xjkr3b').text
                price = product.find('span', class_='a8Pemb OFFNJ').text
                shop = product.find('div', class_='aULzUe IuHnof').text
                url = product.find('div', class_='zLPF4b').find('div').find('a').get('href')[9:]
                image = product.find('div', class_="ArOc1c").find('img')['src']
                writer.writerow([name, price, shop, url, image])

            return ScraperData(file=path_file, size=size)
