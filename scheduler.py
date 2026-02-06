import asyncio
import logging
import datetime
import requests
from aiogram import Bot
from aiogram.types import URLInputFile
from config import CHANNEL_ID

# Посилання на зображення (Київ та Дніпро)
KYIV_IMAGE_URL = "https://raw.githubusercontent.com/Baskerville42/outage-data-ua/refs/heads/main/images/kyiv/gpv-all-today.png"
DNIPRO_IMAGE_URL = "https://raw.githubusercontent.com/Baskerville42/outage-data-ua/refs/heads/main/images/dnipro/gpv-all-today.png"


async def get_lviv_text_schedule():
    """Парсер для Львова (текстовий)"""
    url = "https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/data/Lvivoblenerho.json"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            today_ts = str(data.get('today', ''))
            day_data = data.get('data', {}).get(today_ts, {})
            if not day_data: return None

            text = f"📝 <b>ГРАФІК ЛЬВІВ</b>\n📅 {datetime.date.today().strftime('%d.%m.%Y')}\n\n"
            for group, hours in day_data.items():
                line = "".join(["⬛" if str(hours.get(str(h), '')).lower() == 'no' else "⬜" for h in range(1, 25)])
                text += f"<b>Гр {group}:</b>\n<code>{line}</code>\n"
            text += f"\n⬜-є світло | ⬛-немає\n🔗 <a href='https://poweron.loe.lviv.ua/'>Сайт</a>"
            return text
    except Exception as e:
        logging.error(f"❌ Помилка Львова: {e}")
    return None


async def check_updates(bot: Bot):
    logging.info("🚀 Планувальник (Львів, Київ, Дніпро) запущено")
    while True:
        try:
            # 1. ПЕРЕВІРКА ЛЬВОВА
            logging.info("🔍 Перевірка Львова...")
            lviv_text = await get_lviv_text_schedule()
            if lviv_text:
                await bot.send_message(CHANNEL_ID, lviv_text)
                logging.info("✅ Львів відправлено")

            # 2. ПЕРЕВІРКА КИЄВА (Картинка)
            logging.info("🔍 Перевірка Києва...")
            try:
                kyiv_photo = URLInputFile(KYIV_IMAGE_URL, filename="kyiv_schedule.png")
                await bot.send_photo(CHANNEL_ID, photo=kyiv_photo, caption="⚡️ <b>Графік відключень: КИЇВ</b>")
                logging.info("✅ Київ відправлено")
            except Exception as e:
                logging.error(f"❌ Помилка Києва: {e}")

            # 3. ПЕРЕВІРКА ДНІПРА (Картинка)
            logging.info("🔍 Перевірка Дніпра...")
            try:
                dnipro_photo = URLInputFile(DNIPRO_IMAGE_URL, filename="dnipro_schedule.png")
                await bot.send_photo(CHANNEL_ID, photo=dnipro_photo, caption="⚡️ <b>Графік відключень: ДНІПРО</b>")
                logging.info("✅ Дніпро відправлено")
            except Exception as e:
                logging.error(f"❌ Помилка Дніпра: {e}")

        except Exception as e:
            logging.error(f"❌ Критична помилка: {e}")

        logging.info("😴 Чекаємо 1 годину до наступної перевірки...")
        await asyncio.sleep(3600)  # Перевірка раз на годину, щоб не спамити


def setup_scheduler(bot: Bot):
    asyncio.create_task(check_updates(bot))