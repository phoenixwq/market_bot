from aiogram.utils.emoji import emojize
from aiogram import types
from typing import List
import aiogram.utils.markdown as fmt


def get_product_text_message(product: dict) -> str:
    name = product.get("name")
    price = product.get("price")
    shop = product.get("shop")
    url = product.get("url")
    return emojize(fmt.hlink(fmt.text(
        fmt.text(":arrow_right:", name),
        fmt.text(":exclamation:", "price:", fmt.text(price)),
        fmt.text(":shopping_cart:", "shop:", fmt.text(shop)),
        sep="\n"), url)
    )


def get_paginate_keyboard(methods: List[str]) -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    count_methods = len(methods)
    if count_methods == 2:
        keyboard.row(
            types.KeyboardButton("prev"), types.KeyboardButton("next"),
        ).add(types.KeyboardButton("exit"))
    elif count_methods == 1:
        if methods[0] == "next":
            keyboard.row(
                types.KeyboardButton("exit"), types.KeyboardButton("next"),
            )
        else:
            keyboard.row(
                types.KeyboardButton("prev"), types.KeyboardButton("exit"),
            )
    else:
        keyboard.row(
            types.KeyboardButton("exit"),
        )
    return keyboard
