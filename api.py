from typing import Optional, List

import aiohttp
import asyncio
import json
import secret

import config


async def get_int_id(task_id) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=config.ENDPOINT, data=secret.data['get_int_id'].format(task_id),
                                cookies=secret.cookies, headers=secret.headers) as resp:
            try:
                result = await resp.json()
                return result['Task']['General']['ID']
            except KeyError:
                return None


async def get_check_list(task_id) -> List[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=config.ENDPOINT, data=secret.data['get_check_list'].format(task_id),
                                cookies=secret.cookies, headers=secret.headers) as resp:
            result = await resp.json()
            tasks = []
            for point in result['CheckList']:
                if point['Status'] == 2:
                    tasks.append((point['Title'], len(point['TreePath'].split(',')) - 2))
            return tasks


async def create_task(task_id, task) -> bool:
    async with aiohttp.ClientSession() as session:
        data_for_create = secret.data['create_task']
        data_for_create['TaskParentID'] = str(task_id)
        data_for_create['TaskCheckDescription'] = task
        async with session.post(url=config.ENDPOINT, data=data_for_create,
                                cookies=secret.cookies, headers=secret.headers) as resp:
            try:
                result = await resp.json()
                return result['TaskCheck']['ID']
            except KeyError:
                return False
