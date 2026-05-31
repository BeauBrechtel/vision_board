import sqlite3

DB_NAME = "foos_board.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birthday TEXT,
            hire_date TEXT,
            photo_filename TEXT,
            fun_fact_1 TEXT,
            fun_fact_2 TEXT,
            fun_fact_3 TEXT,
            active INTEGER DEFAULT 1,
            photo_scale REAL DEFAULT 1.0,
            photo_x INTEGER DEFAULT 0,
            photo_y INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT,
            image_filename TEXT,
            start_date TEXT,
            end_date TEXT,
            duration_seconds INTEGER DEFAULT 15,
            active INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            company_name TEXT DEFAULT 'Foosackly''s Vision Board',
            default_slide_duration INTEGER DEFAULT 15,
            new_hire_slide_duration INTEGER DEFAULT 20
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS backgrounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            background_key TEXT NOT NULL UNIQUE,
            image_filename TEXT,
            text_color TEXT DEFAULT '#ffffff'
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO settings (
            id,
            company_name,
            default_slide_duration,
            new_hire_slide_duration
        )
        VALUES (1, 'Foosackly''s Vision Board', 15, 20)
    """)

    background_keys = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
        "birthday", "fooversary", "new_hire_intro", "new_hire_detail", "announcement"
    ]

    for key in background_keys:
        cur.execute(
            """
            INSERT OR IGNORE INTO backgrounds (
                background_key,
                image_filename,
                text_color
            )
            VALUES (?, ?, ?)
            """,
            (key, None, "#ffffff")
        )

    conn.commit()
    conn.close()