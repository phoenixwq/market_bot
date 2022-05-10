from aiogram import types
from aiogram.methods import SendPhoto
from bot.db.models import *
from bot.db.base import session
from bot.db.utils import *
from sqlalchemy import func
from geoalchemy2 import func as geo_func
from bot.settings import images_path


def get_paginate_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = [
        [types.KeyboardButton(text="next")],
        [types.KeyboardButton(text="exit")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def send_data_to_user(chat_id: int, data: list):
    photo = data[2]
    if photo is None or photo == "":
        photo = types.FSInputFile(images_path + "image_not_found.png",
                                  filename="image_not_found.png")
    else:
        photo = types.URLInputFile(photo, filename=data[1])

    await SendPhoto(chat_id=chat_id, photo=photo, caption=data_to_message(data),
                    disable_notification=True, parse_mode="HTML")


def data_to_message(data: list) -> str:
    s = f"{data[1]}\n{data[3]}\n{data[4]}\n{data[5]} ₽"
    return s


def search(message: types.Message):
    with session() as s:
        query = message.text.lower()
        user = get_user(s, message.from_user.id)
        q = select(func.count('*')).select_from(Request) \
            .join(RequestCity, Request.id == RequestCity.request_id) \
            .join(City, City.id == RequestCity.city_id) \
            .where(Request.query.ilike(f"%{query}%"), City.id == user.city.id)
        request_count = s.execute(q).scalar()
        if request_count != 0:
            products = select(Product.id, Product.name, Product.image, Shop.name, ShopProduct.address,
                              ShopProduct.price,
                              geo_func.ST_Distance(ShopProduct.address_point, user.point)) \
                .join(ShopProduct, Product.id == ShopProduct.product_id) \
                .join(Shop, Shop.id == ShopProduct.shop_id) \
                .where(ShopProduct.city_id == user.city.id, Product.name.ilike(f"%{query}%"),
                       ShopProduct.address_point is not None) \
                .order_by(geo_func.ST_Distance(ShopProduct.address_point, user.point))
            for row in s.execute(products).all():
                yield row
    yield None


def get_user(session, chat_id):
    user = session.scalars(
        select(User).where(User.chat_id == chat_id)
    ).first()
    return user
