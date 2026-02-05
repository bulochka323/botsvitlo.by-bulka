import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiohttp import web
from config import BOT_TOKEN
from scheduler import setup_scheduler
from storage import init_db


# Веб-сервер для "пробудження" через Cron-job.org
async def handle(request):
    return web.Response(text="Бот працює!")


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # Запуск перевірки графіків
    setup_scheduler(bot)

    # Налаштування сервера для Render
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()

    # Render автоматично надає порт
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)

    logging.info(f"✅ Бот запущено на порту {port}")

    await site.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())