from pyrogram import filters
from .database import *
from bot import app, OWNER_ID, ALLOWED_CHAT

async def is_authorize(chat_id: int) -> bool:
    chats = await auth_chat()
    return bool(chat_id in chats)

def command(command, sudo: bool = False, allow_chat: bool = False):
    BOT_USERNAME = (app.get_me()).username
    if isinstance(command, list):
        cmds = []
        for i in command:
            cmds.extend([i, i + '@' + BOT_USERNAME])
        command = filters.command(cmds)
    else:
        command = filters.command([command, command + '@' + BOT_USERNAME])
    if sudo:
        command = command & filters.user(OWNER_ID)
    elif allow_chat:
        command = command & filters.chat(ALLOWED_CHAT)
    return command & ~filters.edited
