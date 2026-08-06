import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MAIN_GROUP_ID = int(os.getenv("MAIN_GROUP_ID", 0))
ABBOS_GROUP_ID = int(os.getenv("ABBOS_GROUP_ID", 0))


SESSION_NAME = os.getenv("SESSION_NAME", "")