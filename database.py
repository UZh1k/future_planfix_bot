import psycopg2

import config
import asyncio
import api


class PostgesOperations:

    def __init__(self, DB_URL: str = config.DB_URL):
        self.DB_URL = DB_URL
        self.connect = psycopg2.connect(config.DB_URL)
        self.cursor = self.connect.cursor()

    def db_update(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except psycopg2.InterfaceError:
                self.connect = psycopg2.connect(config.DB_URL)
                self.cursor = self.connect.cursor()
                return func(self, *args, **kwargs)
        return wrapper

    @db_update
    def create_table_if_not_exists(self):
        """
        Создает таблицу, если она еще не была создана
        :return:
        """
        sql_command = "CREATE TABLE IF NOT EXISTS chat_to_task " \
                      "(chat_id varchar(255), " \
                      "ext_id varchar(255), " \
                      "int_id varchar(255), " \
                      "type varchar(255));"
        self.cursor.execute(sql_command)
        self.connect.commit()


    @db_update
    def get_all_rows(self):
        """
        Выводит все строки из бд. Нужно для тестов
        :return:
        """
        self.cursor.execute(f"SELECT * FROM chat_to_task;")
        return self.cursor.fetchall()


    @db_update
    async def connect_chat_to_task(self, chat_id, task_id, tag) -> bool:
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
            self.cursor.execute(sql_command)
            self.connect.commit()
            return True
        else:
            return False


    @db_update
    def get_task_id(self, chat_id, tag):
        """
        Возвращает task_id по chat_id, tag из бд
        :param chat_id:
        :param tag:
        :return:
        """
        sql_command = f"SELECT ext_id " \
                      f"FROM chat_to_task " \
                      f"WHERE chat_id='{chat_id}' and type='{tag}'"
        self.cursor.execute(sql_command)
        return self.cursor.fetchone()[0]
