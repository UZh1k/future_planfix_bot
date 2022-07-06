import config


def create_table_if_not_exists():
    """
    Создает таблицу, если она еще не была создана
    :return:
    """
    sql_command = "CREATE TABLE IF NOT EXISTS chat_to_task " \
                  "(chat_id varchar(255), " \
                  "ext_id varchar(255), " \
                  "int_id varchar(255), " \
                  "type varchar(255));"
    config.cursor.execute(sql_command)
    config.connect.commit()


def get_all_rows():
    """
    Выводит все строки из бд. Нужно для тестов
    :return:
    """
    config.cursor.execute(f"SELECT * FROM chat_to_task;")
    return config.cursor.fetchall()


def connect_chat_to_task(chat_id, task_id, tag) -> bool:
    """
    Записывает в бд связь между id чата и id задачи из planfix
    :param chat_id:
    :param task_id:
    :param tag:
    :return:
    """
    sql_command = f"UPDATE chat_to_task SET ext_id='{task_id}' WHERE chat_id='{chat_id}' and type='{tag}';" \
                  f"INSERT INTO chat_to_task (chat_id, ext_id, type) " \
                  f"SELECT '{chat_id}', '{task_id}', '{tag}' " \
                  f"WHERE NOT EXISTS (SELECT 1 FROM chat_to_task WHERE chat_id='{chat_id}' and type='{tag}');"
    config.cursor.execute(sql_command)
    config.connect.commit()
    return True


def get_task_id(chat_id, tag):
    """
    Возвращает task_id по chat_id, tag из бд
    :param chat_id:
    :param tag:
    :return:
    """
    sql_command = f"SELECT ext_id " \
                  f"FROM chat_to_task " \
                  f"WHERE chat_id='{chat_id}' and type='{tag}'"
    config.cursor.execute(sql_command)
    return config.cursor.fetchone()[0]
