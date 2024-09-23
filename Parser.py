# coding: utf-8
import os
from dotenv import load_dotenv
import tabulate
import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
from db import Select, Delete
from ApiRequests import message_sender

load_dotenv()
local_path = os.getenv('local_path')
url = os.getenv('url_groups')


class DataStorage:
    def __init__(self):
        self.data_list = []
        self.data_date = []
        self.data_group_name = []

    def add_data(self, data):
        self.data_list.append(data)

    def add_date(self, date):
        self.data_date.append(date)

    def add_group_name(self, group_name):
        self.data_group_name.append(group_name)

    def get_data(self):
        return self.data_list

    def get_date(self):
        return self.data_date

    def get_group_name(self):
        return self.data_group_name


async def webparser():
    print("Создание htm файла с группами..")
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url=url, headers=headers) as response:
            page = await response.text()
            print("Парсинг информации о группах..")

            with open(f"{local_path}cg.htm", "w") as file:
                file.write(page)

            print("Создание json групп..")
            soup = BeautifulSoup(page, "lxml")
            all_groups_hrefs = soup.find_all(class_="z0")
            groups = {}

            for item in all_groups_hrefs:
                item_text = item.text
                item_href = item.get("href")
                groups[item_text] = item_href

            json_data = json.dumps(groups, indent=4, ensure_ascii=False)

            with open(f"{local_path}groups.json", "w") as file:
                file.write(json_data)

            print("Успешно")


async def fileParser(data_storage, filename):
    with open(f"{local_path}{filename}") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")

    h1 = soup.find("h1")
    table = soup.find("table", class_="inf")
    rows = table.find_all("tr")
    hdtags = soup.find_all(class_="hd", rowspan="6")
    date = soup.find(class_="hd", rowspan="6")
    Nulclass = table.find_all(class_="nul")
    brtag = table.select("br")

    for br in brtag:
        br.replace_with(" ")
    for hd in hdtags:
        hd.replace_with("")
    for nul in Nulclass:
        nul.string.replace_with("Нет пары")
    group_name = [h1.text[8:]]
    dateTomorrow = [date.text]
    data_storage.add_group_name(group_name)
    data_storage.add_date(dateTomorrow)
    for item in rows[3:9]:
        table_data = item.find_all("td")
        data = [j.text for j in table_data]
        data_storage.add_data(data)


async def Result(bot):
    await webparser()
    groups_and_chat_ids = await Select()

    with open(f"{local_path}groups.json") as json_file:
        groups_dict = json.load(json_file)

    for group, chat_id in groups_and_chat_ids:
        data_storage = DataStorage()
        filename = groups_dict.get(group)
        if filename:
            await fileParser(data_storage, filename)
            data = data_storage.get_data()
            date_t = data_storage.get_date()
            group = data_storage.get_group_name()
            schedule = tabulate.tabulate(data, tablefmt="plain")
            group_name = tabulate.tabulate(group, tablefmt="plain")
            date = tabulate.tabulate(date_t, tablefmt="plain")
            message = f"Группа: {group_name}\nДата: {date}\n{schedule}"
            try:
                await message_sender(bot, chat_id, message)
            except Exception as e:
                print(f"Ошибка отправки рассылки {e} . Бот был удалён из беседы:{chat_id} не при помощи команды.")
                await Delete(chat_id)
                pass


if __name__ == "__main__":
    asyncio.run(webparser())
