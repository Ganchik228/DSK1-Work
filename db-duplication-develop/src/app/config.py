from dotenv import load_dotenv
import os
from telegram import Bot


load_dotenv()

LogPath = "/home/wall/DB_duplication/log.log"

USERNAME = str(os.getenv("USERNAME"))
PASSWORD = str(os.getenv("PASSWORD"))
DBNAME = str(os.getenv("DBNAME"))
DBHOSTNAME = str(os.getenv("DBHOSTNAME"))
TOKEN = str(os.getenv("TOKEN"))
CHAT_ID = str(os.getenv("CHAT_ID"))
PORT = str(os.getenv("PORT"))
bot = Bot(token=TOKEN)
