from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.router import Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram import types, F
from bot.web_scraper import Scraper
from bot.db.base import session
from bot.db.utils import get_or_create
from bot.db.models import User, Product
from bot.paginator import Paginator
from bot.filters import PaginateFilter
from .common import menu
from .utils import get_paginate_keyboard, send_page_to_user
import re

PAGE_SIZE = 3

router = Router()


class SearchProduct(StatesGroup):
    product_name = State()
    load_data = State()


@router.message(F.text.casefold() == "🔎")
async def search_start(message: types.Message, state: FSMContext):
    await state.set_state(SearchProduct.product_name)
    await message.answer(
        "Enter the name of the product you want to find!",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(SearchProduct.product_name, ContentTypesFilter(content_types=["text"]))
async def load_data(message: types.Message, state: FSMContext):
    location = None
    with session() as s:
        user = get_or_create(s, User, chat_id=message.from_user.id)
        if user.longitude is not None and user.latitude is not None:
            location = {
                "longitude": user.longitude,
                "latitude": user.latitude
            }
    data = Scraper(location).parse(message.text.lower())
    paginator = Paginator(data, PAGE_SIZE)
    await message.answer(
        f"{message.from_user.first_name.capitalize()}, here's what I found!",
        reply_markup=get_paginate_keyboard(paginator)
    )
    await state.update_data(paginator=paginator)
    await send_page_to_user(message.from_user.id, paginator.current(), text='Add to favorites',
                            callback_data='add_product_to_favorites')
    await state.set_state(SearchProduct.load_data)


@router.message(SearchProduct.load_data, ContentTypesFilter(content_types=["text"]), PaginateFilter())
async def page_view(message: types.Message, state: FSMContext):
    user_message = message.text.lower()
    if user_message == "exit":
        await state.clear()
        return await menu(message, state)

    data = await state.get_data()
    paginator: Paginator = data.get("paginator")
    try:
        if user_message == "next":
            products = paginator.next()
        else:
            products = paginator.previous()
    except IndexError:
        return await message.answer("page not found!")

    await state.update_data(paginator=paginator)
    await send_page_to_user(message.from_user.id, products, text='Add to favorites',
                            callback_data='add_product_to_favorites')
    await message.answer(f"page: {paginator.current_page + 1}", reply_markup=get_paginate_keyboard(paginator))


@router.callback_query(lambda query: query.data == "add_product_to_favorites", )
async def add_product_in_user_favorite(call: types.CallbackQuery):
    name, price, shop = re.match(r"name: ([\w\W]*)\nprice: ([\w\W]*)\nshop: ([\w\W]*)", call.message.caption).groups()
    image = call.message.photo[0].file_id
    url = call.message.caption_entities[0].url
    with session() as s:
        user = get_or_create(s, User, chat_id=call.from_user.id)
        product = get_or_create(s, Product, name=name, price=price, shop=shop, url=url, image=image)
        user.products.append(product)
        s.add(product)
    await call.answer(text="Product added to favorites!", show_alert=True)
