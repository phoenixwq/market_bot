from aiogram import types
from typing import List
import aiogram.utils.markdown as fmt
from aiogram.utils.keyboard import *

from bot.handlers.paginator import Paginator


def get_product_text_message(product) -> fmt:
    name = product.get("name")
    price = product.get("price")
    shop = product.get("shop")
    url = product.get("url")
    return fmt.hlink(fmt.text(
        fmt.text(f"name: {name}"),
        fmt.text(f"price: {price}"),
        fmt.text(f"shop: {shop}"),
        sep="\n"), url)


def get_paginate_keyboard(paginator) -> types.ReplyKeyboardMarkup:
    paginate_buttons = []
    if paginator.has_previous():
        paginate_buttons.append(types.KeyboardButton(text="prev"))
    if paginator.has_next():
        paginate_buttons.append(types.KeyboardButton(text="next"))
    keyboard = [
        paginate_buttons,
        [types.KeyboardButton(text="exit")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
