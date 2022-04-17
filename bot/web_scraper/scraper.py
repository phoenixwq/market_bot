from .driver import WebDriver
from bs4 import BeautifulSoup
from typing import List


class GoogleShoppingScraper:
    url = "https://www.google.ru/search?tbm=shop&hl=ru&q=%s"

    def __init__(self, location=None):
        self._web_driver = WebDriver()
        self.location = location

    def parse(self, product_name: str) -> List[dict]:
        if self.location is not None:
            self._web_driver.set_location(**self.location)
        html = self._web_driver.get_page_content(self.url % product_name)
        soup = BeautifulSoup(html, 'html.parser')
        soup.find_all("div", {"class": "i0X6df"})
        products = []
        for product in soup.find_all("div", {"class": "i0X6df"}):
            name = product.find('h4', class_='Xjkr3b').text
            price = product.find('span', class_='a8Pemb OFFNJ').text
            shop = product.find('div', class_='aULzUe IuHnof').text
            url = product.find('div', class_='zLPF4b').find('div').find('a').get('href')[9:]
            image = product.find('div', class_="ArOc1c").find('img')['src']
            products.append(
                {
                    'name': name,
                    'price': price,
                    'shop': shop,
                    'url': url,
                    'image': image
                }
            )

        return products
