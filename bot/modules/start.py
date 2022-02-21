from pyrogram import filters
from bot.utils import capture_error, sendMessage, FSubs
from bot import app, SUDO_CHATS_ID

@app.on_message(filters.command("start") & ~filters.edited & filters.chat(SUDO_CHATS_ID))
@capture_error
async def start_command(_, message):
    await FSubs(message)
    await sendMessage(message, "What did you expect to happen? Try /help")


@app.on_message(filters.command("help") & ~filters.edited)
@capture_error
async def help_command(_, message):
    await FSubs(message)
    await sendMessage(message, "/search [Query]")