import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
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

    # Виправлений запуск бота згідно з помилкою у логах Render
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # Запуск перевірки графіків
    setup_scheduler(bot)

    # Налаштування сервера для Render
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()

    # Використовуємо динамічний порт від Render
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)

    logging.info(f"✅ Бот запущено на порту {port}")

    await site.start()

    # Запуск бота у режимі отримання повідомлень
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())