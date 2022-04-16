from aiogram import Dispatcher
from aiogram import types
from app.db.tables import User
from app.db.base import get_or_create


async def start(message: types.Message):
    user = message.from_user
    get_or_create(User, chat_id=user.id)
    await message.answer(f"Hi, {user.first_name.capitalize()}, i'm a bot that finds goods in your muhosransk")


def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands="start", state="*")
