import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

# Подгружаем переменные окружения из .env
load_dotenv()

bot_token = os.getenv("TOKEN")
# Ловим отсутствие токена
if not bot_token:
    exit("Error: no token provided")

storage = MemoryStorage()


# Создаём бот и его обработчик
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=storage)
