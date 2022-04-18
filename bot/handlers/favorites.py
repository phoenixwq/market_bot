from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from aiogram import F, types
from bot.db.base import session
from bot.db.tables import User, Product
from .utils import send_page_to_user, get_paginate_keyboard
from bot.filters import PaginateFilter
from bot.paginator import Paginator
from .common import menu

PAGE_SIZE = 3
router = Router()


class ViewFavorites(StatesGroup):
    load_data = State()


@router.message(F.text.casefold() == "⭐")
async def favorites_load_data(message: types.Message, state: FSMContext):
    with session() as s:
        user = s.query(User).filter_by(chat_id=message.from_user.id).first()
        products = s.query(Product).filter_by(user=user.id).all()
        data = []
        for product in products:
            product_data: dict = {column.name: getattr(product, column.name) for column in product.__table__.columns}
            data.append(product_data)

        paginator = Paginator(data, PAGE_SIZE)
        await message.answer("My favorites:", reply_markup=get_paginate_keyboard(paginator))
        await state.update_data(paginator=paginator)
        await send_page_to_user(message.from_user.id, paginator.current(), text='Remove from favorites',
                                callback_data='remove_product_from_favorites')
        await state.set_state(ViewFavorites.load_data)


@router.message(ViewFavorites.load_data, PaginateFilter())
async def page_view(message: types.Message, state: FSMContext):
    user_message = message.text.lower()
    if user_message == "exit":
        await state.clear()
        return await menu(message)

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
    await send_page_to_user(message.from_user.id, products, text='Remove from favorites',
                            callback_data='remove_product_from_favorites')
    await message.answer(f"page: {paginator.current_page + 1}", reply_markup=get_paginate_keyboard(paginator))


@router.callback_query(lambda query: query.data == "remove_product_from_favorites")
async def remove_product_from_favorites(call: types.CallbackQuery):
    await call.answer(text="Product remove from favorites!", show_alert=True)
    url = call.message.caption_entities[0].url
    with session() as s:
        user = s.query(User).filter_by(chat_id=call.from_user.id).first()
        product = s.query(Product).filter_by(url=url, user=user.id).one_or_none()
        if product is not None:
            s.delete(product)
