from importlib import import_module, reload as reloads
from asyncio import get_event_loop, sleep, exceptions
from pyrogram import idle

from bot.modules import ALL_MODULES
from bot.utils.database import clean_restart
from bot import app, LOG_CHAT

for module in ALL_MODULES:
    imported_module = import_module(f'bot.modules.{module}')
    reloads(imported_module)

async def start_bot():
    data = await clean_restart()
    try:
        if data:
            await app.edit_message_text(
                data["chat_id"],
                data["message_id"],
                "**Restarted Successfully**",
            )

        else:
            await app.send_message(LOG_CHAT, "Bot started!")
    except Exception:
        pass

    await idle()
    await app.stop()

loop = get_event_loop()

if __name__ == "__main__":
    try:
        try:
            loop.run_until_complete(start_bot())
        except exceptions.CancelledError:
            pass
        loop.run_until_complete(sleep(3.0))
    finally:
        loop.close()
