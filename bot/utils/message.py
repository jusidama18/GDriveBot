from time import sleep

from pyrogram.types import Message
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserNotParticipant
from pyrogram.errors import FloodWait, ChatWriteForbidden

from bot.utils import ikb, is_authorize
from bot import app, MUST_JOIN

async def sendMessage(message: Message, text: str, button=None):
    try:
        return await message.reply_text(
            text, quote=True, 
            disable_web_page_preview=True, disable_notification=True, 
            reply_markup=button,
        )
    except FloodWait as e:
        await sleep(e.x)
        return await sendMessage(message, text, button)

async def editMessage(message: Message, text, button=None):
    try:
        return await message.edit(
            text, disable_web_page_preview=True, 
            disable_notification=True, reply_markup=button
        )
    except FloodWait as e:
        sleep(e.x)
        return editMessage(message, text, button)

async def FSubs(message: Message):
    await check_auth(message)
    try:
        user = await app.get_chat_member(MUST_JOIN, message.from_user.id)
        if user.status == "kicked":
            return await sendMessage(message, "Sorry Sir, You are Banned to use me.")
    except UserNotParticipant:
        if MUST_JOIN.isalpha():
            link = f'https://t.me/{MUST_JOIN}'
        else:
            link = (await app.get_chat(MUST_JOIN)).invite_link
        try:
            return await sendMessage(message, f"You must join [@Jusidama]({link}) to use search Gdrive. After joining try again !", ikb({"✨ Join Channel ✨": link}))
        except ChatWriteForbidden:
            pass
    except ChatAdminRequired:
        return await sendMessage(message, f"I'm not admin in the MUST_JOIN chat : {MUST_JOIN} !")
    except Exception as e:
        return await sendMessage(message, f"**ERROR:** `{e}`")

async def check_auth(message: Message):
    reply = message.reply_to_message
    if reply:
        chat_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    else:
        chat_id = message.from_user.id if message.from_user else message.sender_chat.id

    check = await is_authorize(chat_id)
    if not check:
        return await sendMessage(message, "You are not authorize to use this bot !")
    else:
        pass