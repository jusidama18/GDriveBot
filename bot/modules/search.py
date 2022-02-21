import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import MessageEmpty, MessageNotModified

from bot.drive import GoogleDriveHelper, drive
from bot.utils import (
    ikb, FSubs, capture_error, command,
    get_readable_time, sendMessage, editMessage
)
from bot import app, RESULTS_COUNT, ALLOWED_CHAT

i = 0
ii = 0
m = None
keyboard = None
data = None

@app.on_message(command("search", allow_chat=True))
@capture_error
async def search(_, message):
    global i, m, data
    await FSubs(message)
    start = time.time() # soon
    if len(message.command) < 2:
        await sendMessage(message, '/seach Filename')
        return
    query = message.text.split(' ',maxsplit=1)[1]
    m = await sendMessage(message, "**Searching....**")
    drive = GoogleDriveHelper()
    data = drive.drive_list(query)

    results = len(data)
    i = 0
    i += RESULTS_COUNT

    if results == 0:
        await editMessage(message, "Found Literally Nothing.")
        return

    text = f"**Total Results:** __{results}__ **in {get_readable_time(time.time() - start)}\n"
    for count in range(min(i, results)):
        if data[count]['type'] == "file":
            text += f"\n📄  **[{data[count]['name']} ({data[count]['size']})]({data[count]['drive_url']})**"
        else:
            text += f"\n📂  **[{data[count]['name']}]({data[count]['drive_url']})**"
    if len(data) > RESULTS_COUNT:
        button = ikb({"<<   Previous": "previous", "Next   >>": "next"})
    else:
        button = None
    try:
        await editMessage(message, text, button)
    except (MessageEmpty, MessageNotModified):
        pass


@app.on_callback_query(filters.regex("previous"))
async def previous_callbacc(_, query):
    global i, ii, m, data
    if i < RESULTS_COUNT:
        await query.answer(
            "Already at 1st page, Can't go back.",
            show_alert=True
        )
        return
    ii -= RESULTS_COUNT
    i -= RESULTS_COUNT
    text = ""

    for count in range(ii, i):
        try:
            if data[count]['type'] == "file":
                text += f"\n📄  **[{data[count]['name']} ({data[count]['size']})]({data[count]['drive_url']})**"
            else:
                text += f"\n📂  **[{data[count]['name']}]({data[count]['drive_url']})**"
        except IndexError:
            continue

    button = ikb({"<<   Previous": "previous", "Next   >>": "next"})
    try:
        await editMessage(query.message, text, button)
    except (MessageEmpty, MessageNotModified):
        pass


@app.on_callback_query(filters.regex("next"))
async def next_callbacc(_, query):
    global i, ii, m, data
    ii = i
    i += RESULTS_COUNT
    text = ""

    for count in range(ii, i):
        try:
            if data[count]['type'] == "file":
                text += f"\n📄  **[{data[count]['name']} ({data[count]['size']})]({data[count]['drive_url']})**"
            else:
                text += f"\n📂  **[{data[count]['name']}]({data[count]['drive_url']})**"
        except IndexError:
            continue

    button = ikb({"<<   Previous": "previous", "Next   >>": "next"})
    try:
        await editMessage(query.message, text, button)
    except (MessageEmpty, MessageNotModified):
        pass