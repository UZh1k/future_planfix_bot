from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, Message, AllowedUpdates
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


@dp.message_handler(lambda message: is_group_message(message), commands=config.TAGS)
async def send_task(message: Message):
    print(message)
    await bot.send_message(message.chat.id, ' - Создание задач в телеграмме\n'
                                            ' - перенос задач в нужную папку\n'
                                            ' - Контроль над задачей\n'
                                            '   - подпункт')


@dp.message_handler(lambda message: is_group_message(message), commands=map(lambda x: f"connect_{x}", config.TAGS))
async def connect_task(message: Message):
    if len(message.text.split()) == 1:
        await bot.send_message(message.chat.id,
                               f"Используйте формат {message.text} <id задачи из PlanFix>")
    else:
        await bot.send_message(message.chat.id,
                               f'Привязали группу к задаче #{config.TRANS_DICT[message.text.split()[0].split("connect_")[-1]]}')


@dp.message_handler(lambda message: is_group_message(message) and filter_add_task(message))
async def add_task(message: Message):
    await bot.send_message(message.chat.id, 'Добавили задачи')


def is_group_message(message: Message) -> bool:
    return message.chat.type == 'group'


def filter_add_task(message: Message):
    for tag in config.TAGS_RU:
        if message.text.lower().startswith(f"#{tag}"):
            return True
    return False


async def on_startup(dispatcher: Dispatcher):
    print(await bot.me)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True, allowed_updates=AllowedUpdates.all())
