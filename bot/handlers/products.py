from aiogram.methods import SendPhoto
from aiogram.dispatcher.router import Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram import types
from bot.web_scraper import Scraper
from .paginator import Paginator
from .utils import *
from bot.db.base import session
from bot.db.tables import User, Product

PAGE_SIZE = 3

router = Router()


class SearchProduct(StatesGroup):
    product_name = State()
    load_data = State()


@router.message(commands=["search"])
async def search_start(message: types.Message, state: FSMContext):
    await state.set_state(SearchProduct.product_name)
    await message.answer(
        "Enter the name of the product you want to find!",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(SearchProduct.product_name)
async def load_data(message: types.Message, state: FSMContext):
    data = Scraper().parse(message.text.lower())
    paginator = Paginator(data, PAGE_SIZE)
    await message.answer(
        f"{message.from_user.first_name.capitalize()}, here's what I found!",
        reply_markup=get_paginate_keyboard(paginator)
    )
    await state.update_data(paginator=paginator)
    for product in paginator.current():
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Add to favorites", callback_data="add_product_to_favorites")]
            ]
        )
        text: str = get_product_text_message(product)
        photo = types.URLInputFile(product.get('image'), filename=product.get('name'))
        await SendPhoto(chat_id=message.from_user.id, photo=photo, caption=text,
                        disable_notification=True, parse_mode="HTML", reply_markup=keyboard)

    await state.set_state(SearchProduct.load_data)


@router.message(SearchProduct.load_data)
async def page_view(message: types.Message, state: FSMContext):
    user_message = message.text.lower()
    if user_message not in ('next', 'prev', 'exit'):
        await message.answer("Please use the keyboard bellow")
        return
    if user_message == "exit":
        await message.answer("searched completed!", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return

    data = await state.get_data()
    paginator: Paginator = data.get("paginator")
    try:
        if user_message == "next":
            products = paginator.next()
        else:
            products = paginator.previous()
    except IndexError:
        await message.answer("page not found!")
        return

    await state.update_data(paginator=paginator)
    for product in products:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Add to favorites", callback_data="add_product_to_favorites")]
            ]
        )
        text: str = get_product_text_message(product)
        photo = types.URLInputFile(product.get('image'), filename=product.get('name'))
        await SendPhoto(chat_id=message.from_user.id, photo=photo, caption=text,
                        disable_notification=True, parse_mode="HTML", reply_markup=keyboard)

    await message.answer(f"page: {paginator.current_page + 1}", reply_markup=get_paginate_keyboard(paginator))


@router.callback_query(lambda query: query.data == "add_product_to_favorites",)
async def add_product_in_user_favorite(call: types.CallbackQuery):
    import re
    name, price, shop = re.match(r"name: ([\w\W]*)\nprice: ([\w\W]*)\nshop: ([\w\W]*)", call.message.caption).groups()
    image = call.message.photo[0].file_id
    url = call.message.caption_entities[0].url
    with session() as s:
        user = s.query(User).filter_by(chat_id=call.from_user.id).first()
        product = Product(name=name, price=price, shop=shop, url=url, user=user.id, image=image)
        s.add(product)
    await call.answer(text="Product added to favorites!", show_alert=True)