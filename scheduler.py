import asyncio
import logging
import datetime
import requests
import time
from aiogram import Bot
from aiogram.types import URLInputFile
from config import CHANNEL_ID, REGIONS_CONFIG
from storage import get_schedule, save_schedule


async def get_lviv_text_schedule():
    """Парсер JSON для Львова: перетворює yes/no у квадратики"""
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
                line = ""
                for h in range(1, 25):
                    status = str(hours.get(str(h), '')).lower()
                    line += "⬛" if status == 'no' else "⬜"
                text += f"<b>Гр {group}:</b>\n<code>{line}</code>\n"

            text += f"\n⬜-є світло | ⬛-немає\n🔗 <a href='https://poweron.loe.lviv.ua/'>Сайт</a>"
            return text
    except Exception as e:
        logging.error(f"Помилка парсингу: {e}")
    return None


async def check_updates(bot: Bot):
    while True:
        today = datetime.date.today().isoformat()
        # Для Львова шлемо текст, якщо немає картинки
        if not get_schedule("lviv", today):
            text = await get_lviv_text_schedule()
            if text:
                await bot.send_message(CHANNEL_ID, text)
                save_schedule("lviv", today, "TEXT", "v1")
        await asyncio.sleep(600)  # Перевірка кожні 10 хв


def setup_scheduler(bot: Bot):
    asyncio.create_task(check_updates(bot))