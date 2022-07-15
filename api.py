from typing import Optional, List

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
                    tasks.append((point['Description'] if point['Description'] else point['Title'], len(point['TreePath'].split(',')) - 2))
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
