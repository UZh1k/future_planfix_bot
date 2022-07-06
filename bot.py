from typing import List, Optional

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, Message
from aiogram.utils import executor

import config
import database
import services

dsn = f'dbname={config.DB_NAME} user={config.DB_USER} password={config.DB_PASSWORD} host={config.DB_HOST}'
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    """
    Слушает /start и /help
    """
    await bot.send_message(message.chat.id, "hello")


@dp.message_handler(lambda message: services.is_group_message(message) and services.filter_show_task(message))
async def show_task(message: Message):
    """
    Слушает #настройка и #монтаж
    Отправляет список невыполненных задач по монтажу или настройке соответственно
    :param message:
    :return:
    """
    tag = services.get_tag_from_string(message.text, config.TAGS_RU)
    task_id = database.get_task_id(message.chat.id, config.TRANS_DICT_RU[tag])
    await bot.send_message(message.chat.id, f'Ищем чеклист по задаче {task_id}\n'
                                            '- Создание задач в телеграмме\n'
                                            ' - перенос задач в нужную папку\n'
                                            ' - Контроль над задачей\n'
                                            '   - подпункт')


@dp.message_handler(lambda message: services.is_group_message(message), commands=map(lambda x: f"connect_{x}", config.TAGS))
async def connect_task(message: Message):
    """
    Слушает /connect_mount и /connect_tuning <id задачи из PlanFix>
    Привязывает задачу к id группы из телеграмма
    :param message:
    :return:
    """
    splitted_message = message.text.split()
    if len(splitted_message) == 1 or len(splitted_message) > 2 or not splitted_message[1].isdigit():
        await bot.send_message(message.chat.id,
                               f"Используйте формат {message.text} <id задачи из PlanFix>")
    else:
        task_id = splitted_message[-1]
        tag = services.get_tag_from_string(splitted_message[0], config.TAGS)
        if database.connect_chat_to_task(chat_id=message.chat.id,
                                         task_id=task_id,
                                         tag=tag):
            await bot.send_message(message.chat.id,
                                   f'Привязали группу к задаче #{config.TRANS_DICT[tag]}')
        else:
            await bot.send_message(message.chat.id,
                                   f'Не вышло привязать группу к задаче #{config.TRANS_DICT[tag]}. '
                                   f'Перепроверьте данные')


@dp.message_handler(lambda message: services.is_group_message(message), commands=config.TAGS)
async def add_task(message: Message):
    """
    Слушает /mount и /tuning \n <список задач, каждая с новой строки>
    Добавляет задачи из группы по соответствующему тэгу
    :param message:
    :return:
    """
    splitted_by_n = message.text.split('\n')
    first_string_splitted = splitted_by_n[0].split()
    tag = services.get_tag_from_string(first_string_splitted[0], config.TAGS)
    task_id = database.get_task_id(message.chat.id, tag)

    tasks = [" ".join(first_string_splitted[1:])] if len(first_string_splitted) > 1 else []
    if len(splitted_by_n) > 1:
        tasks.extend(splitted_by_n[1:])
    print(tasks)  # таски в листе отправляем в апи

    await bot.send_message(message.chat.id, f'Добавили пункты для задачи #{config.TRANS_DICT[tag]} {task_id}')


async def on_startup(dispatcher: Dispatcher):
    """
    Выводит информацию о боте при его включении
    :param dispatcher:
    :return:
    """
    database.create_table_if_not_exists()
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
