import sqlite3
from pathlib import Path

# Locate project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Define database location
DB_PATH = PROJECT_DIR / "data" / "politician_trades.db"

def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    # Create tables
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS politicians (
        politician_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        party TEXT,
        state TEXT,
        chamber TEXT
    );

    CREATE TABLE IF NOT EXISTS trades (
        trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        politician_id INTEGER NOT NULL,
        ticker TEXT,
        asset_description TEXT,
        transaction_type TEXT,
        transaction_date TEXT,
        disclosure_date TEXT,
        amount_low REAL,
        amount_high REAL,
        owner TEXT,
        source_url TEXT,

        FOREIGN KEY (politician_id)
            REFERENCES politicians(politician_id)
    );

    CREATE TABLE IF NOT EXISTS stock_prices (
        ticker TEXT NOT NULL,
        date TEXT NOT NULL,
        adjusted_close REAL,
        volume INTEGER,
        
        PRIMARY KEY (ticker, date)
    );

    """)

    conn.close()

    print("Database Created")
    print(f"Database location: {DB_PATH}")

if __name__ == "__main__":
    create_database()
