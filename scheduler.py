import asyncio
import logging
import datetime
import requests
import time
import urllib3
from aiogram import Bot
from aiogram.types import URLInputFile
from config import CHANNEL_ID, UPDATE_INTERVAL_MIN, REGIONS_CONFIG
from storage import get_schedule, save_schedule

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_best_url(region_id):
    cache_buster = f"?t={int(time.time())}"
    VARIANTS = {
        "kyiv": ["kyiv"], "kyiv_region": ["koem"],
        "dnipro": ["dnipro"], "odesa": ["odesa"], "lviv": ["lviv"]
    }
    folders = VARIANTS.get(region_id, [region_id])
    for folder in folders:
        url = f"https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/images/{folder}/gpv-all-today.png"
        try:
            if requests.head(url, timeout=5).status_code == 200:
                return url + cache_buster
        except:
            continue
    return None


async def get_json_text_schedule(region_id):
    """Парсер: дістає дані з data -> timestamp -> group"""
    url = "https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/data/Lvivoblenerho.json"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            full_data = res.json()
            inner_data = full_data.get('data', {})  #

            # Визначаємо ключ сьогоднішнього дня
            today_ts = str(full_data.get('today', ''))
            if today_ts not in inner_data:
                keys = sorted([k for k in inner_data.keys() if str(k).isdigit()])
                if not keys: return None
                today_ts = keys[0]

            day_schedule = inner_data.get(today_ts, {})
            text = f"📝 <b>ГРАФІК ЛЬВІВ</b>\n📅 {datetime.date.today().strftime('%d.%m.%Y')}\n\n"

            for group, hours in day_schedule.items():
                line = ""
                for h in range(1, 25):
                    status = str(hours.get(str(h), '?')).lower()
                    if status == 'yes':
                        line += "⬜"  #
                    elif status == 'no':
                        line += "⬛"  #
                    else:
                        line += "▫️"
                text += f"<b>{group}:</b>\n<code>{line}</code>\n"

            text += f"\n⬜-є світло | ⬛-немає\n🔗 <a href='{REGIONS_CONFIG[region_id]['url']}'>Сайт</a>"
            return text
    except Exception as e:
        logging.error(f"Помилка JSON: {e}")
    return None


async def check_power_updates(bot: Bot):
    while True:
        logging.info("🚀 Перевірка...")
        today = datetime.date.today().isoformat()
        for region_id, info in REGIONS_CONFIG.items():
            img_url = get_best_url(region_id)
            if img_url:
                try:
                    res = requests.head(img_url, timeout=10)
                    marker = res.headers.get('ETag') or today
                    if not get_schedule(region_id, today) or get_schedule(region_id, today)['updated'] != marker:
                        await bot.send_photo(CHANNEL_ID, URLInputFile(img_url),
                                             caption=f"📊 <b>{info['name']}</b>\n🔗 <a href='{info['url']}'>Сайт</a>")
                        save_schedule(region_id, today, "IMG", marker)
                except:
                    pass
            elif region_id == "lviv":
                if not get_schedule(region_id, today):
                    text = await get_json_text_schedule(region_id)
                    if text:
                        await bot.send_message(CHANNEL_ID, text, disable_web_page_preview=True)
                        save_schedule(region_id, today, "TEXT", "V2")
        await asyncio.sleep(UPDATE_INTERVAL_MIN * 60)