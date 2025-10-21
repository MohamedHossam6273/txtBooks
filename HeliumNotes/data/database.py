import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "heliumnotes.db")


def get_connection():
    """
    Returns a connection to the SQLite database.
    Creates the database file if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables dict-like access to results
    return conn


def init_db():
    """
    Initializes all database tables required by HeliumNotes.
    This function is called when the app starts for the first time.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Notes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT,
        tags TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # Plans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER,
        objectives TEXT,
        tasks TEXT,
        created_at TEXT,
        FOREIGN KEY(note_id) REFERENCES notes(id)
    )
    """)

    # Tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER,
        task TEXT,
        due_date TEXT,
        person TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY(note_id) REFERENCES notes(id)
    )
    """)

    # Patterns / recurring issues table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue TEXT,
        frequency INTEGER,
        last_detected TEXT
    )
    """)

    # Relations table for the knowledge graph
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_id INTEGER,
        to_id INTEGER,
        relation_type TEXT
    )
    """)

    # Embeddings table for semantic search
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER,
        vector BLOB,
        FOREIGN KEY(note_id) REFERENCES notes(id)
    )
    """)

    # Reflections table (for weekly reflections)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reflections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_start TEXT,
        completed_tasks TEXT,
        ongoing_plans TEXT,
        issues TEXT,
        summary TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


if __name__ == "__main__":
    # For testing purposes
    print("Initializing HeliumNotes database...")
    init_db()