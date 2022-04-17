# from typing import List
# import math
#
#
# class Paginator:
#     def __init__(self, data: List[dict], page_size: int):
#         self.data = data
#         self.page_size = page_size
#         self.current_page = 0
#         self.count_page = math.ceil(len(data) / page_size)
#
#     def next(self):
#         if self.current_page + 1 > self.count_page:
#             raise IndexError("page not found")
#
#         self.current_page += 1
#         page = self.__get_page()
#         return page
#
#     def prev(self):
#         if self.current_page - 1 < 0:
#             raise IndexError("page not found")
#         self.current_page -= 1
#         page = self.__get_page()
#         return page
#
#     def current(self):
#         page = self.__get_page()
#         return page
#
#     def __get_page(self) -> List[dict]:
#         start = self.current_page * self.page_size
#         slice_ = slice(start, start + self.page_size, 1)
#         return self.data[slice_]
#
#     def get_allowed_method(self) -> List[str]:
#         methods = []
#         if self.current_page - 1 >= 0:
#             methods.append('prev')
#         if self.current_page + 1 < self.count_page:
#             methods.append('next')
#
#         return methods
