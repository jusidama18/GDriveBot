from bot.utils import capture_error, add_auth, rmv_auth, auth_chat, command
from bot import app, OWNER_ID, LOGGER

@app.on_message(command(['auth', 'unauth', 'chat'], sudo=True))
@capture_error
async def auth_chat(_, message):
    ALLOWED_CHAT = await auth_chat()
    target = str(message.command[0]).split("@", maxsplit=1)[0]
    msg = await message.reply_text('`Processing....`', quote=True)
    if not message.reply_to_message:
        try:
            ids = int(message.text.split(None, 1)[1])
        except IndexError:
            ids = message.chat.id
        except ValueError:
            return await msg.edit('`Send Valid Chat ID !`')
    else:
        if message.reply_to_message.from_user:
            ids = message.reply_to_message.from_user.id
        else:
            return await msg.delete()
    
    if 'chat' in target:
        txt = ''
        for chat in ALLOWED_CHAT:
            txt += f'➤ `{chat}`\n'
        check = bool(message.chat.id in ALLOWED_CHAT)
        return await msg.edit(f'**[ Authorized Chat ID ({len(ALLOWED_CHAT)}) ]**\n\n' + txt + f'\n**Is Authorized Chat :** `{check}`')

    if 'un' not in target:
        if ids in ALLOWED_CHAT:
            return await msg.edit('`This Chat ID Already In Allowed Chat !`')
        else:
            LOGGER.info(f"Auth : {ids}")
            await add_auth(ids)
            return await msg.edit('`Success Add This Chat ID In Allowed Chat For Next 24 Hours !`')
    else:
        if ids not in ALLOWED_CHAT:
            return await msg.edit('`This Chat ID Not In Allowed Chat !`')
        else:
            await rmv_auth(ids)
            LOGGER.info(f"Unauth : {ids}")
            return await msg.edit('`Success Remove This Chat ID From Allowed Chat !`')