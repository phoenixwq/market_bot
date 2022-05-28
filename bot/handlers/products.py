from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.router import Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram import types
from bot.db.base import session
from geoalchemy2.shape import to_shape
from bot.handlers.utils import (
    get_paginate_keyboard,
    send_data_to_user,
    search,
    get_user
)

PAGE_SIZE = 3

router = Router()


class SearchProduct(StatesGroup):
    waiting_product_name = State()
    waiting_to_find = State()


@router.message(commands=["search"])
async def search_start(message: types.Message, state: FSMContext):
    await state.set_state(SearchProduct.waiting_product_name)
    await message.answer(
        "Enter the name of the product you want to find:",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(SearchProduct.waiting_product_name, ContentTypesFilter(content_types=["text"]))
async def find_product(message: types.Message, state: FSMContext):
    with session() as s:
        user = get_user(s, message.from_user.id)
        point = user.point
        if point is None:
            await message.answer(
                "Product search is not possible without your geolocation, "
                "please use the command /location"
            )
            await state.clear()
            return
        point = to_shape(point)
        try:
            product, data_iterator = await search(message, point)
        except ValueError:
            await message.answer("Unfortunately I couldn't find anything, please try again!")
            return
        await message.answer(
            f"{message.from_user.first_name.capitalize()}, here's what I found!",
            reply_markup=get_paginate_keyboard()
        )
        await state.update_data(data_iterator=data_iterator)
        await send_data_to_user(message.from_user.id, product)
        await state.set_state(SearchProduct.waiting_to_find)


@router.message(SearchProduct.waiting_to_find, ContentTypesFilter(content_types=["text"]))
async def page_view(message: types.Message, state: FSMContext):
    user_message = message.text.lower()
    if user_message not in ("next", "exit"):
        return
    if user_message == "exit":
        await message.answer("exit", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return

    data = await state.get_data()
    data_iterator = data.get("data_iterator")
    try:
        for _ in range(PAGE_SIZE):
            row = next(data_iterator)
            await send_data_to_user(message.from_user.id, row)
    except StopIteration:
        await message.answer("Completed", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
