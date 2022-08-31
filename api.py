import datetime
from typing import Optional, List, Dict

from urllib.parse import quote
import aiohttp
import asyncio
import json
import re

import secret

import config


async def get_int_id(task_id) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.ENDPOINT}/task/{task_id}", data=secret.data['get_int_id'].format(task_id),
                               cookies=secret.cookies, headers=secret.headers) as resp:
            try:
                result = await resp.text()
                return re.search(r"Current\.task = '\d+';", result).group(0).split('\'')[1]
            except AttributeError:
                return None


async def get_check_list(task_id) -> List[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"{config.ENDPOINT}/ajax/", data=secret.data['get_check_list'].format(task_id),
                                cookies=secret.cookies, headers=secret.headers) as resp:
            result = await resp.json()
            tasks = []
            for point in result['CheckList']:
                if point['Status'] in [1, 2]:
                    tree_path_splitted = point['TreePath'].split(',')
                    nesting_level = len(tree_path_splitted[tree_path_splitted.index(task_id) + 1:])
                    tasks.append({"name": point['Description'] if point['Description'] else point['Title'],
                                  "nesting_level": nesting_level,
                                  "workers": [worker['Name'] for worker in point['WorkersList']]})
            return tasks


async def create_task(task_id, task) -> bool:
    async with aiohttp.ClientSession() as session:
        data_for_create = secret.data['create_task']
        data_for_create['TaskParentID'] = str(task_id)
        data_for_create['TaskCheckDescription'] = task
        async with session.post(url=f"{config.ENDPOINT}/ajax/", data=data_for_create,
                                cookies=secret.cookies, headers=secret.headers) as resp:
            try:
                result = await resp.json()
                return result['TaskCheck']['ID']
            except KeyError:
                return False


async def get_user(name) -> Dict | bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"{config.ENDPOINT}/ajax/", data=secret.data['get_all_users'],
                                cookies=secret.cookies, headers=secret.headers) as resp:
            result = await resp.json()
            users = []
            for usr in result['UserList']:
                if name.lower() in usr['FIO'].lower():
                    users.append({'FIO': usr['FIO'], 'LoginID': usr['LoginID']})

            if len(users) == 1:
                return users[0]
            else:
                return False


async def create_comment(draft_id: int, session: aiohttp.ClientSession) -> bool:
    data_for_create_comment = secret.data['create_comment']
    data_for_create_comment['draftid'] = draft_id
    async with session.post(url=f"{config.ENDPOINT}/ajax/", data=data_for_create_comment,
                            cookies=secret.cookies, headers=secret.headers) as resp:
        try:
            result = await resp.json()
            return result['Result'] == 'success'
        except KeyError:
            return False


async def delete_draft(draft_id: int, session: aiohttp.ClientSession) -> bool:
    data_for_delete_draft = secret.data['delete_draft']
    data_for_delete_draft['draftid'] = draft_id
    async with session.post(url=f"{config.ENDPOINT}/ajax/", data=data_for_delete_draft,
                            cookies=secret.cookies, headers=secret.headers) as resp:
        try:
            result = await resp.json()
            return result['Result'] == 'success'
        except KeyError:
            return False


async def create_analytics(user_login_id: int, username: str, arrived_time=datetime.datetime.now(),
                           departed_time=datetime.datetime.now() + datetime.timedelta(minutes=5),
                           comment: str = '') -> bool:
    async with aiohttp.ClientSession() as session:
        data = secret.data_for_analytics
        date = arrived_time.strftime('%d-%m-%Y')
        time_begin = arrived_time.strftime('%H:%M')
        time_end = departed_time.strftime('%H:%M')
        data['AttachedAnalitics'] = data['AttachedAnalitics'].substitute(date=date,
                                                                         time_begin=time_begin,
                                                                         time_end=time_end,
                                                                         login_id=user_login_id,
                                                                         username=username)
        data['ActionDescription'] = data['ActionDescription'].format(quote(comment))

        async with session.post(url=f"{config.ENDPOINT}/ajax/", data=data,
                                cookies=secret.cookies, headers=secret.headers) as resp:

            result = await resp.json()
            if result['Result'] == 'fail':
                return False

            draft_id = result['DraftID']

            save_comment = await create_comment(draft_id, session)
            delete_old_draft = await delete_draft(draft_id, session)

            return save_comment and delete_old_draft
