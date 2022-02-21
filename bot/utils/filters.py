from email import message
from pyrogram.types import Message
from .database import *

async def is_authorize(message: Message) -> bool:
    chat_id = message.from_user.id if message.from_user else message.sender_chat.id
    chats = await auth_chat()
    return bool(chat_id in chats)