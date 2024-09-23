# coding: utf-8
import aiohttp
import os
import aioftp
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from Parser import Result
from datetime import datetime

load_dotenv()
local_path = os.getenv('local_path')
url_main = os.getenv('url')
host = os.getenv('host')
login = os.getenv('login')
password = os.getenv('password')


async def Checker(bot):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36"
    }
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url=url_main, headers=headers) as response:
            page = await response.text()

            with open(f"{local_path}hg.htm", "w") as file:
                file.write(page)
            print(f"Проверка на обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            soup = BeautifulSoup(page, "lxml")
            date_update = soup.find(class_="ref")
            date_today = soup.find(class_="zgr")
            with open(f'{local_path}fileInfo.json') as json_file:
                date_upd = json.load(json_file)
                if date_upd["dateUpdate"] != date_update.text or date_upd["dateToday"] != date_today.text:
                    print("Зафиксировано обновление расписания.")
                    fileInfo = {
                        "dateUpdate": f'{date_update.text}',
                        "dateToday": f'{date_today.text}'
                    }
                    with open(f'{local_path}fileInfo.json', 'w') as file:
                        json.dump(fileInfo, file)
                    await ftpDownload()
                    await Result(bot)
                else:
                    print("Обновлений не найдено")
async def ftpDownload():
    client = aioftp.Client()
    try:
        await client.connect(host)
        await client.login(login, password)
        for file, info in (await client.list()):
            if file.name.startswith("cg"):
                await client.download(file, destination=f"{local_path}")
                print("Downloading.. " + file.name)
    except Exception as e:
        print(f"Ошибка скачивания файла с FTP сервера: {e}")
    finally:
        await client.quit()
