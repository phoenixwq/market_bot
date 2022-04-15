from aiogram import Dispatcher
from aiogram import types


async def start(message: types.Message):
    user = message.from_user
    await message.answer(f"Привет, {user.first_name.capitalize()}, я бот, который находит товары в твоем мухосранске")


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(start, commands="start", state="*")
