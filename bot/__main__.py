import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove


async def main():
    bot = Bot(token=getenv("TOKEN"), parse_mode="HTML")
    dp = Dispatcher()
    from handlers.products import router
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
