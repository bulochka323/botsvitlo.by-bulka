import asyncio
import logging
import datetime
import hashlib
import httpx
from aiogram import Bot
from aiogram.types import URLInputFile
from config import CHANNEL_ID

# Посилання на джерела
KYIV_IMAGE_URL = "https://raw.githubusercontent.com/Baskerville42/outage-data-ua/refs/heads/main/images/kyiv/gpv-all-today.png"
DNIPRO_IMAGE_URL = "https://raw.githubusercontent.com/Baskerville42/outage-data-ua/refs/heads/main/images/dnipro/gpv-all-today.png"
LVIV_JSON_URL = "https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/data/Lvivoblenerho.json"

# Словник для зберігання хешів останніх надісланих даних
# Це дозволяє боту "пам'ятати", що він уже надсилав
last_sent_hashes = {
    "kyiv": None,
    "dnipro": None,
    "lviv": None
}


def get_content_hash(content):
    """Створює MD5 хеш контенту для порівняння змін"""
    if isinstance(content, str):
        content = content.encode()
    return hashlib.md5(content).hexdigest()


async def get_lviv_text_schedule():
    """Парсер для Львова (текстовий)"""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(LVIV_JSON_URL, timeout=10)
            if res.status_code == 200:
                data = res.json()
                today_ts = str(data.get('today', ''))
                day_data = data.get('data', {}).get(today_ts, {})
                if not day_data: return None

                text = f"📅 <b>Графік ЛЬВІВ на {datetime.date.today().strftime('%d.%m.%Y')}</b>\n\n"
                for group, hours in day_data.items():
                    line = "".join(["⬛" if str(hours.get(str(h), '')).lower() == 'no' else "⬜" for h in range(1, 25)])
                    text += f"<b>Гр {group}:</b>\n<code>{line}</code>\n"
                text += f"\n⬜-є світло | ⬛-немає\n🔗 <a href='https://poweron.loe.lviv.ua/'>Сайт</a>"
                return text
    except Exception as e:
        logging.error(f"❌ Помилка парсингу Львова: {e}")
    return None


async def check_updates(bot: Bot):
    logging.info("🚀 Моніторинг змін (Київ, Дніпро, Львів) запущено")

    while True:
        try:
            async with httpx.AsyncClient() as client:

                # --- 1. КИЇВ (Картинка) ---
                try:
                    res_kyiv = await client.get(KYIV_IMAGE_URL)
                    if res_kyiv.status_code == 200:
                        new_hash = get_content_hash(res_kyiv.content)
                        if last_sent_hashes["kyiv"] != new_hash:
                            prefix = "🆕 <b>З'явились зміни у графіку: КИЇВ</b>" if last_sent_hashes[
                                "kyiv"] else "⚡️ <b>Графік відключень: КИЇВ</b>"
                            await bot.send_photo(
                                CHANNEL_ID,
                                photo=URLInputFile(KYIV_IMAGE_URL),
                                caption=prefix
                            )
                            last_sent_hashes["kyiv"] = new_hash
                            logging.info("✅ Київ оновлено")
                except Exception as e:
                    logging.error(f"Помилка Київ: {e}")

                # --- 2. ДНІПРО (Картинка) ---
                try:
                    res_dnipro = await client.get(DNIPRO_IMAGE_URL)
                    if res_dnipro.status_code == 200:
                        new_hash = get_content_hash(res_dnipro.content)
                        if last_sent_hashes["dnipro"] != new_hash:
                            prefix = "🆕 <b>З'явились зміни у графіку: ДНІПРО</b>" if last_sent_hashes[
                                "dnipro"] else "⚡️ <b>Графік відключень: ДНІПРО</b>"
                            await bot.send_photo(
                                CHANNEL_ID,
                                photo=URLInputFile(DNIPRO_IMAGE_URL),
                                caption=prefix
                            )
                            last_sent_hashes["dnipro"] = new_hash
                            logging.info("✅ Дніпро оновлено")
                except Exception as e:
                    logging.error(f"Помилка Дніпро: {e}")

                # --- 3. ЛЬВІВ (Текст) ---
                lviv_text = await get_lviv_text_schedule()
                if lviv_text:
                    new_hash = get_content_hash(lviv_text)
                    if last_sent_hashes["lviv"] != new_hash:
                        prefix = "🆕 <b>З'явились зміни у графіку:</b>\n" if last_sent_hashes["lviv"] else ""
                        await bot.send_message(CHANNEL_ID, prefix + lviv_text, disable_web_page_preview=True)
                        last_sent_hashes["lviv"] = new_hash
                        logging.info("✅ Львів оновлено")

        except Exception as e:
            logging.error(f"Критична помилка в циклі: {e}")

        # Перевірка кожні 15 хвилин (900 секунд)
        # GitHub оновлює файли не миттєво, тому 15 хв — оптимально.
        await asyncio.sleep(900)


def setup_scheduler(bot: Bot):
    asyncio.create_task(check_updates(bot))