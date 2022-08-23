from typing import Optional, List, Dict

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
                    nesting_level = len(tree_path_splitted[tree_path_splitted.index(task_id)+1:])
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
