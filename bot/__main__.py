import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher
from commands import set_commands
from bot.handlers import common, favorites, products
from bot.db import create_db


async def main():
    bot = Bot(token=getenv("TOKEN"), parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(favorites.router)
    dp.include_router(products.router)

    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    create_db()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
