import math
import pandas as pd


class Paginator:
    def __init__(self, csv_file: str, page_size: int):
        with open(csv_file) as file:
            self.count_rows = -1
            for _ in file:
                self.count_rows += 1
        self.csv_file = csv_file
        self.page_size = page_size
        self.current_page = 0
        self.count_page = math.ceil(self.count_rows / self.page_size)

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
        return pd.read_csv(self.csv_file, skiprows=start, nrows=start + self.page_size)

    def has_next(self):
        return self.current_page + 1 < self.count_page

    def has_previous(self):
        return self.current_page > 1