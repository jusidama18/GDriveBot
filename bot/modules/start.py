from pyrogram import filters
from bot.utils import capture_error, sendMessage, FSubs
from bot import app, ALLOWED_CHAT

@app.on_message(filters.command("start") & ~filters.edited & filters.chat(ALLOWED_CHAT))
@capture_error
async def start_command(_, message):
    await FSubs(message)
    await sendMessage(message, "What did you expect to happen? Try /help")


@app.on_message(filters.command("help") & ~filters.edited)
@capture_error
async def help_command(_, message):
    await FSubs(message)
    await sendMessage(message, "/search [Query]")