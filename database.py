import config
import asyncio
import api

connect = psycopg2.connect(DB_URL)
cursor = connect.cursor()





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
    cursor.execute(sql_command)
    connect.commit()


def get_all_rows():
    """
    Выводит все строки из бд. Нужно для тестов
    :return:
    """
    cursor.execute(f"SELECT * FROM chat_to_task;")
    return cursor.fetchall()


async def connect_chat_to_task(chat_id, task_id, tag) -> bool:
    """
    Записывает в бд связь между id чата и id задачи из planfix
    :param chat_id:
    :param task_id:
    :param tag:
    :return:
    """
    ext_id = await api.get_int_id(task_id)
    if ext_id:
        sql_command = f"UPDATE chat_to_task SET ext_id='{ext_id}', int_id='{task_id}' WHERE chat_id='{chat_id}' and type='{tag}';" \
                      f"INSERT INTO chat_to_task (chat_id, ext_id, int_id, type) " \
                      f"SELECT '{chat_id}', '{ext_id}', '{task_id}', '{tag}' " \
                      f"WHERE NOT EXISTS (SELECT 1 FROM chat_to_task WHERE chat_id='{chat_id}' and type='{tag}');"
        cursor.execute(sql_command)
        connect.commit()
        return True
    else:
        return False


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
    cursor.execute(sql_command)
    return cursor.fetchone()[0]
