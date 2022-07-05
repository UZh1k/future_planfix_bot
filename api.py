import config
import asyncio
import aiohttp

url = "https://smft.planfix.ru"
HEADERS = {'User-Agent': 'Chrome/98.0.4758.80'}


async def get_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as resp:
            print(await resp.text())


if __name__ == "__main__":
    asyncio.run(get_html(url))