from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, Message
from aiogram.utils import executor

import config


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    print(message)
    await bot.send_message(message.chat.id, "hello")


@dp.message_handler(commands=config.TAGS)
async def send_task(message: Message):
    print(message)
    await bot.send_message(message.chat.id, 'Создание задач в телеграмме '
                                            'перенос задач в нужную папку '
                                            'Контроль над задачей '
                                            'подпункт')


async def on_startup(dispatcher: Dispatcher):
    print(await bot.me)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
