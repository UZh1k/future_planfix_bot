import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

OWNER_IDS = os.environ.get("OWNER_IDS").split(',')

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PF_TOKEN = os.environ.get("PF_TOKEN")

BOT_TYPE = os.environ.get("BOT_TYPE", "POLLING")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "localhost")
WEBHOOK_PORT = os.environ.get("WEBHOOK_PORT", "8000")

DB_URL = os.environ.get("DB_URL")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

ENDPOINT = os.environ.get("ENDPOINT")

MONTAGE = "mount"
MONTAGE_RU = "монтаж"
SETTING = "tuning"
SETTING_RU = "настройка"

TAGS = (MONTAGE, SETTING)
TAGS_RU = (MONTAGE_RU, SETTING_RU)
TRANS_DICT = dict(zip(TAGS, TAGS_RU))
TRANS_DICT_RU = dict(zip(TAGS_RU, TAGS))
