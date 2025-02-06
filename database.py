import sqlite3, asyncio

def initialize_database(DB_PATH: str, table_name: str):
    """Creates the SQLite database and the necessary table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            screenshot_filename TEXT NOT NULL,
            subtitle_text TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

async def save_to_database(DB_PATH, screenshot_filename, subtitle_text, table_name):
    """Inserts data into the SQLite database asynchronously."""
    await asyncio.to_thread(_save_to_database, DB_PATH, screenshot_filename, subtitle_text, table_name)

def _save_to_database(DB_PATH, screenshot_filename, subtitle_text, table_name):
    """Performs the database insertion (runs in a separate thread)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {table_name} (screenshot_filename, subtitle_text)
        VALUES (?, ?)
    """, (screenshot_filename, subtitle_text))
    conn.commit()
    conn.close()

# Connect the screenshot and the caption

# Save data