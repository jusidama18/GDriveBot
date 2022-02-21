from os.path import exists
from pyrogram import Client
from logging import basicConfig, FileHandler, StreamHandler, getLogger, INFO, WARNING
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

basicConfig(
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        FileHandler("logs.txt"),
        StreamHandler()
    ],
    level=INFO
)

LOGGER = getLogger(__name__)
getLogger("pyrogram").setLevel(WARNING)

is_config = exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

mongo_client = MongoClient(MONGO_URL)
db = mongo_client.bot

# Input Your Own ID or Hash if u want
app = Client(
    ":memory:", 
    bot_token=BOT_TOKEN, 
    api_id=API_ID,
    api_hash=API_HASH
)