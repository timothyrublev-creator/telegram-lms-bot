import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import init_db
from handlers import start, menu, lessons, game, jobs, rating, referral, ai_expert, admin

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация всех роутеров
dp.include_router(start.router)
dp.include_router(menu.router)
dp.include_router(lessons.router)
dp.include_router(game.router)
dp.include_router(jobs.router)
dp.include_router(rating.router)
dp.include_router(referral.router)
dp.include_router(ai_expert.router)
dp.include_router(admin.router)

async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
