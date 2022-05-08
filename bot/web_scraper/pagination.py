from typing import List
import math
from .scraper import BaseContent


class Paginator:
    def __init__(self, data: List[BaseContent], page_size: int):
        self.data = data
        self.page_size = page_size
        self.current_page = 0
        self.size = len(self.data)
        self.count_page = math.ceil(self.size / self.page_size)

    def next(self) -> List[dict]:
        if self.current_page + 1 > self.count_page:
            raise IndexError("page not found")

        self.current_page += 1
        page = self.__get_page()
        return page

    def previous(self) -> List[dict]:
        if self.current_page - 1 < 0:
            raise IndexError("page not found")
        self.current_page -= 1
        page = self.__get_page()
        return page

    def current(self) -> List[dict]:
        page = self.__get_page()
        return page

    def __get_page(self) -> List[dict]:
        start = self.current_page * self.page_size
        return self.data[start: start + self.page_size]

    def has_next(self) -> bool:
        return self.current_page + 1 < self.count_page

    def has_previous(self) -> bool:
        return self.current_page >= 1
