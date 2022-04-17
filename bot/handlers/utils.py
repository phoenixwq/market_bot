# from aiogram.utils.emoji import emojize
from aiogram import types
from typing import List
import aiogram.utils.markdown as fmt


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


def get_paginate_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = [
        [
            types.KeyboardButton(text="prev"),
            types.KeyboardButton(text="next"),
            types.KeyboardButton(text="exit")
        ]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
