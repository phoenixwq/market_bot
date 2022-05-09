from typing import List
from aiogram import types
from aiogram.methods import SendPhoto
from bot.db.models import *
from bot.db.base import session
from bot.db.utils import *
import json
from bot import geocoder


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
        photo = content["image"]
        if photo is None or photo == "":
            photo = types.URLInputFile("https://fisnikde.com/wp-content/uploads/2019/01/broken-image.png",
                                       filename=content["name"])
        else:
            photo = types.URLInputFile(photo, filename=content["name"])

        await SendPhoto(chat_id=chat_id, photo=photo, caption=data_to_message(content),
                        disable_notification=True, parse_mode="HTML")


def data_to_message(data: List[dict]) -> str:
    name = data.get("name")
    local_info = data.get("local_info")
    str_list = []
    index = 0
    for data in json.loads(local_info):
        index += 1
        s = "\nshop: {0} \naddress: {1} \nprice: {2} \n".format(*data)
        str_list.append(s)
        if index == 3:
            break
    description = "----------------->".join(str_list)
    return f"{name}\n{description}"


def data_loader(message: types.Message, data):
    with session() as s:
        request = get_or_create(s, UsersRequest, query=message.text.lower())
        request.date = datetime.datetime.utcnow()
        user = s.query(User).filter_by(chat_id=message.from_user.id).first()
        city = user.city
        request.users.append(user)
        s.add_all([request, user])
        for row in data:
            product_id = int(row["id"])
            product_name = row["name"]
            product_image = row["image"]
            product = s.query(Product).filter_by(site_id=product_id).one_or_none()
            if product is None:
                product = Product()
            product.site_id = product_id,
            product.name = product_name,
            product.image = product_image,
            s.add(product)
            for local_data in json.loads(row["local_info"]):
                shop_name = local_data[0]
                address = local_data[1]
                price = local_data[2]
                shop = get_or_create(s, Shop, name=shop_name)
                shop_product = s.query(ShopProduct).filter_by(shop=shop, product=product, address=address).one_or_none()
                if shop_product is None:
                    shop_product = ShopProduct()
                point = geocoder.search_by_query(address)
                if point is not None:
                    point = f"POINT({point['lat']} {point['lon']})"
                shop_product.address = address
                shop_product.address_point = point
                shop_product.price = price
                shop_product.shop = shop
                shop_product.product = product
                shop_product.city = city
                s.add(shop_product)
