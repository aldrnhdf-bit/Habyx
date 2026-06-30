import os
import shutil
import sqlite3
from datetime import datetime


def get_db():
    conn = sqlite3.connect("fitness.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Backup existing DB before applying schema changes.
    if os.path.exists("fitness.db"):
        bak_name = f"fitness.db.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            shutil.copy2("fitness.db", bak_name)
        except Exception:
            pass

    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        name TEXT, body_part TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS cardio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        activity TEXT, duration INTEGER, intensity TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        name TEXT, meal_type TEXT, calories INTEGER,
        protein REAL, carbs REAL, fat REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS hydration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        amount_ml INTEGER, time TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS hygiene (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        task TEXT, time_of_day TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS planned_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        task_name TEXT, task_type TEXT,
        day_of_week INTEGER, time TEXT,
        completed BOOLEAN DEFAULT 0, date_completed TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY,
        user_id INTEGER DEFAULT 1,
        level INTEGER DEFAULT 1,
        current_xp INTEGER DEFAULT 0,
        total_xp INTEGER DEFAULT 0,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        last_activity_date TEXT
    )""")

    cols = [r[1] for r in c.execute("PRAGMA table_info(user_stats)").fetchall()]
    if "user_id" not in cols:
        c.execute("ALTER TABLE user_stats ADD COLUMN user_id INTEGER DEFAULT 1")

    expected = {
        "user_stats": [
            ("user_id", "INTEGER DEFAULT 1"),
            ("level", "INTEGER DEFAULT 1"),
            ("current_xp", "INTEGER DEFAULT 0"),
            ("total_xp", "INTEGER DEFAULT 0"),
            ("current_streak", "INTEGER DEFAULT 0"),
            ("longest_streak", "INTEGER DEFAULT 0"),
            ("last_activity_date", "TEXT"),
        ],
        "workouts": [
            ("user_id", "INTEGER DEFAULT 1"),
            ("name", "TEXT"),
            ("body_part", "TEXT"),
        ],
        "cardio": [
            ("user_id", "INTEGER DEFAULT 1"),
            ("activity", "TEXT"),
            ("duration", "INTEGER"),
            ("intensity", "TEXT"),
        ],
        "meals": [
            ("user_id", "INTEGER DEFAULT 1"),
            ("name", "TEXT"),
            ("meal_type", "TEXT"),
            ("calories", "INTEGER"),
            ("protein", "REAL"),
            ("carbs", "REAL"),
            ("fat", "REAL"),
        ],
        "hydration": [
            ("user_id", "INTEGER DEFAULT 1"),
            ("amount_ml", "INTEGER"),
            ("time", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ],
        "hygiene": [
            ("user_id", "INTEGER DEFAULT 1"),
            ("task", "TEXT"),
            ("time_of_day", "TEXT"),
        ],
        "planned_tasks": [
            ("user_id", "INTEGER DEFAULT 1"),
            ("task_name", "TEXT"),
            ("task_type", "TEXT"),
            ("day_of_week", "INTEGER"),
            ("time", "TEXT"),
            ("completed", "BOOLEAN DEFAULT 0"),
            ("date_completed", "TEXT"),
        ],
    }

    for table, cols in expected.items():
        try:
            existing = [
                r[1] for r in c.execute(f"PRAGMA table_info({table})").fetchall()
            ]
        except Exception:
            existing = []
        for col_name, col_def in cols:
            if col_name not in existing:
                try:
                    c.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass

    c.execute("INSERT OR IGNORE INTO user_stats (id, user_id) VALUES (1, 1)")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database created successfully!")
