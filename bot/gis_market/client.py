import re
from typing import Iterator, Union, Tuple
import requests
from bs4 import BeautifulSoup
from geopy import distance
from bot.geocoder import search_by_query


class GisMarketProduct:
    def __init__(
            self,
            product_id: int,
            product_name: str,
            image_url: str,
            price: int,
            shop: str,
            address: str,
            distance: float
    ):
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
    def id(self) -> int:
        return self.data.get('id')

    @property
    def name(self) -> str:
        return self.data.get("name")

    @property
    def image(self) -> str:
        return self.data.get("image")

    @property
    def price(self) -> int:
        return self.data.get("price")

    @property
    def shop(self) -> str:
        return self.data.get("shop")

    @property
    def address(self) -> str:
        return self.data.get("address")

    @property
    def distance(self) -> float:
        return self.data.get("distance")

    def __str__(self) -> str:
        return f"name: {self.name}\nshop: {self.shop}\naddress: {self.address}\nprice: {self.price}р."


class GisMarketClient:
    def __init__(self, location: Tuple[int, int]):
        self.location = location
        self.base_url = "https://2gis.ru"
        self._headers = {
            "referer": "https://www.google.com/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
        }

    def search(self, term: str, duration: bool = False) -> Iterator[GisMarketProduct]:
        search_url = "/search/{0}/tab/market/?m={2}%2C{1}%2F17.65".format(
            term, *self.location
        )
        resp = requests.get(
            self.base_url + search_url,
            headers=self._headers
        )
        html = resp.content
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

    def __parse_product(self, product) -> Iterator[Tuple[Union[int, float, str]]]:
        product_url = product.find("a", class_="_1rehek").get('href')
        product_id = re.search(r"\d+", product_url).group(0)
        product_name = product.find("span", class_="_hc69qa").text
        resp = requests.get(
            self.base_url + product_url,
            headers=self._headers
        )
        product_detail_html = resp.content
        product_detail_soup = BeautifulSoup(product_detail_html, "html.parser")
        try:
            image_url = product_detail_soup.find("div", class_="_2b7zvfy").find('img')['src']
        except (AttributeError, TypeError):
            image_url = None
        for local_info in product_detail_soup.find_all("div", {"class": "_1xqczd6"}):
            shop_div = local_info.find("div", class_="_b8wvvmq")
            address_div = local_info.find("div", class_="_9vba8w")
            price_div = local_info.find("span", class_="_f9pg1j5")
            shop = shop_div.text if shop_div else None
            price = price_div.text if price_div else None
            address = address_div.text if address_div else None
            location = search_by_query(address)
            if location:
                distance_ = distance.distance(location, self.location)
                yield product_id, product_name, image_url, price, shop, address, distance_
