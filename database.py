import sqlite3, asyncio


def initialize_image_database():
    """Creates the SQLite database and the necessary table."""
    conn = sqlite3.connect("scene_caption_correspondence.db")
    cursor = conn.cursor()

    # Create 'videos' table for storing video names with a unique ID
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            video_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL
        );
        """
    )

    # Create 'images' table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            caption TEXT,
            video_id INTEGER,
            FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    conn.close()

# Function to get or insert a video and return its video_id
def get_or_insert_video_id(video_path: str) -> str:
    """Gets or inserts a video and return its video_id."""
    conn = sqlite3.connect("scene_caption_correspondence.db")
    cursor = conn.cursor()

    cursor.execute("SELECT video_id FROM videos WHERE file_path = ?", (video_path,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]  # Return existing video_id
    else:
        cursor.execute("INSERT INTO videos (file_path) VALUES (?)", (video_path,))
        conn.commit()
        conn.close()
        return cursor.lastrowid  # Return new video_id


# Save data
def save_images_captions(image_data: list):
    """
    Batch save the image paths and captions.
    
    Args:
        image_data (list): List of tuples containing image paths, captions, and video IDs.
    """
    conn = sqlite3.connect("scene_caption_correspondence.db")
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO images (file_path, caption, video_id) VALUES (?, ?, ?)",
        image_data,
    )
    conn.commit()
    conn.close()
