import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PF_TOKEN = os.environ.get("PF_TOKEN")
ENDPOINT = "https://smft.planfix.com/rest"
