from typing import List
from .scraper import ScraperData
from .config import CSV_DELIMITER
import math
import csv


class Paginator:
    def __init__(self, data: ScraperData, page_size: int):
        self.data = data
        self.page_size = page_size
        self.current_page = 0
        self.count_page = math.ceil(self.data.size / self.page_size)

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
        data = []
        with open(self.data.file, newline='') as file:
            reader = csv.DictReader(file, delimiter=CSV_DELIMITER)
            next(reader)
            try:
                for _ in range(start):
                    next(reader)
                for _ in range(self.page_size):
                    data.append(next(reader))
            except StopIteration:
                pass
        return data

    def has_next(self) -> bool:
        return self.current_page + 1 < self.count_page

    def has_previous(self) -> bool:
        return self.current_page > 1
