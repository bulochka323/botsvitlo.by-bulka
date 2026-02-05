import sqlite3
import logging

DB_NAME = "outage_data.db"

def init_db():
    """Створює таблицю, якщо її не існує"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            region TEXT,
            date TEXT,
            data TEXT,
            updated TEXT,
            PRIMARY KEY (region, date)
        )
    ''')
    conn.commit()
    conn.close()

def save_schedule(region, date, data, updated):
    init_db()  # Перевірка таблиці перед записом
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO schedules (region, date, data, updated)
        VALUES (?, ?, ?, ?)
    ''', (region, date, data, updated))
    conn.commit()
    conn.close()

def get_schedule(region, date):
    init_db()  # Перевірка таблиці перед читанням
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT data, updated FROM schedules WHERE date=? AND region=?', (date, region))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'data': row[0], 'updated': row[1]}
    return None