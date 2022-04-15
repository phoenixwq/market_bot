from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from app.parser.parser import GoogleShopParser
from app.parser.paginator import Paginator
from aiogram import Dispatcher
import aiogram.utils.markdown as fmt

PAGE_SIZE = 3


class SearchProduct(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_get_products = State()


def get_product_text_message(product: dict) -> str:
    name = product.get("name")
    price = product.get("price")
    shop = product.get("shop").split('.')[0]
    link = product.get("link")
    image = product.get('image')
    return fmt.text(
        fmt.hbold(name),
        fmt.text("price:", fmt.text(price)),
        fmt.text("shop:", fmt.text(shop)),
        fmt.hlink("link", link),
        fmt.hide_link(image),
        sep="\n"
    )


async def get_product_name(message: types.Message):
    await message.answer("Введите название товара, который хотите найти!")
    await SearchProduct.waiting_for_product_name.set()


async def get_products_by_name(message: types.Message, state: FSMContext):
    user = message.from_user
    await message.answer(f"{user.first_name.capitalize()}, вот что мне удалось найти!")
    parser = GoogleShopParser()
    data = parser.get_products(message.text.lower())
    paginator = Paginator(data, PAGE_SIZE)
    await state.update_data(paginator=paginator)

    for product in paginator.current():
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Добавить в избранное", callback_data="add_product"))
        text = get_product_text_message(product)
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton("prev"), types.KeyboardButton("next"),
    ).add(types.KeyboardButton("exit"))
    await message.answer(
        f"Текущая страница: {paginator.current_page + 1}, Количество страниц:{paginator.count_page + 1}",
        reply_markup=keyboard)

    await SearchProduct.next()


async def watch_page(message: types.Message, state: FSMContext):
    user_message = message.text.lower()
    if user_message not in ('next', 'prev', 'exit'):
        await message.answer("Please use the keyboard bellow")
        return
    data = await state.get_data()
    paginator = data.get("paginator")
    try:
        if user_message == "next":
            products = paginator.next()
        elif user_message == "prev":
            products = paginator.prev()
        else:
            await message.reply("searched completed!", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            return
    except IndexError:
        await message.answer("page not found!")
        return

    await state.update_data(paginator=paginator)
    for product in products:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Добавить в избранное", callback_data="add_product"))
        text = get_product_text_message(product)
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await message.answer(f"Current page: {paginator.current_page + 1}, Count page:{paginator.count_page + 1}")


async def add_product_in_user_favorite(call: types.CallbackQuery):
    await call.answer(text="Товар добавлен в избранное!", show_alert=True)


def register_products_handlers(dp: Dispatcher):
    dp.register_message_handler(get_product_name, commands="search", state="*")
    dp.register_message_handler(get_products_by_name, state=SearchProduct.waiting_for_product_name)
    dp.register_message_handler(watch_page, state=SearchProduct.waiting_for_get_products)
    dp.register_callback_query_handler(add_product_in_user_favorite, lambda query: query.data == "add_product",
                                       state='*')
