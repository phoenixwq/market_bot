import math
import pandas as pd
from .scraper import ScraperData


class Paginator:
    def __init__(self, data: ScraperData, page_size: int):
        self.csv_file = data.file
        self.size = data.size
        self.page_size = page_size
        self.current_page = 0
        self.count_page = math.ceil(self.size / self.page_size)

    def next(self) -> pd.DataFrame:
        if self.current_page + 1 > self.count_page:
            raise IndexError("page not found")

        self.current_page += 1
        page = self.__get_page()
        return page

    def previous(self) -> pd.DataFrame:
        if self.current_page - 1 < 0:
            raise IndexError("page not found")
        self.current_page -= 1
        page = self.__get_page()
        return page

    def current(self) -> pd.DataFrame:
        page = self.__get_page()
        return page

    def __get_page(self) -> pd.DataFrame:
        start = self.current_page * self.page_size
        return pd.read_csv(self.csv_file, skiprows=start, nrows=self.page_size,delimiter=';')

    def has_next(self):
        return self.current_page + 1 < self.count_page

    def has_previous(self):
        return self.current_page > 1