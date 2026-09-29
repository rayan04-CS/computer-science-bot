import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from database import init_db
from handlers.user import router as user_router
from handlers.admin import router as admin_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise RuntimeError("ضع BOT_TOKEN داخل ملف .env")

async def main():
    await init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    print("Computer Science Student Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
