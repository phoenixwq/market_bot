from aiogram import types
from bot.db.tables import User
from bot.db.base import get_or_create
from aiogram.dispatcher.router import Router

router = Router()


@router.message(commands=["menu"])
async def menu(message: types.Message):
    keyboard = [
        [
            types.KeyboardButton(text="🔎"),
            types.KeyboardButton(text="⭐"),
        ]
    ]

    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer("🔎 - search product\n⭐ - favorites", reply_markup=markup)


@router.message(commands=["start"])
async def start(message: types.Message):
    user = message.from_user
    get_or_create(User, chat_id=user.id)
    await message.answer(f"Hi, {user.first_name.capitalize()}, i'm a bot that finds goods in your muhosransk")
    await menu(message)
