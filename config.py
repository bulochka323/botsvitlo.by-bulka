BOT_TOKEN = "8190914200:AAEUbwWbgiQ4riyph-wpIP_8bhZYhDlvmAo"
CHANNEL_ID = -1001657753695    # ID каналу (наприклад "@your_channel")
# Видаляємо старі змінні SCHEDULE_URL та COMPANY_NAME
# Замість них вставляємо словник:
REGIONS_CONFIG = {
    "kyiv": {"name": "Київ", "url": "https://www.dtek-kem.com.ua/ua/shutdowns"},
    "kyiv_region": {"name": "Київська область", "url": "https://www.dtek-krem.com.ua/ua/shutdowns"},
    "dnipro": {"name": "Дніпро", "url": "https://www.dtek-dnem.com.ua/ua/shutdowns"},
    "dnipro_region": {"name": "Дніпропетровська область", "url": "https://www.dtek-dnem.com.ua/ua/shutdowns"},
    "odesa": {"name": "Одеса", "url": "https://www.dtek-oem.com.ua/ua/shutdowns"},
    "lviv": {"name": "Львів", "url": "https://poweron.loe.lviv.ua/"},
    "vinnytsia": {"name": "Вінниця", "url": "https://www.voe.com.ua/disconnection/detailed"}
} # Ось ця дужка була пропущена!


PUBLISH_TIME = "23:30"          # Час ранкового поста
UPDATE_INTERVAL_MIN = 15        # Інтервал перевірок (хвилин)
DB_PATH = "outage_data.db"
RETRY_COUNT = 3
RETRY_DELAY = 10                # Затримка при помилці (сек)
LOG_LEVEL = "INFO"