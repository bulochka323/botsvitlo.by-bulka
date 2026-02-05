import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiohttp import web
from config import BOT_TOKEN
from scheduler import setup_scheduler
from storage import init_db


# Веб-сервер для "пробудження" Render
async def handle(request):
    return web.Response(text="Bot is running!")


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # Запуск планувальника
    setup_scheduler(bot)

    # Налаштування сервера
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)

    logging.info("✅ Бот та веб-сервер запущені!")

    # Одночасний запуск сервера та бота
    await asyncio.gather(
        site.start(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())