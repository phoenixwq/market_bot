from aiogram.dispatcher.filters import BaseFilter
from aiogram import types


class PaginateFilter(BaseFilter):
    commands: list = ["prev", "next", "exit"]

    async def __call__(self, message: types.Message) -> bool:
        if message.text in self.commands:
            return True
        await message.answer("Please use the keyboard bellow")
        return False
