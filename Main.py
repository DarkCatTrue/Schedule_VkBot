# coding: utf-8
from vkbottle import CtxStorage, BaseStateGroup
from vkbottle.bot import Bot, Message, rules
from Finder import *
from Fchecker import Checker
from db import Insert, Delete, GetGroup
load_dotenv()
token = os.getenv('token')
bot = Bot(token=token)
group_id = os.getenv('group_id')
ctx = CtxStorage()


class RegData(BaseStateGroup):
    GROUP = 0
    RESULT = 1


@bot.on.chat_message(rules.ChatActionRule("chat_invite_user"))
async def bot_joined(message: Message) -> None:
    if message.action.member_id == -225692189:
        print(f"Бот присоединился к беседе:{message.peer_id}")
        await message.answer(
            "Здравствуйте, я бот ЗабГК. Моя задача - отправлять расписание вашей группы, когда оно обновилось в этот чат.\n О работе бота вы можете узнать в  @zabgc_schedule(сообществе), в разделе FAQ(руководство пользователя), которое является обязательным для прочтения. Там описываются все основные моменты работы бота.\nСоветуем подписаться на сообщество в целях информирования о возможных технических работах!")


@bot.on.chat_message(lev="/del")
async def delete_from_db(message: Message):
    delete = await Delete(message.peer_id)
    if delete:
        await message.answer("Вы успешно отписались от рассылки.")
    else:
        await message.answer("Не удалось отписать вас от рассылки. Возможно вы не были подписаны на рассылку.")


@bot.on.chat_message(lev="/info")
async def get_group(message: Message):
    await GetGroup(bot, message.peer_id)


@bot.on.chat_message(lev="/add")
async def insert_to_db(message: Message):
    await bot.state_dispenser.set(message.peer_id, RegData.GROUP)
    return "Пожалуйста, введите вашу группу."


@bot.on.chat_message(state=RegData.GROUP)
async def group_handler(message: Message):
    if message.reply_message and message.reply_message.from_id == -225692189:
        ctx.set("group", message.text)
        group = ctx.get("group")
        finder = await group_finder(group)
        if finder == group:
            insert = await Insert(message.peer_id, group)
            if insert:
                await message.answer(f"Вы успешно подписались на рассылку группы: {group}")
                await bot.state_dispenser.delete(message.peer_id)
            else:
                await message.answer("Сейчас вы не можете подписаться на обновления какой-либо группы, т.к вы уже подписались на обновления.")
        else:
            await bot.state_dispenser.set(message.peer_id, RegData.RESULT)
            return f"Пожалуйста, выберите одну из указанных групп:\n{finder}"
    else:
        pass


@bot.on.chat_message(state=RegData.RESULT)
async def regist_confirmed(message: Message):
    if message.reply_message and message.reply_message.from_id == -225692189:
        ctx.set("result", message.text)
        group = ctx.get("result")
        finder = await group_finder(group)
        if finder == group:
            insert = await Insert(message.peer_id, group)
            if insert:
                await message.answer(f"Вы успешно подписались на рассылку группы: {group}")
                await bot.state_dispenser.delete(message.peer_id)
            else:
                await message.answer("Сейчас вы не можете подписаться на обновления какой-либо группы, т.к вы уже подписались на обновления.")
        else:
            await message.answer("Вы ввели не точное название у группы. Название группы должно быть идентичным с названием в расписании.")
            await bot.state_dispenser.delete(message.peer_id)
    else:
        pass


@bot.loop_wrapper.interval(seconds=60)
async def notification():
    try:
        await Checker(bot)
    except Exception as e:
        print(f"Ошибка чекера: {e}")
        pass

bot.run_forever()
