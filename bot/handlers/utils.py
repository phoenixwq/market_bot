from aiogram import types
import aiogram.utils.markdown as fmt
from aiogram.utils.keyboard import *
from aiogram.methods import SendPhoto


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


async def send_page_to_user(chat_id: int, page: List[dict], **button_kwargs):
    for product in page:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(**button_kwargs)]
            ]
        )
        text: str = get_product_text_message(product)
        photo = product.get('image')
        if photo.startswith("http"):
            photo = types.URLInputFile(photo, filename=product.get('name'))

        await SendPhoto(chat_id=chat_id, photo=photo, caption=text,
                        disable_notification=True, parse_mode="HTML", reply_markup=keyboard)
