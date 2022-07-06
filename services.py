from typing import List, Optional

from aiogram.types import Message

import config


def is_group_message(message: Message) -> bool:
    """
    :param message:
    :return: True, если сообщение пришло из группы
    """
    return message.chat.type == 'group'


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
