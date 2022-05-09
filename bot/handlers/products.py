from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.router import Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram import types
from bot.db.base import session
from bot.db.utils import get_or_create
from bot.db.models import User, Product
from bot.web_scraper import Paginator, Scraper, Page
from bot.filters import PaginateFilter
from bot.handlers.utils import get_paginate_keyboard, send_page_to_user, data_loader
from geoalchemy2.shape import to_shape

PAGE_SIZE = 3

router = Router()


class SearchProduct(StatesGroup):
    product_name = State()
    load_data = State()


@router.message(commands=["search"])
async def search_start(message: types.Message, state: FSMContext):
    await state.set_state(SearchProduct.product_name)
    await message.answer(
        "Enter the name of the product you want to find:",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(SearchProduct.product_name, ContentTypesFilter(content_types=["text"]))
async def load_data(message: types.Message, state: FSMContext):
    with session() as s:
        user = get_or_create(s, User, chat_id=message.from_user.id)
        point = user.point
        if point is None:
            await message.answer(
                "Product search is not possible without your geolocation, please use the command /location"
            )
            await state.clear()
            return
        point = to_shape(point)
    page = Page(latitude=point.x, longitude=point.y, product_name=message.text.lower())
    scraper = Scraper()
    await message.answer("Loading...")
    scraper.parse(page)
    data = scraper.get_data()
    data_loader(message, data)
    paginator = Paginator(data, PAGE_SIZE)
    if paginator.size == 0:
        await message.answer("Unfortunately I couldn't find anything, please try again")
        return
    await message.answer(
        f"{message.from_user.first_name.capitalize()}, here's what I found!",
        reply_markup=get_paginate_keyboard(paginator)
    )
    await state.update_data(paginator=paginator)
    await send_page_to_user(message.from_user.id, paginator.current())
    await state.set_state(SearchProduct.load_data)


@router.message(SearchProduct.load_data, ContentTypesFilter(content_types=["text"]), PaginateFilter())
async def page_view(message: types.Message, state: FSMContext):
    user_message = message.text.lower()
    if user_message == "exit":
        await message.answer(text="Exit", reply_markup=types.ReplyKeyboardRemove())
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
        return await message.answer("page not found!")
    await state.update_data(paginator=paginator)
    await send_page_to_user(message.from_user.id, products)
    await message.answer(f"page: {paginator.current_page + 1}", reply_markup=get_paginate_keyboard(paginator))
