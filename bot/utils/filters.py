from .database import *

async def is_authorize(chat_id: int) -> bool:
    chats = await auth_chat()
    return bool(chat_id in chats)