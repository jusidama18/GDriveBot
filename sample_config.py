from os import environ

HEROKU = bool(
    environ.get('DYNO')
)

if HEROKU:
    BOT_TOKEN = environ.get('BOT_TOKEN')
    RESULTS_COUNT = int(environ.get('RESULTS_COUNT', 4))  # NOTE Number of results to show, 4 is better
    SUDO_CHATS_ID = [i for i in str(environ.get('SUDO_CHATS_ID')).split(' ')]
    CHANNEL = environ.get('CHANNEL', "@Jusidama")
    MONGO_URL = environ.get('MONGO_URL')
    LOG_CHAT = int(environ.get('LOG_CHAT'))
    API_ID = environ.get('API_ID')
    API_HASH = environ.get('API_HASH')
    APPDRIVE_EMAIL = environ.get('APPDRIVE_EMAIL')
    APPDRIVE_PASS = environ.get('APPDRIVE_PASS')
    GDTOT_CRYPT = environ.get('GDTOT_CRYPT')
    IS_TEAM_DRIVE = bool(environ.get('IS_TEAM_DRIVE').lower() == 'true')
    USE_SERVICE_ACCOUNTS = bool(environ.get('USE_SERVICE_ACCOUNTS').lower() == 'true')
    FOLDER_ID = environ.get('FOLDER_ID')
else:
    BOT_TOKEN = "1629027959:AAEaTw4s2qaAL3mYP3fQRnE"
    RESULTS_COUNT = 4  # NOTE Number of results to show, 4 is better
    SUDO_CHATS_ID = [-1001485393652, -1005456463651]
    CHANNEL = "@Jusidama"
    LOG_CHAT = -1001485393652
    API_ID = 6
    API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
    MONGO_URL = "mongodb+srv://username:password@cluster0.ksiis.mongodb.net/YourDataBaseName?retryWrites=true&w=majority"
    APPDRIVE_EMAIL = ""
    APPDRIVE_PASS = ""
    GDTOT_CRYPT = ""
    IS_TEAM_DRIVE = False
    FOLDER_ID = ""
    USE_SERVICE_ACCOUNTS = False

# Later in mongo

DRIVE_NAME = [
    "Root",  # folder 1 name
    "Cartoon",  # folder 2 name
    "Course",  # folder 3 name
    "Movies",  # ....
    "Series",  # ......
    "Others"  # and soo onnnn folder n names
]

DRIVE_ID = [
    "1B9A3QqQqF31IuW2om3Qhr-wkiVLloxw8",  # folder 1 id
    "12wNJTjNnR-CNBOTnLHqe-1vqFvCRLecn",  # folder 2 id
    "11nZcObsJJHojHYg43dBS0_eVvJrSD7Nf",  # and so onn... folder n id
    "10_hTMK8HE8k144wOTth_3x1hC2kZL-LR",
    "1-oTctBpyFcydDNiptLL09Enwte0dClCq",
    "1B9A3QqQqF31IuW2om3Qhr-wkiVLloxw8"
]

INDEX_URL = [
    "https://dl.null.tech/0:",  # folder 1 index link
    "https://dl.null.tech/0:/Cartoon",  # folder 2 index link
    "https://dl.null.tech/0:/Course",  # and soo on folder n link
    "https://dl.null.tech/0:/MOVIES",
    "https://dl.null.tech/0:/Series",
    "https://dl.null.tech/0:/Roms"
]
