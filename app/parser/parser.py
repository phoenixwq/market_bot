from typing import List
from .driver import WebDriver
from bs4 import BeautifulSoup


class GoogleShopParser:
    google_shop_url = "https://www.google.ru/search?tbm=shop&hl=ru&q=%s"

    def __init__(self, location=None):
        self._web_driver = WebDriver()
        self.location = location

    def get_products(self, product_name: str) -> List[dict]:
        with self._web_driver as driver:
            if self.location is not None:
                driver.set_location(**self.location)
            html = driver.get_page_content(self.google_shop_url % product_name)
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
