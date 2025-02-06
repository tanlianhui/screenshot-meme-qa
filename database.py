import sqlite3, asyncio

def initialize_database(DB_PATH: str):
    """Creates the SQLite database and the necessary table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

     # Table for storing video names with a unique ID
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_names (
            video_id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT UNIQUE NOT NULL
        )
    """)

    # Table for storing screenshots with subtitles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scene_caption_correspondence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            screenshot_filename TEXT NOT NULL,
            subtitle_text TEXT NOT NULL,
            FOREIGN KEY (video_id) REFERENCES video_names(video_id)
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
    cursor.execute(
        f"""INSERT INTO {table_name} (screenshot_filename, subtitle_text)
        VALUES (?, ?)
    """, (screenshot_filename, subtitle_text))
    conn.commit()
    conn.close()

def get_or_create_video_id(DB_PATH, video_name):
    """Inserts a video name into `video_names` and returns its `video_id`."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert video name if it doesn't exist
    cursor.execute("""
        INSERT INTO video_names (video_name) 
        VALUES (?)
        ON CONFLICT(video_name) DO NOTHING
    """, (video_name,))

    # Retrieve the video_id
    cursor.execute("SELECT video_id FROM video_names WHERE video_name = ?", (video_name,))
    video_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()
    return video_id

# Connect the screenshot and the caption

# Save data
