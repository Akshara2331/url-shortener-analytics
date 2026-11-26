import sqlite3

DB_PATH = "shortener.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referrer TEXT,
                user_agent TEXT,
                FOREIGN KEY (url_id) REFERENCES urls(id)
            );

            CREATE INDEX IF NOT EXISTS idx_urls_short_code ON urls(short_code);
            CREATE INDEX IF NOT EXISTS idx_clicks_url_id ON clicks(url_id);
            """
        )