from aiogram.methods import SendPhoto
from aiogram.dispatcher.router import Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram import types
from bot.web_scraper import Paginator, GoogleShoppingScraper
from .utils import *


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
    scraper = GoogleShoppingScraper()
    data = scraper.parse(message.text.lower())
    paginator = Paginator(data, PAGE_SIZE)
    await message.answer(
        f"{message.from_user.first_name.capitalize()}, here's what I found!",
        reply_markup=get_paginate_keyboard()
    )
    await state.update_data(paginator=paginator)
    products = paginator.next().reset_index()
    for index, product in products.iterrows():
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Add to favorites", callback_data="add_product_to_favorites")]
            ]
        )
        text: str = get_product_text_message(product)
        image = product.get('image')
        if image is None:
            image = "https://www.google.com/url?sa=i&url=http%3A%2F%2Fxn--90amjd2bbb.xn--p1ai%2F%25D0%25BD%25D0%25BE%25D0%25B2%25D0%25BE%25D1%2581%25D1%2582%25D0%25B8%2F%25D0%25BF%25D1%2580%25D0%25B5%25D1%2581%25D1%2581-%25D1%2580%25D0%25B5%25D0%25BB%25D0%25B8%25D0%25B7%2F%25D0%25BE%25D1%2582%25D1%2581%25D1%2583%25D1%2582%25D1%2581%25D1%2582%25D0%25B2%25D1%2583%25D0%25B5%25D1%2582-%25D1%2582%25D0%25B5%25D0%25BB%25D0%25B5%25D1%2584%25D0%25BE%25D0%25BD%25D0%25BD%25D0%25B0%25D1%258F-%25D1%2581%25D0%25B2%25D1%258F%25D0%25B7%25D1%258C&psig=AOvVaw2EiqR80YRO7-wQtONHlieA&ust=1650302191380000&source=images&cd=vfe&ved=0CAwQjRxqFwoTCPD-ivLMm_cCFQAAAAAdAAAAABAD"
        photo = types.URLInputFile(image, filename=product.get('name'))
        await SendPhoto(chat_id=message.from_user.id, photo=photo, caption=text,
                        disable_notification=True, parse_mode="HTML", reply_markup=keyboard)

    await state.set_state(SearchProduct.load_data)


@router.message(SearchProduct.load_data)
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
            products = paginator.previous()
        else:
            await message.answer("searched completed!", reply_markup=types.ReplyKeyboardRemove())
            await state.clear()
            return
    except IndexError:
        await message.answer("page not found!")
        return
    await state.update_data(paginator=paginator)
    for index, product in products.reset_index().iterrows():
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Add to favorites", callback_data="add_product_to_favorites")]
            ]
        )
        text: str = get_product_text_message(product)
        photo = types.URLInputFile(product.get('image'), filename=product.get('name'))
        await SendPhoto(chat_id=message.from_user.id, photo=photo, caption=text,
                        disable_notification=True, parse_mode="HTML", reply_markup=keyboard)

    await message.answer(f"page: {paginator.current_page + 1}", reply_markup=get_paginate_keyboard())


# @router.callback_query(ProductCallback.filter())
# async def add_product_in_user_favorite(call: types.CallbackQuery, state: FSMContext, callback_data: ProductCallback):
#     callback_data = callback_data.unpack(call.data)
    # SendPhoto(chat_id=call.message.from_user.id,)

    # print(call.message.json())
    # print(call.message.photo[0].file_unique_id)
    # print(call.json())
    # print(call.message.md_text)
    # name, price, shop = data.get("caption").split('\n')
    # name = name[3:]
    # price = price[9:]
    # shop = shop[8:]
    # url = data.get('caption_entities')[0].get("url")
    # with session() as s:
    #     user = s.query(User).filter_by(chat_id=call.from_user.id).first()
    #     product = Product(name=name, price=price, shop=shop, url=url, user=user.id)
    #     s.add(product)
    # await call.answer(text="Product added to favorites!", show_alert=True)
