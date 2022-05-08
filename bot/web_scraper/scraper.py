from bs4 import BeautifulSoup
from .driver import WebDriver
from geopy.geocoders import Nominatim
from geopy import distance
from geopy.exc import GeocoderTimedOut
from typing import List
from abc import ABC, abstractmethod


class BasePage(ABC):
    base_url: str

    def __init__(self, **kwargs):
        self._driver = WebDriver()
        self.query_param = kwargs

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass


class BaseContent(ABC):
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class BaseScraper(ABC):
    def __init__(self):
        self._driver = WebDriver()

    @abstractmethod
    def parse(self, page: BasePage) -> List[BaseContent]:
        pass


class GisMarketPage(BasePage):
    base_url = "https://2gis.ru/search/{product_name}/tab" \
               "/market/page/{page}?m={longitude}%2C{latitude}%2F17.65"

    def __init__(self, **kwargs):
        if 'page' in kwargs:
            kwargs.pop('page')
        super(GisMarketPage, self).__init__(**kwargs)
        try:
            self.location = self.query_param["latitude"], self.query_param["longitude"]
        except KeyError:
            raise ValueError("Invalid URL")

    def __iter__(self):
        self._number = 1
        return self

    def __next__(self):
        if self._number == 1:
            html = self.get_page()
            soup = BeautifulSoup(html, "html.parser")
            self.count_page = len(soup.find_all("span", {"class": "_19xy60y"}))
            self._number += 1
            return html
        elif self._number <= self.count_page:
            self._number += 1
            html = self.get_page()
            return html

        raise StopIteration

    def get_page(self):
        page_url = self.base_url.format(**self.query_param, page=self._number)
        return self._driver.get_page_content(page_url)

    def get_location(self):
        return self.location


class GisMarketContent(BaseContent):
    def __init__(self, name, image, locations):
        self.name = name
        self.image = image
        self.locations = locations

    def __repr__(self):
        return f"{self.name} {self.image}"

    def __str__(self):
        name = self.name
        locations = self.locations
        list_ = []
        for data in locations:
            s = "\nshop: {0} \naddress: {1} \nprice: {2} \ndistance: {3} km\n".format(*data)
            list_.append(s)
        description = "----------------->".join(list_)
        return f"{name}\n{description}"


class GisMarketScraper(BaseScraper):
    base_url = "https://2gis.ru"

    def __init__(self):
        super(GisMarketScraper, self).__init__()
        self.geolocator = Nominatim(user_agent="test_app")

    def parse(self, page: GisMarketPage) -> List[GisMarketContent]:
        contents = []
        user_coordinates = page.get_location()
        for html in page:
            products_page = BeautifulSoup(html, "html.parser")
            for product in products_page.find_all("div", {"class": "_1k2x33mp"}):
                content = self.get_product_content(product, user_coordinates)
                if content is not None:
                    contents.append(content)
        contents.sort(key=lambda d: d.locations[0][-1])
        return contents

    def get_product_content(self, product, user_coordinates) -> GisMarketContent:
        product_url = product.find("a", class_="_1rehek").get('href')
        name = product.find("span", class_="_hc69qa").text
        html = self._driver.get_page_content(self.base_url + product_url)
        product_detail = BeautifulSoup(html, "html.parser")
        try:
            image_url = product_detail.find("div", class_="_1l59x1q").find('img')['src']
        except AttributeError:
            image_url = None
        product_locations: list = []
        for local_info in product_detail.find_all("div", {"class": "_1xqczd6"}):
            shop = local_info.find("div", class_="_b8wvvmq").text
            address = local_info.find("div", class_="_9vba8w").text
            price = local_info.find("span", class_="_f9pg1j5").text
            try:
                location = self.geolocator.geocode(address)
                address_coords = (location.latitude, location.longitude)
            except (GeocoderTimedOut, AttributeError):
                continue
            distance_ = round(distance.distance(user_coordinates, address_coords).km, 3)
            product_locations.append([shop, address, price, distance_])
        product_locations.sort(key=lambda x: x[-1])
        if len(product_locations) < 1:
            return None
        data = {"name": name, "image": image_url, "locations": product_locations[:3]}
        return GisMarketContent(**data)
