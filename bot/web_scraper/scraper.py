from bs4 import BeautifulSoup
from .driver import WebDriver
from geopy.geocoders import Nominatim
from geopy import distance
from geopy.exc import GeocoderTimedOut
from typing import List
from methodtools import lru_cache


class GISScraper:
    base_url = "https://2gis.ru"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GISScraper, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        self._driver = WebDriver()
        self.geolocator = Nominatim(user_agent="test_app")
        self.location = None

    def set_location(self, latitude: float, longitude: float, rotation: str = "2F17.65") -> None:
        self.location = {
            "latitude": latitude,
            "longitude": longitude,
            "rotation": rotation
        }

    @lru_cache(maxsize=16)
    def parse(self, product_name: str) -> List[dict]:
        if self.location is None:
            raise ValueError("Doesn't not exists location")

        driver = self._driver
        products_url = self.base_url + "/search/{product_name}/tab/market?m={longitude}%2C{latitude}%{rotation}".format(
            product_name=product_name,
            **self.location
        )
        html = driver.get_page_content(products_url)

        soup = BeautifulSoup(html, "html.parser")
        products = []
        user_coordinates = (self.location.get("latitude"), self.location.get("longitude"))
        for product in soup.find_all("div", {"class": "_1k2x33mp"}):
            url = product.find("a", class_="_1rehek").get('href')
            name = product.find("span", class_="_hc69qa").text

            html = driver.get_page_content(
                "{base_url}{url}?m={longitude}%2C{latitude}%{rotation}".format(base_url=self.base_url,
                                                                               url=url,
                                                                               **self.location))
            product_detail = BeautifulSoup(html, "html.parser")
            try:
                image_url = product_detail.find("div", class_="_1l59x1q").find('img')['src']
            except AttributeError:
                image_url = None
            product_locations = []
            for elem in product_detail.find_all("div", {"class": "_1xqczd6"}):
                shop = elem.find("div", class_="_b8wvvmq").text
                address = elem.find("div", class_="_9vba8w").text
                price = elem.find("span", class_="_f9pg1j5").text
                try:
                    location = self.geolocator.geocode(address)
                    if location is None:
                        if "," in address:
                            address = " ".join(address.split(",")[::-1])
                            location = self.geolocator.geocode(address)
                    address_coords = (location.latitude, location.longitude)
                except (GeocoderTimedOut, AttributeError):
                    continue
                distance_ = round(distance.distance(user_coordinates, address_coords).km, 3)
                product_locations.append([shop, address, price, distance_])
            product_locations.sort(key=lambda x: x[-1])
            if len(product_locations) < 1:
                continue
            products.append(
                {
                    "name": name,
                    "image": image_url,
                    "locations": product_locations[:3]
                }
            )
        products.sort(key=lambda d: d["locations"][0][-1])
        return products
