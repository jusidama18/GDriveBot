from bot import db

authdb = db.auths
folderdb = db.folders
searchdb = db.search
restartdb = db.restart
# Later

async def start_restart(chat_id: int, message_id: int):
    await restartdb.update_one(
        {"something": "something"},
        {
            "$set": {
                "chat_id": chat_id,
                "message_id": message_id,
            }
        },
        upsert=True,
    )


async def clean_restart() -> dict:
    data = await restartdb.find_one({"something": "something"})
    if not data:
        return {}
    await restartdb.delete_one({"something": "something"})
    return {
        "chat_id": data["chat_id"],
        "message_id": data["message_id"],
    }


async def auth_chat() -> list:
    auths = await authdb.find_one({"auth": "auth"})
    if not auths:
        return []
    return auths["authorize"]


async def add_auth(chat_id: int) -> bool:
    auths = await auth_chat()
    auths.append(chat_id)
    await authdb.update_one(
        {"auth": "auth"}, {"$set": {"authorize": auths}}, upsert=True
    )
    return True


async def rmv_auth(user_id: int) -> bool:
    auths = await auth_chat()
    auths.remove(user_id)
    await authdb.update_one(
        {"auth": "auth"}, {"$set": {"authorize": auths}}, upsert=True
    )
    return True