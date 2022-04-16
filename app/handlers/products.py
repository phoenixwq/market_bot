from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from app.parser import GoogleShopParser
from app.parser import Paginator
from app.db.base import session
from app.db.tables import User, Product
from aiogram import Dispatcher
from bot import bot
import urllib.request
from .utils import *
import json

PAGE_SIZE = 3


class SearchProduct(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_load_data = State()


async def search_start(message: types.Message):
    await message.answer("Enter the name of the product you want to find!", reply_markup=types.ReplyKeyboardRemove())
    await SearchProduct.waiting_for_product_name.set()


async def load_data(message: types.Message, state: FSMContext):
    parser = GoogleShopParser()
    data = parser.get_products(message.text.lower())
    paginator = Paginator(data, PAGE_SIZE)
    paginate_keyboard = get_paginate_keyboard(paginator.get_allowed_method())
    await message.answer(f"{message.from_user.first_name.capitalize()}, here's what I found!",
                         reply_markup=paginate_keyboard)
    await state.update_data(paginator=paginator)

    for product in paginator.current():
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Add to favorites", callback_data="add_product_to_favorites"))
        text: str = get_product_text_message(product)
        image = urllib.request.urlopen(product['image']).read()
        await bot.send_photo(chat_id=message.from_user.id, photo=image, caption=text,
                             disable_notification=True, parse_mode="HTML", reply_markup=keyboard,
                             caption_entities=product)

    await SearchProduct.next()


async def page_view(message: types.Message, state: FSMContext):
    user_message = message.text.lower()
    if user_message not in ('next', 'prev', 'exit'):
        await message.answer("Please use the keyboard bellow")
        return
    data = await state.get_data()
    paginator: Paginator = data.get("paginator")
    try:
        if user_message == "next":
            products = paginator.next()
        elif user_message == "prev":
            products = paginator.prev()
        else:
            await message.answer("searched completed!", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            return
    except IndexError:
        await message.answer("page not found!")
        return
    paginate_keyboard = get_paginate_keyboard(paginator.get_allowed_method())
    await state.update_data(paginator=paginator)
    for product in products:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Add to favorites", callback_data="add_product_to_favorites"))
        text = get_product_text_message(product)
        image = urllib.request.urlopen(product['image']).read()
        await bot.send_photo(chat_id=message.from_user.id, photo=image, caption=text,
                             disable_notification=True, parse_mode="HTML", reply_markup=keyboard)

    await message.answer(f"page: {paginator.current_page + 1}", reply_markup=paginate_keyboard)


async def add_product_in_user_favorite(call: types.CallbackQuery):
    data = json.loads(call.message.as_json())
    name, price, shop = data.get("caption").split('\n')
    name = name[3:]
    price = price[9:]
    shop = shop[8:]
    url = data.get('caption_entities')[0].get("url")
    with session() as s:
        user = s.query(User).filter_by(chat_id=call.from_user.id).first()
        product = Product(name=name, price=price, shop=shop, url=url, user=user.id)
        s.add(product)
    await call.answer(text="Product added to favorites!", show_alert=True)


def register_products_handlers(dp: Dispatcher):
    dp.register_message_handler(search_start, commands="search", state="*")
    dp.register_message_handler(load_data, state=SearchProduct.waiting_for_product_name)
    dp.register_message_handler(page_view, state=SearchProduct.waiting_for_load_data)
    dp.register_callback_query_handler(add_product_in_user_favorite,
                                       lambda query: query.data == "add_product_to_favorites", state='*')
