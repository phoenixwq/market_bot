from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        (
            [
                BotCommand(command="search", description="search products by name"),
                BotCommand(command="favorites", description="favorites")
            ]
        )
    ]
    for command in commands:
        await bot.set_my_commands(commands=command)
