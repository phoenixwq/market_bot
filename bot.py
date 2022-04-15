from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.bot_command import BotCommand
from dotenv import load_dotenv
import asyncio
import logging
import os
from app.handlers import common, products

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/search", description="Product search"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    dotenv_path = os.path.join('.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    TOKEN = os.environ.get('TOKEN')

    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    common.register_handlers_common(dp)
    products.register_products_handlers(dp)

    await set_commands(bot)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
