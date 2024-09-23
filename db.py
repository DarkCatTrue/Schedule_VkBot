# coding: utf-8
import asyncio
import json
import aioodbc
import os
from dotenv import load_dotenv
from ApiRequests import message_sender

load_dotenv()
local_path = os.getenv('local_path')
Driver = os.getenv('Driver')
Server = os.getenv('Server')
Database = os.getenv('Database')
Trusted_connection = os.getenv('Trusted_connection')
connectionString = f'Driver={Driver};Server={Server};DataBase={Database};Trusted_connection={Trusted_connection};'


async def Insert(chat_id, group_name):
    async with aioodbc.connect(dsn=connectionString) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT COUNT(*) FROM Chats WHERE ChatId = ?",
                (chat_id,)
            )
            count = await cursor.fetchone()

            if count[0] == 0:
                await cursor.execute(
                    "INSERT INTO Chats (ChatId, [Group]) VALUES (?, ?)",
                    (chat_id, group_name)
                )
                await conn.commit()
                print(f"Была добавлена группа: {group_name} с chat_id {chat_id}")
                return True
            else:
                print(f"Беседа с chat_id {chat_id} уже существует в бд")
                return False


async def Select():
    async with aioodbc.create_pool(dsn=connectionString) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT [Group], [ChatId] FROM Chats")
                groups = await cursor.fetchall()
                return [(group[0], group[1]) for group in groups]


async def Delete(chat_id):
    async with aioodbc.connect(dsn=connectionString) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT COUNT(*) FROM Chats WHERE ChatId = ?",
                (chat_id,)
            )
            count = await cursor.fetchone()
            if count[0] == 1:
                try:
                    await cursor.execute(
                        f"DELETE FROM Chats WHERE ChatId = ?",
                        (chat_id,))
                    await conn.commit()
                    print(f"Беседа с :{chat_id} успешно удалилась из бд")
                    return True
                except Exception as e:
                    print(f"Ошибка удаления из бд: {e}")
            else:
                print("Беседа уже была удалена из бд")
                return False


async def Check_old_groups():
    async with aioodbc.connect(dsn=connectionString) as conn:
        async with conn.cursor() as cursor:
            with open(f"{local_path}groups.json") as json_file:
                groups = json.load(json_file)
            keys = list(groups.keys())
            query = f"DELETE FROM Chats WHERE [Group] NOT IN ({', '.join(['?'] * len(keys))})"
            try:
                await cursor.execute(query, keys)
                print("Произошла успешная проверка на удаление неактуальных групп в бд")
            except Exception as e:
                print(f"Ошибка в проверке на удаление неактуальных групп в бд: {e}")


async def GetGroup(bot, chat_id):
    async with aioodbc.create_pool(dsn=connectionString) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    query = "SELECT [Group] FROM Chats WHERE ChatId = ?;"
                    await cursor.execute(query, (chat_id,))
                    row = await cursor.fetchone()
                    await message_sender(chat_id=chat_id, message=f"Вы подписаны на рассылку группы: {row[0]}", bot=bot)
                except Exception as e:
                    print(f"Ошибка поиска имени группы у ChatId:{chat_id}, {e}")
                    await message_sender(chat_id=chat_id, message=f"Вы не подписаны на рассылку.", bot=bot)


async def run_all():
    await GetGroup()


if __name__ == '__main__':
    asyncio.run(run_all())
