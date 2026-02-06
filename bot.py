import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types # Додали types
from aiogram.filters import Command # Додали фільтр команд
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from config import BOT_TOKEN
from scheduler import setup_scheduler
from storage import init_db

# --- ОБРОБНИКИ ПОВІДОМЛЕНЬ ---

async def cmd_start(message: types.Message):
    """Обробник команди /start"""
    await message.answer(
        "👋 Привіт! Я бот для відстеження графіків світла.\n"
        "Я буду надсилати сповіщення, коли з'явиться нова інформація."
    )

# --- ВЕБ-СЕРВЕР ---

async def handle(request):
    return web.Response(text="Бот працює!")

async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # РЕЄСТРАЦІЯ ОБРОБНИКІВ (Важливий момент!)
    dp.message.register(cmd_start, Command("start"))

    # Запуск перевірки графіків
    setup_scheduler(bot)

    # Налаштування сервера для Render
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)

    logging.info(f"✅ Бот запущено на порту {port}")

    await site.start()

    try:
        # Видаляємо старі повідомлення, які прийшли, поки бот був офлайн
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())