from bot.drive import GoogleDriveHelper
from bot.utils import (
        new_thread, capture_error, sendMessage, command,
        editMessage, gdtot, appdrive, is_supported, FSubs
    )
from bot import app, LOGGER

cmds = ['clone', 'count']

@app.on_message(command(cmds, allow_chat=True))
@capture_error
@new_thread
async def clone(_, message):
    await FSubs(message)
    args = message.text.split(" ", maxsplit=1)
    link = args[1] if len(args) > 1 else ''
    user_id = message.from_user.id if message.from_user else message.sender_chat.id

    msg = await sendMessage(message, f"<b>Processing:</b> <code>{link}</code>")
    if link == '':
        return await editMessage(msg, f"/{message.command[0]} URL")
    
    deletes = False # Seems stupid lmao
    LOGGER.info(f'User: {user_id} : {link}')
    try:
        check, types = is_supported(link)
        if not check:
            return await editMessage(msg, "`Link Not Supported`")
        if 'new.gdtot' in types:
            deletes = True
            link = gdtot(link)
        elif ('appdrive' or 'driveapp') in link:
            apdict = appdrive(link)
            link = apdict.get('gdrive_link')
            if apdict.get('link_type') == 'login':
                deletes = True
    except Exception as e:
        LOGGER.error(f"ERROR - {user_id} - {link} : {e}")
        return await editMessage(msg, str(e))
    
    await editMessage(msg, f"**Cloning :** `{link}`")
    LOGGER.info(f"Cloning - {user_id} - : {link}")
    target = str(message.command[0]).split("@")[0]
    try:
        gd = GoogleDriveHelper()
        if cmds[1] in target:
            result, button = gd.count(link)
        else:
            result, button = gd.clone(link)
        if deletes:
            LOGGER.info(f"Deleting: {link}")
            gd.deleteFile(link)
        return await editMessage(msg, result, button)
    except Exception as e:
        if deletes:
            LOGGER.info(f"Deleting: {link}")
            gd.deleteFile(link)
        return await editMessage(msg, str(e))
    
    
    
        

    

    