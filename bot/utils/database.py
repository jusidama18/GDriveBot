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