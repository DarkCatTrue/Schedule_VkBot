# coding: utf-8
import asyncio
from vkbottle import VKAPIError


async def message_sender(bot, chat_id, message):
    try:
        await asyncio.sleep(0.25)
        await bot.api.messages.send(peer_id=chat_id, message=message, random_id=0)
    except VKAPIError as vkerror:
        print(f"Ошибка отправки сообщения: {vkerror}")
