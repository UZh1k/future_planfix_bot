import datetime
from typing import List, Optional
import re

from aiogram.types import Message

import config


def is_group_message(message: Message) -> bool:
    """
    :param message:
    :return: True, если сообщение пришло из группы
    """
    return message.chat.type == 'group'


def is_private_message(message: Message) -> bool:
    """
    :param message:
    :return: True, если сообщение пришло из группы
    """
    return message.chat.type == 'private'


def filter_show_task(message: Message):
    """
    :param message:
    :return: True, если сообщение соответствует начинается на тэг
    """
    return message.text.startswith('#') and get_tag_from_string(message.text.split()[0], config.TAGS_RU)


def get_tag_from_string(string: str, tags: List[str] = config.TAGS) -> Optional[str]:
    """
    Возвращает, какой тэг в строке или ничего. Важно следить за списком передаваемых тэгов!
    :param string:
    :param tags:
    :return:
    """
    for tag in tags:
        if tag in string:
            return tag
    return None


def split_text_by_chunks(st: str) -> List[str]:
    """
    Разделяет вывод бота на чанки, чтобы не было ошибки о слишком длинном сообщении
    :param st: Исходный текст
    :return: Массив строк, разделенный на чанки
    """
    if len(st) > 4000:
        texts = []
        text_len = len(st)
        count = text_len // 4000 + 1

        for i in range(count):
            texts.append(st[4000 * i: 4000 * (i + 1)])

        return texts
    else:
        return [st]


def parse_time(arrive_time: str) -> datetime.datetime:
    if arrive_time != '':
        if len(arrive_time) == 4 and arrive_time.isdigit():
            hours, minutes = arrive_time[:2], arrive_time[2:]
        else:
            hours, minutes = re.split('[:. ]', arrive_time)
        return datetime.datetime.now().replace(hour=int(hours), minute=int(minutes))
    return datetime.datetime.now()


def parse_attendance_message(text: str) -> dict:
    arrive_time = re.search("\d{1,2}[:.]{0,1}\d{1,2}", text)
    if not arrive_time:
        arrive_time = ''
    else:
        arrive_time = arrive_time.group(0)
    add_worker = "+1" in text
    all_without_comment = ['+1', arrive_time, config.ARRIVED, config.DEPARTED, ' ', '/']
    comment = text.lower()
    for deleter in all_without_comment:
        comment = comment.replace(deleter, '')
    comment = comment.upper()

    result = {'time': parse_time(arrive_time), 'comment': comment, 'add_worker': add_worker,
              'arrived': config.ARRIVED in text.lower(), 'departed': config.DEPARTED in text.lower()}

    if result['arrived'] and result['departed']:
        second_time = re.search("\d{1,2}[:.]{0,1}\d{1,2}", comment)
        if second_time:
            second_time = second_time.group(0)
            result['second_time'] = parse_time(second_time)
            result['comment'] = result['comment'].replace(second_time, '')

    return result
