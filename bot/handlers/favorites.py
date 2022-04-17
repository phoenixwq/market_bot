# from aiogram import Dispatcher
# from aiogram import types
# from bot.db.tables import Product, User
# from bot.db.base import session
# from .utils import get_product_text_message, get_paginate_keyboard
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher import FSMContext
# from .paginators import Paginator
# import json
#
# PAGE_SIZE = 5
#
#
# class ViewFavorites(StatesGroup):
#     waiting_for_load_data = State()
#
#
# async def favorites_load_data(message: types.Message, state: FSMContext):
#     with session() as s:
#         user = s.query(User).filter_by(chat_id=message.from_user.id).first()
#         products = s.query(Product).filter_by(user=user.id).all()
#         data = []
#         for product in products:
#             product_data: dict = {column.name: getattr(product, column.name) for column in product.__table__.columns}
#             data.append(product_data)
#
#         paginator = Paginator(data, PAGE_SIZE)
#         paginate_keyboard = get_paginate_keyboard(paginator.get_allowed_method())
#         await message.answer("My favorites:", reply_markup=paginate_keyboard)
#         for product in paginator.current():
#             keyboard = types.InlineKeyboardMarkup()
#             keyboard.add(types.InlineKeyboardButton(text="Remove from favorites",
#                                                     callback_data="remove_product_from_favorites"))
#             text = get_product_text_message(product)
#             await message.answer(text, parse_mode="HTML", disable_notification=True, reply_markup=keyboard)
#
#         await state.update_data(paginator=paginator)
#         await ViewFavorites.waiting_for_load_data.set()
#
#
# async def page_view(message: types.Message, state: FSMContext):
#     user_message = message.text.lower()
#     data = await state.get_data()
#     paginator: Paginator = data.get("paginator")
#     try:
#         if user_message == "next":
#             products = paginator.next()
#         elif user_message == "prev":
#             products = paginator.prev()
#         else:
#             await message.answer("exit", reply_markup=types.ReplyKeyboardRemove())
#             await state.finish()
#             return
#     except IndexError:
#         await message.answer("page not found!")
#         return
#     paginate_keyboard = get_paginate_keyboard(paginator.get_allowed_method())
#     await state.update_data(paginator=paginator)
#     for product in products:
#         keyboard = types.InlineKeyboardMarkup()
#         keyboard.add(types.InlineKeyboardButton(text="Remove from favorites",
#                                                 callback_data="remove_product_from_favorites"))
#         text = get_product_text_message(product)
#         await message.answer(text, parse_mode="HTML", disable_notification=True, reply_markup=keyboard)
#
#     await message.answer(f"page: {paginator.current_page + 1}", reply_markup=paginate_keyboard)
#
#
# async def remove_product_from_favorites(call: types.CallbackQuery):
#     await call.answer(text="Product remove from favorites!", show_alert=True)
#     data = json.loads(call.message.as_json())
#     url = data.get('entities')[0].get("url")
#     with session() as s:
#         user = s.query(User).filter_by(chat_id=call.from_user.id).first()
#         product = s.query(Product).filter_by(url=url, user=user.id).one_or_none()
#         if product is not None:
#             s.delete(product)
#
#
# def register_favorites_handlers(dp: Dispatcher):
#     dp.register_message_handler(favorites_load_data, commands="favorites", state="*")
#     dp.register_message_handler(page_view, state=ViewFavorites.waiting_for_load_data)
#     dp.register_callback_query_handler(remove_product_from_favorites,
#                                        lambda query: query.data == "remove_product_from_favorites", state='*')
