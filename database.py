import datetime
from typing import Optional

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Boolean, ForeignKey, literal, exists, \
    DateTime, desc
from sqlalchemy.sql import select

import config
import api

metadata_obj = MetaData()

chat_to_task = Table('chat_to_task', metadata_obj,
                     Column('chat_id', String(255)),
                     Column('ext_id', String(255)),
                     Column('int_id', String(255)),
                     Column('type', String(255))
                     )

worker = Table('worker', metadata_obj,
               Column('id', Integer, primary_key=True),
               Column('name', String(255)),
               Column('login_id', String(255)),
               Column('tg_id', String(255))
               )

attendance = Table('attendance_test', metadata_obj,
                   Column('id', Integer, primary_key=True),
                   Column('arrived', Boolean),
                   Column('time', DateTime),
                   Column('worker_id', ForeignKey('worker.id')),
                   Column('comment', String(255)),
                   Column('is_marked', Boolean, default=False),
                   Column('add_worker', Boolean, default=False)
                   )


class PostgesOperations:

    def __init__(self, DB_URL: str = config.DB_URL):
        self.DB_URL = DB_URL
        self.engine = create_engine(config.DB_URL)
        self.connect = self.engine.connect()

    def db_update(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except:
                self.connect = self.engine.connect()
                return func(self, *args, **kwargs)

        return wrapper

    @db_update
    def create_table_if_not_exists(self):
        """
        Создает таблицу, если она еще не была создана
        :return:
        """
        metadata_obj.create_all(self.engine)

    @db_update
    def get_all_rows(self):
        """
        Выводит все строки из бд. Нужно для тестов
        :return:
        """
        return self.connect.execute(select(chat_to_task))

    @db_update
    async def connect_chat_to_task(self, chat_id: str, task_id: str, tag: str) -> bool:
        """
        Записывает в бд связь между id чата и id задачи из planfix
        :param chat_id:
        :param task_id:
        :param tag:
        :return:
        """
        ext_id = await api.get_int_id(task_id)
        if ext_id:
            upd = chat_to_task.update().values(ext_id=ext_id, int_id=task_id).where(
                chat_to_task.c.chat_id == chat_id and chat_to_task.c.type == tag)
            self.connect.execute(upd)

            sel = select([literal(chat_id), literal(ext_id), literal(task_id), literal(tag)]).where(
                ~exists([chat_to_task.c.chat_id]).where(
                    chat_to_task.c.chat_id == chat_id and chat_to_task.c.type == tag)
            )
            ins = chat_to_task.insert().from_select(["chat_id", "ext_id", "int_id", "type"], sel)
            self.connect.execute(ins)
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
        query = select(chat_to_task).where(chat_to_task.c.chat_id == chat_id and chat_to_task.c.type == tag)
        return self.connect.execute(query).fetchone()._mapping[chat_to_task.c.ext_id]

    @db_update
    def add_user(self, name, login_id, tg_id):
        ins = worker.insert().values(name=name, login_id=login_id, tg_id=tg_id)
        self.connect.execute(ins)

    @db_update
    def get_user_by_tg_id(self, tg_id: str) -> dict | bool:
        query = select(worker).where(worker.c.tg_id == tg_id)
        try:
            return self.connect.execute(query).fetchone()._mapping
        except AttributeError:
            return False

    @db_update
    def add_attendance(self, user_id: int, time=datetime.datetime.now(), arrived: bool = True, comment: str = '',
                       is_marked: bool = False, add_worker: bool = False):
        ins = attendance.insert().values(arrived=arrived, time=time, worker_id=user_id, comment=comment,
                                         is_marked=is_marked, add_worker=add_worker)
        self.connect.execute(ins)

    @db_update
    def get_user_last_attendance(self, user_id: int) -> dict | bool:
        """
        Вывод вида
        {'id': 1, 'arrived': True, 'time': datetime.datetime(2022, 8, 24, 11, 42, 16, 932650), 'worker_id': 1,
        'comment': ''}
        :param user_id:
        :return:
        """
        query = select(attendance).where(
            attendance.c.worker_id == user_id).where(attendance.c.arrived == True).where(
            attendance.c.is_marked == False) \
            .order_by(desc('time'))
        try:
            return self.connect.execute(query).fetchone()._mapping
        except AttributeError:
            return False

    @db_update
    def mark_user_last_attendance(self, user_id: int, last_attendance_id: Optional[int] = None):
        if not last_attendance_id:
            last_attendance = self.get_user_last_attendance(user_id)
            last_attendance_id = last_attendance['id']
        upd = attendance.update().values(is_marked=True).where(attendance.c.id == last_attendance_id)
        self.connect.execute(upd)
