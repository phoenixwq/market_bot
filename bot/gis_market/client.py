import logging, re
from bs4 import BeautifulSoup
from geocoder import search_by_query
from geopy import distance
from selenium import webdriver
import chromedriver_binary

logger = logging.getLogger(__name__)

gis_market_url = "https://2gis.ru"


class GisMarketProduct:
    def __init__(self, product_id, product_name, image_url, price, shop, address, distance):
        self.data = {
            "id": product_id,
            "name": product_name,
            "image": image_url,
            "price": price,
            "shop": shop,
            "address": address,
            "distance": distance
        }

    @property
    def id(self):
        return self.data.get('id')

    @property
    def name(self):
        return self.data.get("name")

    @property
    def image(self):
        return self.data.get("image")

    @property
    def price(self):
        return self.data.get("price")

    @property
    def shop(self):
        return self.data.get("shop")

    @property
    def address(self):
        return self.data.get("address")

    @property
    def distance(self):
        return self.data.get("distance")

    def __str__(self):
        return f"name: {self.name}\nshop: {self.shop}\naddress: {self.address}\nprice: {self.price}р."


class GisMarketClient:
    def __init__(self, location):
        self.location = location

    def _get_driver(self):
        return webdriver.Chrome()

    def search(self, term: str, duration: bool = False):
        search_url = "/search/{0}/tab/market/?m={2}%2C{1}%2F17.65".format(
            term, *self.location
        )
        driver = self._get_driver()
        driver.get(gis_market_url + search_url)
        html = driver.page_source

        products_soup = BeautifulSoup(html, "html.parser")
        for product_soup in products_soup.find_all("div", {"class": "_1k2x33mp"}):
            products = []
            for product_data in self.__parse_product(product_soup):
                products.append(
                    GisMarketProduct(*product_data)
                )
            if len(products) > 0 and duration:
                products.sort(key=lambda product: product.distance)
                yield products[0]
            else:
                for product in products:
                    yield product

    def __parse_product(self, product):
        driver = self._get_driver()
        product_url = product.find("a", class_="_1rehek").get('href')
        product_id = re.search(r"\d+", product_url).group(0)
        product_name = product.find("span", class_="_hc69qa").text
        driver.get(gis_market_url + product_url)
        product_detail_html = driver.page_source
        product_detail_soup = BeautifulSoup(product_detail_html, "html.parser")
        try:
            image_url = product_detail_soup.find("div", class_="_1l59x1q").find('img')['src']
        except AttributeError:
            image_url = None
        for local_info in product_detail_soup.find_all("div", {"class": "_1xqczd6"}):
            shop = local_info.find("div", class_="_b8wvvmq").text
            address = local_info.find("div", class_="_9vba8w").text
            price = local_info.find("span", class_="_f9pg1j5").text
            location = search_by_query(address)
            if location:
                distance_ = distance.distance(
                    (location["lat"], location["lon"]),
                    self.location
                )
                yield product_id, product_name, image_url, price, shop, address, distance_
