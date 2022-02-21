from pyrogram import filters

from bot.utils import *
from bot import app, LOGGER


@app.on_message(filters.command('clone'))
@capture_error
@new_thread
async def clone(_, message):
    args = message.text.split(" ", maxsplit=1)
    link = args[1] if len(args) > 1 else ''
    