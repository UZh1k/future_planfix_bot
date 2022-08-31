import datetime

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, Message
from aiogram.utils import executor

import api
import config
import database
import services

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)
postgres = database.PostgesOperations()


async def user_is_owner(message: Message):
    if str(message.from_user.id) in config.OWNER_IDS:
        return True
    else:
        await bot.send_message(message.chat.id, 'Эту функцию могут выполнять только администраторы')
        return False


@dp.message_handler(lambda message: services.is_group_message(message), commands=['start', 'help'])
async def send_welcome(message: Message):
    """
    Слушает /start и /help
    """
    print(message)
    await bot.send_message(message.chat.id,
                           "/start и /help - выводит список команд\n"
                           "/mount и /tuning <список задач> сохраняет задачи для монтажа или настройки\n"
                           "/connect_mount и /connect_tuning <id задачи из url> - соединяет чат с задачей монтажа "
                           "или настройки\n"
                           "#монтаж и #настройка - выводят невыполненные задачи по монтажу или настройки")


@dp.message_handler(lambda message: services.is_group_message(message) and services.filter_show_task(message))
async def show_task(message: Message):
    """
    Слушает #настройка и #монтаж
    Отправляет список невыполненных задач по монтажу или настройке соответственно
    :param message:
    :return:
    """
    print(message)
    tag = services.get_tag_from_string(message.text, config.TAGS_RU)
    task_id = postgres.get_task_id(message.chat.id, config.TRANS_DICT_RU[tag])
    tasks = await api.get_check_list(task_id)
    tasks_pretty = []
    for task in tasks:
        task_pretty = f'{"    " * task["nesting_level"]}- {task["name"]}'
        if task['workers']:
            task_pretty += f" ({', '.join(task['workers'])})"
        tasks_pretty.append(task_pretty)
    text = "\n".join(tasks_pretty)
    if text:
        for message_slices in services.split_text_by_chunks(text):
            await bot.send_message(message.chat.id, message_slices)
    else:
        await bot.send_message(message.chat.id, "Все задачи выполнены")


@dp.message_handler(lambda message: services.is_group_message(message),
                    commands=map(lambda x: f"connect_{x}", config.TAGS))
