from aiogram.dispatcher.filters.callback_data import CallbackData


class ProductCallback(CallbackData, prefix="product"):
    index: int
    name: str
    page: int


