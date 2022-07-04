from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, Message
from aiogram.utils import executor

import config


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['main'])
async def start_message(message: Message):
    print(message)
    await bot.send_message(message.chat.id, 'Дарова')


if __name__ == "__main__":
    executor.start_polling(dp)