import sqlite3

def init_db():
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    # 💪 WORKOUTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        body_part TEXT
    )
    """)

    # ❤️ CARDIO
    c.execute("""
    CREATE TABLE IF NOT EXISTS cardio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity TEXT,
        duration INTEGER,
        intensity TEXT
    )
    """)

    # 🥗 MEALS (NUTRITION)
    c.execute("""
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        meal_type TEXT,
        calories INTEGER,
        protein REAL,
        carbs REAL,
        fat REAL
    )
    """)

    # 💧 HYDRATION
    c.execute("""
    CREATE TABLE IF NOT EXISTS hydration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount_ml INTEGER,
        time TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 🧼 HYGIENE
    c.execute("""
    CREATE TABLE IF NOT EXISTS hygiene (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        time_of_day TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database created successfully!")

if __name__ == "__main__":
    init_db()