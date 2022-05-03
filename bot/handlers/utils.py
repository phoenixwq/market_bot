from aiogram import types
from aiogram.utils.keyboard import *
from aiogram.methods import SendPhoto


def get_product_text_message(product) -> str:
    name = product.get("name")
    locations = product.get("locations")
    str_list = []
    for data in locations:
        s = "\nshop: {0} \naddress: {1} \nprice: {2} \ndistance: {3} km\n".format(*data)
        str_list.append(s)
    description = "----------------->".join(str_list)
    return f"{name}\n{description}"


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
        if photo is None:
            photo = types.URLInputFile("https://fisnikde.com/wp-content/uploads/2019/01/broken-image.png", filename=product.get('name'))
        elif photo.startswith("http"):
            photo = types.URLInputFile(photo, filename=product.get('name'))

        await SendPhoto(chat_id=chat_id, photo=photo, caption=text,
                        disable_notification=True, parse_mode="HTML", reply_markup=keyboard)
