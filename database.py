# database.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,      -- YYYY-MM-DD
            time_slot TEXT NOT NULL, -- e.g., "10:00-12:00"
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_reservation(user_id, name, phone, service, date, time_slot):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations (user_id, name, phone, service, date, time_slot)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, phone, service, date, time_slot))
    conn.commit()
    conn.close()

def get_user_reservations(user_id):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservations WHERE user_id = ?', (user_id,))
    reservations = cursor.fetchall()
    conn.close()
    return reservations
