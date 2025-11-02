import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from handlers import start_help, tasks, focus, profile, settings
from database.db import init_db
from utils.logger import setup_logger

async def main():
    setup_logger()
    logging.info("Bot ishga tushmoqda...")
    init_db()
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    start_help.register_handlers(dp)
    tasks.register_handlers(dp)
    focus.register_handlers(dp)
    profile.register_handlers(dp)
    settings.register_handlers(dp)
    
    logging.info("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot to'xtatildi")
