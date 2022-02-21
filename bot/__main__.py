from importlib import import_module, reload as reloads
from pyrogram import idle

from bot.modules import ALL_MODULES
from bot import app

for module in ALL_MODULES:
    imported_module = import_module("bot.modules." + module)
    reloads(imported_module)

if __name__ == "__main__":
    app.start()
    idle()
