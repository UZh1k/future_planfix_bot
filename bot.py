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


async def user_is_owner(message: Message):
    if str(message.from_user.id) in config.OWNER_IDS:
        return True
    else:
        await bot.send_message(message.chat.id, 'Эту функцию могут выполнять только администраторы')
        return False


@dp.message_handler(commands=['start', 'help'])
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
    tag = services.get_tag_from_string(message.text, config.TAGS_RU)
    task_id = database.get_task_id(message.chat.id, config.TRANS_DICT_RU[tag])
    tasks = await api.get_check_list(task_id)
    tasks_pretty = [f'{"    " * task[1]}- {task[0]}' for task in tasks]
    text = "\n".join(tasks_pretty)
    await bot.send_message(message.chat.id, text)


@dp.message_handler(lambda message: services.is_group_message(message),
                    commands=map(lambda x: f"connect_{x}", config.TAGS))
async def connect_task(message: Message):
    """
    Слушает /connect_mount и /connect_tuning <id задачи из PlanFix>
    Привязывает задачу к id группы из телеграмма
    :param message:
    :return:
    """
    if await user_is_owner(message):
        splitted_message = message.text.split()
        if len(splitted_message) == 1 or len(splitted_message) > 2 or not splitted_message[1].isdigit():
            await bot.send_message(message.chat.id,
                                   f"Используйте формат {message.text} <id задачи из PlanFix>")
        else:
            task_id = splitted_message[-1]
            tag = services.get_tag_from_string(splitted_message[0], config.TAGS)
            if await database.connect_chat_to_task(chat_id=message.chat.id,
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
    if await user_is_owner(message):
        splitted_by_n = message.text.split('\n')
        first_string_splitted = splitted_by_n[0].split()
        tag = services.get_tag_from_string(first_string_splitted[0], config.TAGS)
        task_id = database.get_task_id(message.chat.id, tag)

        tasks = [" ".join(first_string_splitted[1:])] if len(first_string_splitted) > 1 else []
        if len(splitted_by_n) > 1:
            tasks.extend(splitted_by_n[1:])
        print(tasks)  # таски в листе отправляем в апи
        everything_worked = True
        nesting_ids = [task_id]

        for i in range(len(tasks)):
            dot_count = tasks[i].split()[0].count('.')
            tasks[i] = [dot_count, tasks[i].replace('.', '', dot_count)]  # sample_task == [3, 'SAMPLE TEXT']
        print(tasks)

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
                print(tasks)
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

                print(f'ADD task:    ID list: {nesting_ids} -- Current nesting lvl: {nesting_lvl} -- Task text: {task}')

                current_id = await api.create_task(nesting_ids[-1], task)
                if current_id:
                    nesting_ids += [current_id]
                everything_worked = everything_worked and current_id

        if everything_worked:
            await bot.send_message(message.chat.id, f'Добавили пункты для задачи #{config.TRANS_DICT[tag]} {task_id}')
        else:
            await bot.send_message(message.chat.id, f'Что-то пошло не так: не все пункты добавлены.')


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
