from bot.utils import capture_error, sendMessage, FSubs, command
from bot import app

@app.on_message(command("start"))
@capture_error
async def start_command(_, message):
    await FSubs(message)
    await sendMessage(message, "What did you expect to happen? Try /help")


@app.on_message(command("help", allow_chat=True))
@capture_error
async def help_command(_, message):
    await FSubs(message)
    await sendMessage(message, "/search [Query]")