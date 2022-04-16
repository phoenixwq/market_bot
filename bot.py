from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.bot_command import BotCommand
from app.db import create_db
from app.handlers import common, favorites, products
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN')
bot = Bot(token=TOKEN)


def register_handlers(dp):
    common.register_common_handlers(dp)
    favorites.register_favorites_handlers(dp)
    products.register_products_handlers(dp)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/search", description="Product search"),
        BotCommand(command='/favorites', description="Favorites")
    ]
    await bot.set_my_commands(commands)


async def main():
    global bot
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers(dp)

    await set_commands(bot)
    await dp.start_polling()


if __name__ == '__main__':
    create_db()
    asyncio.run(main())
