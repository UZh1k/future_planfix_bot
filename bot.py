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
    Слушает /start и /help
    """
    print(message)
    await bot.send_message(message.chat.id, "hello")


@dp.message_handler(lambda message: is_group_message(message), commands=config.TAGS)
async def send_task(message: Message):
    """
    Слушает /mnt и /pnk
    Отправляет список невыполненных задач по монтажу или настройке соответственно
    :param message:
    :return:
    """
    print(message)
    await bot.send_message(message.chat.id, ' - Создание задач в телеграмме\n'
                                            ' - перенос задач в нужную папку\n'
                                            ' - Контроль над задачей\n'
                                            '   - подпункт')


@dp.message_handler(lambda message: is_group_message(message), commands=map(lambda x: f"connect_{x}", config.TAGS))
async def connect_task(message: Message):
    """
    Слушает /connect_mnt и /connect_pnk <id задачи из PlanFix>
    Привязывает задачу к id группы из телеграмма
    :param message:
    :return:
    """
    if len(message.text.split()) == 1:
        await bot.send_message(message.chat.id,
                               f"Используйте формат {message.text} <id задачи из PlanFix>")
    else:
        await bot.send_message(message.chat.id,
                               f'Привязали группу к задаче #{config.TRANS_DICT[message.text.split()[0].split("connect_")[-1]]}')


@dp.message_handler(lambda message: is_group_message(message) and filter_add_task(message))
async def add_task(message: Message):
    """
    Слушает #настройка и #монтаж \n <список задач, каждая с новой строки>
    Добавляет задачи из группы по соответсвующему тэгу
    :param message:
    :return:
    """
    await bot.send_message(message.chat.id, 'Добавили задачи')


def is_group_message(message: Message) -> bool:
    """
    :param message:
    :return: True, если сообщение пришло из группы
    """
    return message.chat.type == 'group'


def filter_add_task(message: Message):
    """
    :param message:
    :return: True, если сообщение соответствует начинается на тэг
    """
    for tag in config.TAGS_RU:
        if message.text.lower().startswith(f"#{tag}"):
            return True
    return False


async def on_startup(dispatcher: Dispatcher):
    """
    Выводит информацию о боте при его включении
    :param dispatcher:
    :return:
    """
    print(await bot.me)
    if config.BOT_TYPE == "WEBHOOK":
        await bot.set_webhook(config.WEBHOOK_URL)


if __name__ == "__main__":
    if config.BOT_TYPE == "POLLING":
        executor.start_polling(dispatcher=dp,
                               on_startup=on_startup,
                               skip_updates=True)
    elif config.BOT_TYPE == "WEBHOOK":
        print(config.WEBHOOK_URL)
        print(config.WEBHOOK_PORT)
        executor.start_webhook(dispatcher=dp,
                               webhook_path=f"",
                               on_startup=on_startup,
                               skip_updates=True,
                               host="0.0.0.0",
                               port=config.WEBHOOK_PORT,
                               )
