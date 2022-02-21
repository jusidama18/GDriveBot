""" WRITTEN BY @pokurt, https://github.com/pokurt"""
from sys import exc_info
from traceback import format_exception
from time import sleep
from functools import wraps

from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from bot import app, LOG_CHAT


def split_limits(text):
    if len(text) < 2048:
        return [text]

    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 2048:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    result.append(small_msg)

    return result


def capture_error(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            await client.leave_chat(message.chat.id)
            return
        except Exception as err:
            exc_type, exc_obj, exc_tb = exc_info()
            errors = format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            # time = NOW.strftime("%d/%m/%Y %H:%M:%S")
            if not message.sender_chat:
                error_feedback = split_limits(
                    "**JUSIDAMA ERROR || {}**\n\n `{}` (`@{}`) | `{}` | `{}`\n\n```{}```\n\n```{}```\n".format(
                        0 if not message.from_user else message.from_user.first_name,
                        "" if not message.from_user.username else message.from_user.username,
                        0 if not message.from_user else message.from_user.id,
                        0 if not message.chat else message.chat.id,
                        message.text or message.caption,
                        "".join(errors),
                    ),
                )
            else:
                error_feedback = split_limits(
                    "**JUSIDAMA ERROR || {}**\n\n `{}` (`@{}`) | `{}` | `{}`\n\n```{}```\n\n```{}```\n".format(
                        0 if not message.sender_chat else message.sender_chat.title,
                        "" if not message.sender_chat.username else message.sender_chat.username,
                        0 if not message.sender_chat else message.sender_chat.id,
                        0 if not message.chat else message.chat.id,
                        message.text or message.caption,
                        "".join(errors),
                    ),
                )
            for x in error_feedback:
                try:
                    await app.send_message(LOG_CHAT ,x)
                except FloodWait as e:
                    sleep(e.x)
            raise err

    return capture