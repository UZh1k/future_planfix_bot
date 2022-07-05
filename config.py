import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PF_TOKEN = os.environ.get("PF_TOKEN")

BOT_TYPE = os.environ.get("BOT_TYPE", "POLLING")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "localhost")
WEBHOOK_PORT = os.environ.get("WEBHOOK_PORT", "8000")

ENDPOINT = "https://smft.planfix.com/rest"

MONTAGE = "mnt"
MONTAGE_RU = "монтаж"
SETTING = "pnk"
SETTING_RU = "настройка"

TAGS = (MONTAGE, SETTING)
TAGS_RU = (MONTAGE_RU, SETTING_RU)
TRANS_DICT = dict(zip(TAGS, TAGS_RU))
