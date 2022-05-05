from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        (
            [
                BotCommand(command="search", description="geo-search for products by name"),
                BotCommand(command="favorites", description="favorites"),
                BotCommand(command="location", description="send geolocation for search")
            ]
        )
    ]
    for command in commands:
        await bot.set_my_commands(commands=command)