async def connect_task(message: Message):
    """
    Слушает /connect_mount и /connect_tuning <id задачи из PlanFix>
    Привязывает задачу к id группы из телеграмма
    :param message:
    :return:
    """
    print(message)
    if await user_is_owner(message):
        splitted_message = message.text.split()
        if len(splitted_message) == 1 or len(splitted_message) > 2 or not splitted_message[1].isdigit():
            await bot.send_message(message.chat.id,
                                   f"Используйте формат {message.text} <id задачи из PlanFix>")
        else:
            task_id = splitted_message[-1]
            tag = services.get_tag_from_string(splitted_message[0], config.TAGS)
            if await postgres.connect_chat_to_task(chat_id=message.chat.id,
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
    print(message)
    if await user_is_owner(message):
        splitted_by_n = message.text.split('\n')
        first_string_splitted = splitted_by_n[0].split()
        tag = services.get_tag_from_string(first_string_splitted[0], config.TAGS)
        task_id = postgres.get_task_id(message.chat.id, tag)

        tasks = [" ".join(first_string_splitted[1:])] if len(first_string_splitted) > 1 else []
        if len(splitted_by_n) > 1:
            tasks.extend(splitted_by_n[1:])
        everything_worked = True
        nesting_ids = [task_id]

        for i in range(len(tasks)):
            dot_count = tasks[i].split()[0].count('.')
            tasks[i] = [dot_count, tasks[i].replace('.', '', dot_count)]  # sample_task == [3, 'SAMPLE TEXT']

        if tasks[0][0] > 0:
            everything_worked = False
            await bot.send_message(message.chat.id,
                                   f'Некорректный уровень вложенности первого пункта: первый пункт не должен быть вложенным.')

        if len(tasks) > 1:
            for i in range(len(tasks) - 1):
                # CASE "< 0":  |... 2    |     CASE "== 0":  |. 2    |     CASE "== 1": |. 2    |     CASE "> 1":  |. 2    |
                #              |. 3      |                   |. 3    |                  |.. 3   |                  |... 3  |
                if (tasks[i + 1][0] - tasks[i][0]) > 1:
                    everything_worked = False
                    await bot.send_message(message.chat.id,
                                           f'Некорректный уровень вложенности {i + 2} пункта: {i + 2} пункт должен быть вложен не больше, чем на 1 уровень относительно {i + 1} пункта.')

        if everything_worked:
            for task in tasks:
                if len(task) != 2:
                    everything_worked = False
                    break

                nesting_lvl = task[0]
                task = task[1]
                if nesting_lvl + 1 > len(nesting_ids):
                    everything_worked = False
                    break
                elif nesting_lvl + 1 < len(nesting_ids):
                    nesting_ids = nesting_ids[:nesting_lvl + 1 - len(nesting_ids)]  # remove useless for now parents

                current_id = await api.create_task(nesting_ids[-1], task)
                if current_id:
                    nesting_ids += [current_id]
                everything_worked = everything_worked and current_id

        if everything_worked:
            await bot.send_message(message.chat.id, f'Добавили пункты для задачи #{config.TRANS_DICT[tag]} {task_id}')
        else:
            await bot.send_message(message.chat.id, f'Что-то пошло не так: не все пункты добавлены.')


@dp.message_handler(lambda message: services.is_private_message(message), commands=['start', 'help'])
async def send_welcome(message: Message):
    """
    Слушает /start и /help
    """
    await bot.send_message(message.chat.id,
                           "Введите Вашу фамилию (и имя при необходимости)")


@dp.message_handler(lambda message: services.is_private_message(message))
async def create_worker(message: Message):
    print(message)
    user_info = await api.get_user(message.text)
    if user_info:
        postgres.add_user(user_info["FIO"], user_info["LoginID"], str(message.chat.id))
        await bot.send_message(message.chat.id, f'Мы вас нашли!\n\n'
                                                f'ФИО: {user_info["FIO"]}\n'
                                                f'ID Планфикса: {user_info["LoginID"]}')
    else:
        await bot.send_message(message.chat.id,
                               f'Мы вас не нашли. Перепроверьте данные, добавьте имя или обратитесь к администратору')


@dp.message_handler(lambda message: services.is_group_message(message) and (
        "прибыл" in message.text.lower() or "убыл" in message.text.lower()))
async def add_analytics(message: Message):
    print(message)
    user = postgres.get_user_by_tg_id(str(message.from_user.id))
    parsed_message = services.parse_attendance_message(message.text)
    print(parsed_message)
    if parsed_message['arrived'] == parsed_message['departed'] == True:
        postgres.add_attendance(user_id=user['id'], arrived=True, time=parsed_message['time'],
                                comment=parsed_message['comment'], is_marked=True,
                                add_worker=parsed_message['add_worker'])
        postgres.add_attendance(user_id=user['id'], arrived=False,
                                time=parsed_message['time'] + datetime.timedelta(minutes=5),
                                comment=parsed_message['comment'], is_marked=True,
                                add_worker=parsed_message['add_worker'])

        res = await api.create_analytics(user_login_id=user['login_id'],
                                         username=user['name'],
                                         arrived_time=parsed_message['time'],
                                         departed_time=parsed_message['time'] + datetime.timedelta(minutes=5),
                                         comment=parsed_message['comment'],
                                         add_worker=parsed_message['add_worker'])
        await bot.send_message(message.chat.id, f'Операция прошла {res}')


    elif parsed_message['arrived']:
        postgres.add_attendance(user_id=user['id'], arrived=True, time=parsed_message['time'],
                                comment=parsed_message['comment'],
                                add_worker=parsed_message['add_worker'])
    elif parsed_message['departed']:
        postgres.add_attendance(user_id=user['id'], arrived=False, time=parsed_message['time'],
                                comment=parsed_message['comment'], is_marked=True,
                                add_worker=parsed_message['add_worker'])

    # "Неверный формат сообщения, пожалуйста, введите его в формате:\nприбыл *объект* *время (опционально)*")


async def on_startup(dispatcher: Dispatcher):
    """
    Выводит информацию о боте при его включении
    :param dispatcher:
    :return:
    """
    postgres.create_table_if_not_exists()
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
