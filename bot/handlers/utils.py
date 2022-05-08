from aiogram import types
from aiogram.methods import SendPhoto


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


async def send_page_to_user(chat_id: int, page):
    for content in page:
        photo = content.image
        if photo is None:
            photo = types.URLInputFile("https://fisnikde.com/wp-content/uploads/2019/01/broken-image.png",
                                       filename=content.name)
        elif photo.startswith("http"):
            photo = types.URLInputFile(photo, filename=content.name)

        await SendPhoto(chat_id=chat_id, photo=photo, caption=str(content),
                        disable_notification=True, parse_mode="HTML")
