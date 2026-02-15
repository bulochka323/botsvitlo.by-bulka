import asyncio
import logging
import hashlib
import httpx
from datetime import datetime
from aiogram import Bot
from aiogram.types import URLInputFile, InputMediaPhoto
from config import CHANNEL_ID

CITY_DATA = {
    "kyiv": {
        "url": "https://raw.githubusercontent.com/Baskerville42/outage-data-ua/refs/heads/main/images/kyiv/gpv-all-today.png",
        "name": "Київ"},
    "dnipro": {
        "url": "https://raw.githubusercontent.com/Baskerville42/outage-data-ua/refs/heads/main/images/dnipro/gpv-all-today.png",
        "name": "Дніпро"},
    "lviv": {
        "url": "https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/images/Lvivoblenerho/gpv-all-today.png",
        "name": "Львів"}
}

last_hashes = {"kyiv": None, "dnipro": None, "lviv": None}


def get_hash(content):
    return hashlib.md5(content).hexdigest()


async def check_updates(bot: Bot):
    logging.info("🚀 Моніторинг запущено. Формуємо єдиний підпис...")

    while True:
        try:
            updates_found = False
            updated_cities = []

            async with httpx.AsyncClient() as client:
                for city, data in CITY_DATA.items():
                    try:
                        res = await client.get(data["url"], timeout=30)
                        if res.status_code == 200:
                            new_hash = get_hash(res.content)
                            if last_hashes[city] != new_hash:
                                updates_found = True
                                updated_cities.append(data["name"])
                                last_hashes[city] = new_hash
                    except Exception as e:
                        logging.error(f"Помилка {city}: {e}")

            if updates_found:
                current_time = datetime.now().strftime("%H:%M %d.%m.%Y")

                # Створюємо один спільний текст для всього повідомлення
                cities_list = ", ".join(updated_cities)
                main_caption = (
                    f"⚡️ <b>ОНОВЛЕНО ГРАФІКИ</b>\n"
                    f"🔄 Зміни у регіонах: <b>{cities_list}</b>\n"
                    f"⏰ Час перевірки: {current_time}\n\n"
                    f" Актуальні графіки для Києва, Дніпра та Львова надіслано вище."
                )

                media_group = []
                items = list(CITY_DATA.items())

                for i, (city, data) in enumerate(items):
                    # Додаємо підпис ТІЛЬКИ до першого елемента альбому
                    # Telegram відобразить його як загальний текст під усім блоком фото
                    media_group.append(
                        InputMediaPhoto(
                            media=URLInputFile(data["url"]),
                            caption=main_caption if i == 0 else None,
                            parse_mode="HTML"
                        )
                    )

                await bot.send_media_group(CHANNEL_ID, media=media_group)
                logging.info(f"✅ Альбом надіслано з підписом для: {cities_list}")

        except Exception as e:
            logging.error(f"Помилка в циклі: {e}")

        await asyncio.sleep(900)


def setup_scheduler(bot: Bot):
    asyncio.create_task(check_updates(bot))