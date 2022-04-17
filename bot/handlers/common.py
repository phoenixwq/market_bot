from aiogram import types
from bot.db.tables import User
from bot.db.base import get_or_create
from aiogram.dispatcher.router import Router

router = Router()


@router.message(commands=["start"])
async def start(message: types.Message):
    user = message.from_user
    get_or_create(User, chat_id=user.id)
    await message.answer(f"Hi, {user.first_name.capitalize()}, i'm a bot that finds goods in your muhosransk")
